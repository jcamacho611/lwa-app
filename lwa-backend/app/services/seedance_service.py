from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

import httpx

from ..core.config import Settings
from ..models.schemas import SeedanceAssetResponse, SeedanceBackgroundRequest


class SeedanceProviderError(RuntimeError):
    """Controlled provider error that must not break core LWA clipping."""


class SeedanceDisabledError(SeedanceProviderError):
    """Seedance is intentionally off or missing required configuration."""


class SeedanceRequestError(SeedanceProviderError):
    """Seedance was enabled, but the provider request failed."""


def seedance_available(settings: Settings) -> bool:
    return bool(settings.seedance_enabled and settings.seedance_api_key and settings.seedance_base_url)


def validate_seedance_config(settings: Settings) -> None:
    if not settings.seedance_enabled:
        raise SeedanceDisabledError("Seedance is disabled. LWA core clipping and exports continue without it.")
    if not settings.seedance_api_key:
        raise SeedanceDisabledError("Seedance is enabled but SEEDANCE_API_KEY is missing.")
    if not settings.seedance_base_url:
        raise SeedanceDisabledError("Seedance is enabled but SEEDANCE_BASE_URL is missing.")


def build_seedance_payload(*, settings: Settings, request: SeedanceBackgroundRequest) -> dict[str, Any]:
    payload = {
        "model": settings.seedance_model,
        "prompt": request.prompt,
        "style_preset": request.style_preset,
        "motion_profile": request.motion_profile,
        "duration_seconds": request.duration_seconds,
        "aspect_ratio": request.aspect_ratio,
        "seed": request.seed,
        "reference_image_url": request.reference_image_url,
        "source_clip_url": request.source_clip_url,
        "source_asset_id": request.source_asset_id,
    }
    return {key: value for key, value in payload.items() if value is not None}


async def submit_seedance_job(
    *,
    settings: Settings,
    payload: dict[str, Any],
    job_id: str | None = None,
    job_kind: str = "background",
) -> dict[str, Any]:
    validate_seedance_config(settings)
    local_job_id = job_id or f"seed_{uuid4().hex[:12]}"
    state = _base_job_state(job_id=local_job_id, job_kind=job_kind, payload=payload)
    _save_seedance_job(settings=settings, job=state)

    try:
        async with httpx.AsyncClient(timeout=settings.seedance_timeout_seconds) as client:
            response = await client.post(_submit_url(settings), json=payload, headers=_headers(settings))
            response.raise_for_status()
            provider_payload = response.json()
    except httpx.HTTPStatusError as error:
        _mark_job_failed(settings=settings, job=state, error=f"Seedance submission failed: HTTP {error.response.status_code}")
        raise SeedanceRequestError(f"Seedance submission failed with HTTP {error.response.status_code}.") from error
    except Exception as error:
        _mark_job_failed(settings=settings, job=state, error=f"Seedance submission failed: {error}")
        raise SeedanceRequestError(f"Seedance submission failed: {error}") from error

    normalized = _normalize_seedance_job(
        settings=settings,
        local_job_id=local_job_id,
        job_kind=job_kind,
        payload=provider_payload,
    )
    _save_seedance_job(settings=settings, job=normalized)
    return normalized


async def poll_seedance_job(
    *,
    settings: Settings,
    job_id: str,
) -> dict[str, Any]:
    validate_seedance_config(settings)
    state = _load_seedance_job(settings=settings, job_id=job_id)
    if not state:
        raise SeedanceProviderError(f"Seedance job not found: {job_id}")

    provider_job_id = str(state.get("provider_job_id") or "").strip()
    if not provider_job_id:
        return state

    if str(state.get("status")) in {"completed", "failed", "cancelled"}:
        return state

    try:
        async with httpx.AsyncClient(timeout=settings.seedance_timeout_seconds) as client:
            response = await client.get(_poll_url(settings=settings, provider_job_id=provider_job_id), headers=_headers(settings))
            response.raise_for_status()
            provider_payload = response.json()
    except httpx.HTTPStatusError as error:
        _mark_job_failed(settings=settings, job=state, error=f"Seedance polling failed: HTTP {error.response.status_code}")
        raise SeedanceRequestError(f"Seedance polling failed with HTTP {error.response.status_code}.") from error
    except Exception as error:
        _mark_job_failed(settings=settings, job=state, error=f"Seedance polling failed: {error}")
        raise SeedanceRequestError(f"Seedance polling failed: {error}") from error

    normalized = _normalize_seedance_job(
        settings=settings,
        local_job_id=job_id,
        job_kind=str(state.get("job_kind") or "background"),
        payload=provider_payload,
        previous=state,
    )
    normalized = await _maybe_localize_asset(settings=settings, job=normalized)
    _save_seedance_job(settings=settings, job=normalized)
    return normalized


