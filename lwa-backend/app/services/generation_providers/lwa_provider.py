from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from ...core.config import Settings
from ...models.schemas import ClipResult, GenerationResponse
from .base_provider import BaseGenerationProvider


class LWAGenerationProvider(BaseGenerationProvider):
    """LWA-owned visual generation provider.

    This is intentionally local and deterministic for now: it gives Image/Idea
    flows a normalized runtime contract without making clipping depend on any
    external visual provider.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = getattr(settings, "visual_generation_model", "lwa-visual-v1")

    async def generate_from_text(
        self,
        *,
        text_prompt: str,
        duration: Optional[float] = None,
        style: Optional[str] = None,
        aspect_ratio: str = "9:16",
        **kwargs: Any,
    ) -> GenerationResponse:
        request_id = f"lwa_txt_{uuid4().hex[:12]}"
        asset_id = f"lwa_asset_{uuid4().hex[:12]}"
        duration_seconds = int(duration or kwargs.get("duration_seconds") or 8)
        prompt = text_prompt.strip()

        return self._build_response(
            request_id=request_id,
            asset_id=asset_id,
            generation_type="idea_to_visual",
            title="Generated visual concept",
            hook=prompt[:120] or "Generated short-form concept",
            caption=prompt or "Generated short-form concept.",
            duration_seconds=duration_seconds,
            aspect_ratio=aspect_ratio,
            prompt=prompt,
            style=style,
            source_label="idea",
            thumbnail_url=None,
            preview_url=None,
            extra_metadata=kwargs,
        )

    async def generate_from_image(
        self,
        *,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
        duration: Optional[float] = None,
        motion_strength: str = "medium",
        **kwargs: Any,
    ) -> GenerationResponse:
        request_id = f"lwa_img_{uuid4().hex[:12]}"
        asset_id = f"lwa_asset_{uuid4().hex[:12]}"
        duration_seconds = int(duration or kwargs.get("duration_seconds") or 8)
        image_ref = str(image_path)
        prompt_text = (prompt or "Animate this image into a post-ready short-form asset.").strip()

        return self._build_response(
            request_id=request_id,
            asset_id=asset_id,
            generation_type="image_to_visual",
            title="Image generation concept",
            hook=prompt_text[:120],
            caption=prompt_text,
            duration_seconds=duration_seconds,
            aspect_ratio=str(kwargs.get("aspect_ratio") or "9:16"),
            prompt=prompt_text,
            style=kwargs.get("style") or kwargs.get("style_preset"),
            source_label=image_ref,
            thumbnail_url=image_ref,
            preview_url=image_ref,
            extra_metadata={
                **kwargs,
                "motion_strength": motion_strength,
                "source_image": image_ref,
            },
        )

    async def get_generation_status(self, *, generation_id: str) -> Dict[str, Any]:
        return {
            "generation_id": generation_id,
            "provider": "lwa",
            "status": "ready",
            "message": "LWA-owned visual generation record is available.",
        }

    async def cancel_generation(self, *, generation_id: str) -> bool:
        return False

    def _build_response(
        self,
        *,
        request_id: str,
        asset_id: str,
        generation_type: str,
        title: str,
        hook: str,
        caption: str,
        duration_seconds: int,
        aspect_ratio: str,
        prompt: str,
        style: str | None,
        source_label: str,
        thumbnail_url: str | None,
        preview_url: str | None,
        extra_metadata: dict[str, Any],
    ) -> GenerationResponse:
        playable_url = preview_url if preview_url and preview_url.startswith(("/", "http")) else None
        clip = ClipResult(
            id=asset_id,
            request_id=request_id,
            title=title,
            hook=hook or title,
            caption=caption or hook or title,
            start_time="0:00",
            end_time=self._format_seconds(duration_seconds),
            duration=duration_seconds,
            score=78 if playable_url else 70,
            confidence_score=78 if playable_url else 70,
            confidence_label="Strong early signal" if playable_url else "Worth testing",
            reason="LWA generated this asset from the provided creative input.",
            why_this_matters="This gives the creator a usable packaging direction without blocking the clipping flow.",
            category="Generated",
            format=f"{aspect_ratio} visual",
            aspect_ratio=aspect_ratio,
            preview_url=playable_url,
            clip_url=playable_url,
            thumbnail_url=thumbnail_url if thumbnail_url and thumbnail_url.startswith(("/", "http")) else None,
            preview_image_url=thumbnail_url if thumbnail_url and thumbnail_url.startswith(("/", "http")) else None,
            render_status="ready" if playable_url else "pending",
            is_rendered=bool(playable_url),
            is_strategy_only=not bool(playable_url),
            post_rank=1,
            platform_fit="TikTok, Reels, Shorts",
            packaging_angle=style or "Creator-native short-form asset",
        )

        return GenerationResponse(
            clips=[clip],
            request_id=request_id,
            generation_type=generation_type,
            provider="lwa",
            total_clips=1,
            processing_summary={
                "provider": "lwa",
                "model": self.model,
                "source": source_label,
                "status": clip.render_status,
            },
            metadata={
                "asset_id": asset_id,
                "provider_job_id": request_id,
                "prompt": prompt,
                "style": style,
                "runtime": "lwa-owned",
                **extra_metadata,
            },
        )

    @staticmethod
    def _format_seconds(seconds: int) -> str:
        mins = max(seconds, 0) // 60
        secs = max(seconds, 0) % 60
        return f"{mins}:{secs:02d}"
