"""Seedance provider adapter for premium visual generation.

This is an adapter-only integration. The exact Seedance HTTP API contract
has not been confirmed yet. All external HTTP calls are isolated here so
the rest of the codebase never touches Seedance specifics directly.

When SEEDANCE_ENABLED is false (the default) or env vars are missing,
every public function raises a controlled ``SeedanceUnavailableError``
or returns a safe disabled-state response. Normal clip generation is
never affected.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import httpx

from ..core.config import Settings

logger = logging.getLogger("uvicorn.error")


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class SeedanceUnavailableError(Exception):
    """Raised when Seedance is disabled or misconfigured."""


class SeedanceAPIError(Exception):
    """Raised when a Seedance API call returns an error."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Seedance API error {status_code}: {detail}")


# ---------------------------------------------------------------------------
# Data models (adapter-side; not Pydantic to avoid coupling with schemas.py)
# ---------------------------------------------------------------------------

@dataclass
class SeedanceJobRequest:
    prompt: str
    style_preset: str = "cinematic"
    motion_profile: str = "slow-drift"
    duration_seconds: int = 6
    aspect_ratio: str = "16:9"
    seed: Optional[int] = None
    reference_image_url: Optional[str] = None
    source_clip_url: Optional[str] = None
    source_asset_id: Optional[str] = None


@dataclass
class SeedanceJobStatus:
    job_id: str
    status: str  # "queued" | "processing" | "completed" | "failed"
    asset_url: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Availability check
# ---------------------------------------------------------------------------

def seedance_available(settings: Settings) -> bool:
    """True when Seedance is enabled and minimally configured."""
    if not settings.seedance_enabled:
        return False
    if not settings.seedance_api_key:
        return False
    if not settings.seedance_base_url:
        return False
    return True


def _require_seedance(settings: Settings) -> None:
    """Raise SeedanceUnavailableError with a clear message if not ready."""
    if not settings.seedance_enabled:
        raise SeedanceUnavailableError("Seedance is disabled (SEEDANCE_ENABLED=false)")
    if not settings.seedance_api_key:
        raise SeedanceUnavailableError("SEEDANCE_API_KEY is not configured")
    if not settings.seedance_base_url:
        raise SeedanceUnavailableError("SEEDANCE_BASE_URL is not configured")


# ---------------------------------------------------------------------------
# Adapter boundary — all Seedance HTTP specifics live below this line.
#
# NOTE: The exact API contract (auth headers, endpoints, request/response
# shapes) is pending vendor confirmation. The functions below define the
# adapter interface the rest of LWA will call. The HTTP implementation
# details will be filled in once the contract is confirmed.
# ---------------------------------------------------------------------------

async def submit_seedance_job(
    *,
    settings: Settings,
    request: SeedanceJobRequest,
) -> SeedanceJobStatus:
    """Submit a new visual generation job to Seedance.

    Returns a SeedanceJobStatus with status='queued' on success.
    Raises SeedanceUnavailableError if not configured.
    Raises SeedanceAPIError on upstream failures.

    # ADAPTER NOTE: exact endpoint, auth header, and body schema are
    # pending Seedance contract confirmation. The shape below is a
    # best-guess placeholder and will be updated.
    """
    _require_seedance(settings)

    base = settings.seedance_base_url.rstrip("/")
    url = f"{base}/v1/generate"

    body = {
        "model": settings.seedance_model,
        "prompt": request.prompt,
        "style_preset": request.style_preset,
        "motion_profile": request.motion_profile,
        "duration_seconds": request.duration_seconds,
        "aspect_ratio": request.aspect_ratio,
    }
    if request.seed is not None:
        body["seed"] = request.seed
    if request.reference_image_url:
        body["reference_image_url"] = request.reference_image_url
    if request.source_clip_url:
        body["source_clip_url"] = request.source_clip_url
    if request.source_asset_id:
        body["source_asset_id"] = request.source_asset_id

    headers = {
        "Content-Type": "application/json",
        # ADAPTER NOTE: auth header format pending contract confirmation
        "Authorization": f"Bearer {settings.seedance_api_key}",
    }

    logger.info("seedance_submit url=%s model=%s prompt_len=%s", url, settings.seedance_model, len(request.prompt))

    async with httpx.AsyncClient(timeout=float(settings.seedance_timeout_seconds)) as client:
        response = await client.post(url, json=body, headers=headers)

    if response.status_code >= 400:
        detail = _extract_error_detail(response)
        raise SeedanceAPIError(response.status_code, detail)

    data = response.json()
    return SeedanceJobStatus(
        job_id=str(data.get("job_id", data.get("id", ""))),
        status=str(data.get("status", "queued")),
        created_at=str(data.get("created_at", "")),
    )


