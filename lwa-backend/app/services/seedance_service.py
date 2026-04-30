from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from ..core.config import Settings
from ..models.schemas import GenerationAssetResponse, GenerationBackgroundRequest


class SeedanceProviderError(RuntimeError):
    """Raised when the Seedance adapter cannot run safely."""


def seedance_available(settings: Settings) -> bool:
    return bool(settings.seedance_enabled and settings.seedance_api_key and settings.seedance_base_url)


def validate_seedance_config(settings: Settings) -> None:
    if not settings.seedance_enabled:
        raise SeedanceProviderError("Seedance is disabled. Set SEEDANCE_ENABLED=true to enable the premium visual adapter.")
    if not settings.seedance_api_key:
        raise SeedanceProviderError("Seedance is enabled but SEEDANCE_API_KEY is missing.")
    if not settings.seedance_base_url:
        raise SeedanceProviderError("Seedance is enabled but SEEDANCE_BASE_URL is missing.")


async def submit_seedance_job(*, settings: Settings, payload: dict[str, Any]) -> dict[str, Any]:
    validate_seedance_config(settings)
    raise SeedanceProviderError(
        "Seedance adapter is scaffolded, but the exact vendor job submission contract is not yet confirmed in this repo."
    )


async def poll_seedance_job(*, settings: Settings, job_id: str) -> dict[str, Any]:
    validate_seedance_config(settings)
    raise SeedanceProviderError(
        f"Seedance adapter is scaffolded, but the exact vendor job polling contract is not yet confirmed in this repo for job {job_id}."
    )


async def download_seedance_asset(*, settings: Settings, asset_url: str, destination_path: str) -> str:
    validate_seedance_config(settings)
    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=settings.seedance_timeout_seconds) as client:
        response = await client.get(asset_url)
        response.raise_for_status()
        destination.write_bytes(response.content)
    return str(destination)


async def generate_seedance_background(*, settings: Settings, request: GenerationBackgroundRequest) -> GenerationAssetResponse:
    await submit_seedance_job(settings=settings, payload=build_seedance_payload(settings=settings, request=request))
    raise SeedanceProviderError(
        "Seedance background generation is adapter-only until the exact vendor response contract is confirmed."
    )


def build_seedance_payload(*, settings: Settings, request: GenerationBackgroundRequest) -> dict[str, Any]:
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
