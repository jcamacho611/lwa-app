from __future__ import annotations

from typing import Any
from uuid import uuid4

from ...core.config import Settings
from .base_provider import BaseGenerationProvider


class LWAGenerationProvider(BaseGenerationProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate_from_text(
        self,
        *,
        prompt: str,
        style_preset: str | None = None,
        motion_profile: str | None = None,
        duration_seconds: int = 8,
        aspect_ratio: str = "9:16",
        seed: int | None = None,
        target_platform: str | None = None,
    ) -> dict[str, Any]:
        request_id = f"lwa_txt_{uuid4().hex[:12]}"
        asset_id = f"lwa_asset_{uuid4().hex[:12]}"

        return {
            "request_id": request_id,
            "asset_id": asset_id,
            "provider": "lwa",
            "asset_type": "generated_visual",
            "status": "ready",
            "preview_url": None,
            "video_url": None,
            "thumbnail_url": None,
            "provider_job_id": request_id,
            "error": None,
            "metadata": {
                "prompt": prompt,
                "style_preset": style_preset,
                "motion_profile": motion_profile,
                "duration_seconds": duration_seconds,
                "aspect_ratio": aspect_ratio,
                "seed": seed,
                "target_platform": target_platform,
            },
        }

    async def generate_from_image(
        self,
        *,
        image_url: str | None = None,
        reference_image_url: str | None = None,
        prompt: str | None = None,
        style_preset: str | None = None,
        motion_profile: str | None = None,
        duration_seconds: int = 8,
        aspect_ratio: str = "9:16",
        seed: int | None = None,
        target_platform: str | None = None,
    ) -> dict[str, Any]:
        request_id = f"lwa_img_{uuid4().hex[:12]}"
        asset_id = f"lwa_asset_{uuid4().hex[:12]}"

        return {
            "request_id": request_id,
            "asset_id": asset_id,
            "provider": "lwa",
            "asset_type": "generated_visual",
            "status": "ready",
            "preview_url": image_url or reference_image_url,
            "video_url": None,
            "thumbnail_url": image_url or reference_image_url,
            "provider_job_id": request_id,
            "error": None,
            "metadata": {
                "image_url": image_url,
                "reference_image_url": reference_image_url,
                "prompt": prompt,
                "style_preset": style_preset,
                "motion_profile": motion_profile,
                "duration_seconds": duration_seconds,
                "aspect_ratio": aspect_ratio,
                "seed": seed,
                "target_platform": target_platform,

        return {
            "request_id": request_id,
            "asset_id": asset_id,
            "provider": "lwa",
            "asset_type": "generated_visual",
            "status": "ready",
            "preview_url": None,
            "video_url": None,
            "thumbnail_url": None,
            "provider_job_id": request_id,
            "error": None,
            "metadata": {
                "prompt": prompt,
                "style_preset": style_preset,
                "motion_profile": motion_profile,
                "duration_seconds": duration_seconds,
                "aspect_ratio": aspect_ratio,
                "seed": seed,
                "target_platform": target_platform,
            },
        }