async def download_seedance_asset(
    *,
    settings: Settings,
    asset_url: str,
    destination_path: str,
) -> str:
    validate_seedance_config(settings)
    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        async with httpx.AsyncClient(timeout=settings.seedance_timeout_seconds) as client:
            response = await client.get(asset_url)
            response.raise_for_status()
            destination.write_bytes(response.content)
    except httpx.HTTPStatusError as error:
        raise SeedanceRequestError(f"Seedance asset download failed with HTTP {error.response.status_code}.") from error
    except Exception as error:
        raise SeedanceRequestError(f"Seedance asset download failed: {error}") from error
    return str(destination)


async def generate_seedance_background(
    *,
    settings: Settings,
    request: SeedanceBackgroundRequest,
) -> dict[str, Any]:
    return await submit_seedance_job(
        settings=settings,
        payload=build_seedance_payload(settings=settings, request=request),
        job_kind="background",
    )


async def enhance_clip_with_seedance(
    *,
    settings: Settings,
    request: SeedanceBackgroundRequest,
) -> dict[str, Any]:
    return await submit_seedance_job(
        settings=settings,
        payload=build_seedance_payload(settings=settings, request=request),
        job_kind="clip_enhancement",
    )


def normalize_seedance_asset(*, settings: Settings, payload: dict[str, Any], job_id: str) -> SeedanceAssetResponse:
    asset_url = _first_present(
        payload,
        "asset_url",
        "output_url",
        "video_url",
        "url",
        "download_url",
        nested=("asset", "url"),
    )
    thumbnail_url = _first_present(payload, "thumbnail_url", "poster_url", nested=("asset", "thumbnail_url"))
    return SeedanceAssetResponse(
        asset_id=str(_first_present(payload, "asset_id", "id", nested=("asset", "id")) or job_id),
        provider="seedance",
        status=_normalize_status(str(payload.get("status") or payload.get("state") or "")),
        asset_url=asset_url,
        thumbnail_url=thumbnail_url,
        public_url=asset_url,
        content_type=str(payload.get("content_type") or payload.get("mime_type") or "video/mp4"),
        duration_seconds=_optional_int(payload.get("duration") or payload.get("duration_seconds")),
        aspect_ratio=str(payload.get("aspect_ratio") or ""),
        metadata=_safe_metadata(payload),
    )


