from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..core.config import Settings
from ..models.schemas import GenerationAssetResponse, GenerationBackgroundRequest


class VisualGenerationError(RuntimeError):
    """Controlled local visual generation runtime error."""


class VisualGenerationDisabledError(VisualGenerationError):
    """LWA visual generation is intentionally disabled."""


class VisualGenerationRequestError(VisualGenerationError):
    """LWA visual generation request could not be completed."""


def visual_generation_available(settings: Settings) -> bool:
    return bool(settings.visual_generation_enabled)


def validate_visual_generation_config(settings: Settings) -> None:
    if not settings.visual_generation_enabled:
        raise VisualGenerationDisabledError("LWA visual generation is disabled. Core clipping and exports continue without it.")


def build_visual_generation_payload(*, settings: Settings, request: GenerationBackgroundRequest) -> dict[str, Any]:
    payload = {
        "model": settings.visual_generation_model,
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


async def submit_visual_generation_job(
    *,
    settings: Settings,
    payload: dict[str, Any],
    job_id: str | None = None,
    job_kind: str = "background",
) -> dict[str, Any]:
    validate_visual_generation_config(settings)
    local_job_id = job_id or f"lwa_gen_{uuid4().hex[:12]}"
    now = _now()
    job = {
        "job_id": local_job_id,
        "provider": "lwa",
        "provider_job_id": local_job_id,
        "job_kind": job_kind,
        "status": "completed",
        "message": "LWA visual generation request normalized.",
        "created_at": now,
        "updated_at": now,
        "asset": _normalize_visual_asset(settings=settings, payload=payload, job_id=local_job_id).model_dump(),
        "error": None,
        "request_payload": payload,
        "provider_payload": {"runtime": "lwa-owned"},
    }
    _save_visual_generation_job(settings=settings, job=job)
    return job


async def poll_visual_generation_job(*, settings: Settings, job_id: str) -> dict[str, Any]:
    validate_visual_generation_config(settings)
    state = _load_visual_generation_job(settings=settings, job_id=job_id)
    if not state:
        raise VisualGenerationRequestError(f"LWA visual generation job not found: {job_id}")
    return state


async def download_visual_generation_asset(
    *,
    settings: Settings,
    asset_url: str,
    destination_path: str,
) -> str:
    validate_visual_generation_config(settings)
    if not asset_url:
        raise VisualGenerationRequestError("No asset URL available for download.")

    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = Path(asset_url.replace("/generated/", str(Path(settings.generated_assets_dir)) + "/", 1))
    if source.exists() and source.is_file():
        shutil.copyfile(source, destination)
        return str(destination)

    raise VisualGenerationRequestError("LWA visual generation asset is not local yet.")


async def generate_lwa_background(
    *,
    settings: Settings,
    request: GenerationBackgroundRequest,
) -> dict[str, Any]:
    return await submit_visual_generation_job(
        settings=settings,
        payload=build_visual_generation_payload(settings=settings, request=request),
        job_kind="background",
    )


async def enhance_clip_with_lwa_generation(
    *,
    settings: Settings,
    request: GenerationBackgroundRequest,
) -> dict[str, Any]:
    return await submit_visual_generation_job(
        settings=settings,
        payload=build_visual_generation_payload(settings=settings, request=request),
        job_kind="clip_enhancement",
    )


def _normalize_visual_asset(*, settings: Settings, payload: dict[str, Any], job_id: str) -> GenerationAssetResponse:
    return GenerationAssetResponse(
        asset_id=job_id,
        provider="lwa",
        status="completed",
        asset_url=None,
        thumbnail_url=None,
        public_url=None,
        local_path=None,
        content_type="application/json",
        duration_seconds=_optional_int(payload.get("duration_seconds")),
        aspect_ratio=str(payload.get("aspect_ratio") or "9:16"),
        metadata={
            "prompt": payload.get("prompt"),
            "model": settings.visual_generation_model,
            "runtime": "lwa-owned",
            "note": "Visual generation request normalized. Media synthesis can attach assets to this job when available.",
        },
    )


def _jobs_dir(settings: Settings) -> Path:
    path = Path(settings.generated_assets_dir) / "visual-generation" / "jobs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _job_path(*, settings: Settings, job_id: str) -> Path:
    safe_id = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in job_id)
    return _jobs_dir(settings) / f"{safe_id}.json"


def _save_visual_generation_job(*, settings: Settings, job: dict[str, Any]) -> None:
    path = _job_path(settings=settings, job_id=str(job["job_id"]))
    path.write_text(json.dumps(job, indent=2, sort_keys=True), encoding="utf-8")


def _load_visual_generation_job(*, settings: Settings, job_id: str) -> dict[str, Any] | None:
    path = _job_path(settings=settings, job_id=job_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _optional_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
