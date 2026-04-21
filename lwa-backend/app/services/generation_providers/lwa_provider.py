from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from .base_provider import BaseGenerationProvider
from ...core.config import Settings
from ...models.schemas import ClipResult, GenerationResponse

logger = logging.getLogger("uvicorn.error")


class LWAGenerationProvider(BaseGenerationProvider):
    """LWA-owned local provider for idea and image generation workflows."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = settings.visual_generation_model

    async def generate_from_text(
        self,
        *,
        text_prompt: str,
        duration: Optional[float] = 30.0,
        style: Optional[str] = None,
        aspect_ratio: str = "9:16",
        **kwargs: Any,
    ) -> GenerationResponse:
        prompt = text_prompt.strip()
        response = {
            "id": f"lwa_asset_{uuid4().hex[:12]}",
            "prompt": prompt,
            "title": prompt[:80] or "Generated concept",
            "caption": prompt,
            "duration": duration or 30.0,
            "style": style,
            "aspect_ratio": aspect_ratio,
            "source_mode": "idea",
        }
        return self._normalize_response(response, generation_type="idea_to_asset")

    async def generate_from_image(
        self,
        *,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
        duration: Optional[float] = 30.0,
        motion_strength: str = "medium",
        **kwargs: Any,
    ) -> GenerationResponse:
        image_file = Path(image_path)
        response = {
            "id": f"lwa_asset_{uuid4().hex[:12]}",
            "prompt": (prompt or "Animate this image into a short-form post-ready asset.").strip(),
            "title": image_file.stem or "Animated image concept",
            "caption": prompt or "Image-to-motion concept prepared for short-form packaging.",
            "duration": duration or 30.0,
            "motion_strength": motion_strength,
            "source_image": str(image_file),
            "source_mode": "image",
        }
        return self._normalize_response(response, generation_type="image_to_asset")

    async def get_generation_status(self, *, generation_id: str) -> Dict[str, Any]:
        return {
            "generation_id": generation_id,
            "provider": "lwa",
            "status": "completed",
            "message": "LWA generation request is normalized and ready for packaging.",
        }

    async def cancel_generation(self, *, generation_id: str) -> bool:
        logger.info("lwa_generation_cancel_noop generation_id=%s", generation_id)
        return False

    def _normalize_response(self, response: Dict[str, Any], *, generation_type: str) -> GenerationResponse:
        duration = float(response.get("duration") or response.get("duration_seconds") or 30.0)
        prompt = str(response.get("prompt") or response.get("title") or "Generated asset").strip()
        title = str(response.get("title") or prompt or "Generated asset").strip()
        caption = str(response.get("caption") or prompt).strip()
        asset_id = str(response.get("id") or f"lwa_asset_{uuid4().hex[:12]}")
        video_url = response.get("video_url") or response.get("asset_url")
        thumbnail_url = response.get("thumbnail_url")

        clip = ClipResult(
            id=asset_id,
            request_id=asset_id,
            title=title,
            hook=prompt[:140] or title,
            caption=caption,
            start_time="0:00",
            end_time=f"0:{int(duration):02d}" if duration < 60 else f"{int(duration // 60)}:{int(duration % 60):02d}",
            duration=int(duration),
            preview_url=video_url,
            clip_url=video_url,
            raw_clip_url=video_url,
            thumbnail_url=thumbnail_url,
            preview_image_url=thumbnail_url,
            render_status="ready" if video_url else "pending",
            is_rendered=bool(video_url),
            is_strategy_only=not bool(video_url),
            score=86 if video_url else 74,
            confidence_score=86 if video_url else 74,
            confidence_label="Strong early signal" if video_url else "Worth testing",
            confidence=1.0 if video_url else 0.74,
            reason="LWA generated this asset direction from your source input.",
            why_this_matters="This creates a reusable visual direction without requiring a long-form source.",
            category="Generated",
            format="9:16 generated",
            platform_fit="TikTok, Reels, Shorts",
            packaging_angle=response.get("style") or response.get("motion_strength") or "Generated concept",
        )

        return GenerationResponse(
            clips=[clip],
            request_id=asset_id,
            generation_type=generation_type,
            provider="lwa",
            total_clips=1,
            processing_summary={
                "total_candidates": 1,
                "processing_time": 0,
                "feature_flags": {},
                "target_platform": "TikTok",
                "recommended_platform": "TikTok",
                "credits_remaining": 999,
                "model": self.model,
            },
            metadata=response | {"provider_job_id": asset_id, "runtime": "lwa-owned"},
        )