def _base_job_state(*, job_id: str, job_kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    now = _now()
    return {
        "job_id": job_id,
        "provider": "seedance",
        "provider_job_id": None,
        "job_kind": job_kind,
        "status": "submitting",
        "message": "Submitting Seedance job through LWA adapter.",
        "created_at": now,
        "updated_at": now,
        "asset": None,
        "error": None,
        "request_payload": payload,
    }


def _normalize_seedance_job(
    *,
    settings: Settings,
    local_job_id: str,
    job_kind: str,
    payload: dict[str, Any],
    previous: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = _now()
    provider_job_id = _first_present(payload, "job_id", "id", "task_id", "generation_id") or (previous or {}).get("provider_job_id")
    status = _normalize_status(str(payload.get("status") or payload.get("state") or "submitted"))
    asset = normalize_seedance_asset(settings=settings, payload=payload, job_id=local_job_id)
    asset_payload = asset.model_dump() if asset.asset_url or asset.thumbnail_url else None
    created_at = str((previous or {}).get("created_at") or payload.get("created_at") or now)
    return {
        "job_id": local_job_id,
        "provider": "seedance",
        "provider_job_id": str(provider_job_id) if provider_job_id else None,
        "job_kind": job_kind,
        "status": status,
        "message": str(payload.get("message") or _message_for_status(status)),
        "created_at": created_at,
        "updated_at": str(payload.get("updated_at") or now),
        "asset": asset_payload,
        "error": payload.get("error"),
        "request_payload": (previous or {}).get("request_payload"),
        "provider_payload": _safe_metadata(payload),
    }


async def _maybe_localize_asset(*, settings: Settings, job: dict[str, Any]) -> dict[str, Any]:
    if job.get("status") != "completed":
        return job

    asset = job.get("asset")
    if not isinstance(asset, dict):
        return job

    asset_url = str(asset.get("asset_url") or "")
    if not asset_url or asset.get("local_path"):
        return job

    try:
        extension = _asset_extension(asset_url=asset_url, content_type=str(asset.get("content_type") or "video/mp4"))
        relative_path = Path("seedance") / "assets" / f"{job['job_id']}{extension}"
        destination = Path(settings.generated_assets_dir) / relative_path
        local_path = await download_seedance_asset(settings=settings, asset_url=asset_url, destination_path=str(destination))
        public_url = _generated_public_url(settings=settings, relative_path=relative_path)
        asset.update(
            {
                "local_path": local_path,
                "public_url": public_url,
                "asset_url": public_url,
            }
        )
        job["asset"] = asset
    except Exception as error:
        asset.setdefault("metadata", {})
        if isinstance(asset["metadata"], dict):
            asset["metadata"]["localization_warning"] = str(error)
    return job


def _mark_job_failed(*, settings: Settings, job: dict[str, Any], error: str) -> None:
    job.update(
        {
            "status": "failed",
            "message": "Seedance job failed inside the adapter.",
            "error": error,
            "updated_at": _now(),
        }
    )
    _save_seedance_job(settings=settings, job=job)


def _jobs_dir(settings: Settings) -> Path:
    path = Path(settings.generated_assets_dir) / "seedance" / "jobs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _job_path(*, settings: Settings, job_id: str) -> Path:
    safe_id = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in job_id)
    return _jobs_dir(settings) / f"{safe_id}.json"


def _save_seedance_job(*, settings: Settings, job: dict[str, Any]) -> None:
    path = _job_path(settings=settings, job_id=str(job["job_id"]))
    path.write_text(json.dumps(job, indent=2, sort_keys=True), encoding="utf-8")


def _load_seedance_job(*, settings: Settings, job_id: str) -> dict[str, Any] | None:
    path = _job_path(settings=settings, job_id=job_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _submit_url(settings: Settings) -> str:
    return f"{settings.seedance_base_url.rstrip('/')}/jobs"


def _poll_url(*, settings: Settings, provider_job_id: str) -> str:
    return f"{settings.seedance_base_url.rstrip('/')}/jobs/{provider_job_id}"


def _headers(settings: Settings) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.seedance_api_key}",
        "Content-Type": "application/json",
    }


def _first_present(payload: dict[str, Any], *keys: str, nested: tuple[str, str] | None = None) -> Any:
    for key in keys:
        value = payload.get(key)
        if value:
            return value
    if nested:
        parent = payload.get(nested[0])
        if isinstance(parent, dict):
            return parent.get(nested[1])
    outputs = payload.get("outputs")
    if isinstance(outputs, list) and outputs:
        first = outputs[0]
        if isinstance(first, dict):
            for key in keys:
                value = first.get(key)
                if value:
                    return value
    return None


def _normalize_status(status: str) -> str:
    normalized = (status or "").strip().lower()
    if normalized in {"completed", "complete", "succeeded", "success", "ready", "done"}:
        return "completed"
    if normalized in {"failed", "error", "cancelled", "canceled"}:
        return "failed" if normalized != "cancelled" and normalized != "canceled" else "cancelled"
    if normalized in {"running", "processing", "rendering", "queued", "pending", "submitted", "submitting"}:
        return "processing" if normalized in {"running", "processing", "rendering"} else "submitted"
    return normalized or "submitted"


def _message_for_status(status: str) -> str:
    if status == "completed":
        return "Seedance asset is ready."
    if status == "failed":
        return "Seedance job failed."
    if status == "cancelled":
        return "Seedance job was cancelled."
    return "Seedance job accepted by adapter."


def _optional_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _asset_extension(*, asset_url: str, content_type: str) -> str:
    parsed = urlparse(asset_url)
    suffix = Path(parsed.path).suffix
    if suffix:
        return suffix
    if "png" in content_type:
        return ".png"
    if "jpeg" in content_type or "jpg" in content_type:
        return ".jpg"
    if "webp" in content_type:
        return ".webp"
    return ".mp4"


def _generated_public_url(*, settings: Settings, relative_path: Path) -> str:
    public_path = f"/generated/{relative_path.as_posix()}"
    if settings.api_base_url:
        return f"{settings.api_base_url.rstrip('/')}{public_path}"
    return public_path


def _safe_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(payload)
    for key in list(redacted.keys()):
        if "key" in key.lower() or "token" in key.lower() or "secret" in key.lower():
            redacted[key] = "[redacted]"
    return redacted


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