async def poll_seedance_job(
    *,
    settings: Settings,
    job_id: str,
) -> SeedanceJobStatus:
    """Check the status of a Seedance generation job.

    # ADAPTER NOTE: exact polling endpoint pending contract confirmation.
    """
    _require_seedance(settings)

    base = settings.seedance_base_url.rstrip("/")
    url = f"{base}/v1/jobs/{quote(job_id)}"

    headers = {
        "Authorization": f"Bearer {settings.seedance_api_key}",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers)

    if response.status_code >= 400:
        detail = _extract_error_detail(response)
        raise SeedanceAPIError(response.status_code, detail)

    data = response.json()
    return SeedanceJobStatus(
        job_id=job_id,
        status=str(data.get("status", "unknown")),
        asset_url=data.get("asset_url") or data.get("output_url"),
        error=data.get("error"),
        updated_at=str(data.get("updated_at", "")),
    )


async def download_seedance_asset(
    *,
    settings: Settings,
    asset_url: str,
    output_dir: Path,
    filename: str,
) -> Path:
    """Download a completed Seedance asset to *output_dir* / *filename*.

    Returns the local Path to the saved file.
    """
    _require_seedance(settings)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    async with httpx.AsyncClient(timeout=float(settings.seedance_timeout_seconds)) as client:
        response = await client.get(asset_url)
        response.raise_for_status()

    output_path.write_bytes(response.content)
    logger.info("seedance_asset_downloaded path=%s bytes=%s", output_path, len(response.content))
    return output_path


async def generate_seedance_background(
    *,
    settings: Settings,
    prompt: str,
    style_preset: str = "mythic-void",
    duration_seconds: int = 8,
    aspect_ratio: str = "16:9",
) -> SeedanceJobStatus:
    """Convenience wrapper: submit a background generation job.

    Intended for homepage/hero premium backgrounds.
    """
    return await submit_seedance_job(
        settings=settings,
        request=SeedanceJobRequest(
            prompt=prompt,
            style_preset=style_preset,
            motion_profile="slow-drift",
            duration_seconds=duration_seconds,
            aspect_ratio=aspect_ratio,
        ),
    )


async def enhance_clip_with_seedance(
    *,
    settings: Settings,
    source_clip_url: str,
    prompt: str,
    style_preset: str = "cinematic",
    duration_seconds: int = 6,
) -> SeedanceJobStatus:
    """Convenience wrapper: submit a clip enhancement job.

    Intended for premium users who want Seedance-enhanced clip visuals.
    """
    return await submit_seedance_job(
        settings=settings,
        request=SeedanceJobRequest(
            prompt=prompt,
            style_preset=style_preset,
            motion_profile="match-source",
            duration_seconds=duration_seconds,
            source_clip_url=source_clip_url,
        ),
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_error_detail(response: httpx.Response) -> str:
    try:
        data = response.json()
        return str(data.get("error", data.get("detail", data.get("message", ""))))
    except Exception:
        return response.text[:100] if response.text else f"HTTP {response.status_code}"
