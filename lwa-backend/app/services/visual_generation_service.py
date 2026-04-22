from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from ..core.config import Settings
from .generated_asset_store import GeneratedAssetStore
from .generation_providers.lwa_provider import LWAGenerationProvider


class VisualGenerationError(Exception):
    pass


class VisualGenerationDisabledError(VisualGenerationError):
    pass


@dataclass(frozen=True)
class VisualGenerationRequest:
    mode: str
    prompt: str | None = None
    image_url: str | None = None
    reference_image_url: str | None = None
    source_clip_url: str | None = None
    source_asset_id: str | None = None
    style_preset: str | None = None
    motion_profile: str | None = None
    duration_seconds: int = 8
    aspect_ratio: str = "9:16"
    seed: int | None = None
    target_platform: str | None = None


def visual_generation_available(settings: Settings) -> bool:
    return bool(getattr(settings, "visual_generation_enabled", True))


def validate_visual_generation_config(settings: Settings) -> None:
    if not visual_generation_available(settings):
        raise VisualGenerationDisabledError("Visual generation is disabled.")


def visual_generation_status(settings: Settings) -> dict[str, object]:
    available = visual_generation_available(settings)
    return {
        "enabled": available,
        "configured": available,
        "available": available,
        "provider": "lwa",
        "status": "ready" if available else "disabled",
        "core_clipping_dependency": False,
        "message": "LWA-owned visual generation is available." if available else "LWA-owned visual generation is disabled.",
    }


class VisualGenerationService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.provider = LWAGenerationProvider(settings)
        self.asset_store = GeneratedAssetStore(
            getattr(
                settings,
                "generated_asset_store_path",
                f"{settings.generated_assets_dir}/generated-assets.sqlite3",
            )
        )

    async def generate(self, request: VisualGenerationRequest, *, actor_id: str) -> dict[str, Any]:
        validate_visual_generation_config(self.settings)

        mode = request.mode.strip().lower()
        if mode not in {"image", "idea"}:
            raise VisualGenerationError("Visual generation supports 'image' and 'idea' only.")

        if mode == "idea" and not request.prompt:
            raise VisualGenerationError("Idea mode requires a prompt.")

        if mode == "image" and not (request.image_url or request.reference_image_url or request.prompt):
            raise VisualGenerationError("Image mode requires an image_url, reference_image_url, or prompt.")

        if mode == "idea":
            provider_response = await self.provider.generate_from_text(
                text_prompt=request.prompt or "",
                duration=float(request.duration_seconds),
                style=request.style_preset,
                aspect_ratio=request.aspect_ratio,
                motion_profile=request.motion_profile,
                seed=request.seed,
                target_platform=request.target_platform,
            )
        else:
            image_ref = request.image_url or request.reference_image_url or "lwa-image-input"
            provider_response = await self.provider.generate_from_image(
                image_path=image_ref,
                prompt=request.prompt,
                duration=float(request.duration_seconds),
                motion_strength=request.motion_profile or "medium",
                aspect_ratio=request.aspect_ratio,
                seed=request.seed,
                target_platform=request.target_platform,
            )

        clip = provider_response.clips[0] if provider_response.clips else None
        request_id = provider_response.request_id or f"vg_{uuid4().hex[:12]}"
        asset_id = str(provider_response.metadata.get("asset_id") or (clip.id if clip else "") or f"asset_{uuid4().hex[:12]}")

        source_refs: dict[str, str] = {}
        if request.image_url:
            source_refs["image_url"] = request.image_url
        if request.reference_image_url:
            source_refs["reference_image_url"] = request.reference_image_url
        if request.source_clip_url:
            source_refs["source_clip_url"] = request.source_clip_url
        if request.source_asset_id:
            source_refs["source_asset_id"] = request.source_asset_id
        if actor_id:
            source_refs["actor_id"] = actor_id

        record = self.asset_store.create_asset(
            asset_id=asset_id,
            provider=provider_response.provider,
            asset_type="generated_visual",
            status=str((clip.render_status if clip else None) or "pending"),
            prompt=request.prompt,
            preview_url=clip.preview_url if clip else None,
            video_url=(clip.clip_url or clip.raw_clip_url or clip.edited_clip_url) if clip else None,
            thumbnail_url=clip.thumbnail_url if clip else None,
            provider_job_id=str(provider_response.metadata.get("provider_job_id") or request_id),
            request_id=request_id,
            source_refs=source_refs,
            error=str(provider_response.metadata.get("error")) if provider_response.metadata.get("error") else None,
        )

        return {
            "request_id": request_id,
            "status": record["status"],
            "provider": "lwa",
            "mode": mode,
            "asset": {
                "id": record["id"],
                "provider": record["provider"],
                "asset_type": record["asset_type"],
                "status": record["status"],
                "prompt": record.get("prompt"),
                "preview_url": record.get("preview_url"),
                "video_url": record.get("video_url"),
                "thumbnail_url": record.get("thumbnail_url"),
                "source_refs": record.get("source_refs") or {},
                "created_at": record.get("created_at"),
                "error": record.get("error"),
            },
            "feature_flags": {
                "first_use_no_signup": True,
                "premium_generation": True,
            },
            "actor_id": actor_id,
        }
