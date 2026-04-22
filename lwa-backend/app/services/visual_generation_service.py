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
    """LWA visual generation is intentionally disabled."""


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
        if not self.settings.visual_generation_enabled:
            raise VisualGenerationDisabledError("LWA visual generation is disabled. Core clipping and exports continue without it.")

        mode = request.mode.strip().lower()
        if mode not in {"image", "idea"}:
            raise VisualGenerationError("Visual generation supports 'image' and 'idea' only.")

        if mode == "idea" and not request.prompt:
            raise VisualGenerationError("Idea mode requires a prompt.")

        if mode == "image" and not (request.image_url or request.reference_image_url or request.prompt):
            raise VisualGenerationError("Image mode requires an image_url, reference_image_url, or prompt.")

        if mode == "idea":
            provider_result = await self.provider.generate_from_text(
                prompt=request.prompt or "",
                style_preset=request.style_preset,
                motion_profile=request.motion_profile,
                duration_seconds=request.duration_seconds,
                aspect_ratio=request.aspect_ratio,
                seed=request.seed,
                target_platform=request.target_platform,
            )
        else:
            provider_result = await self.provider.generate_from_image(
                image_url=request.image_url,
                reference_image_url=request.reference_image_url,
                prompt=request.prompt,
                style_preset=request.style_preset,
                motion_profile=request.motion_profile,
                duration_seconds=request.duration_seconds,
                aspect_ratio=request.aspect_ratio,
                seed=request.seed,
                target_platform=request.target_platform,
            )

        request_id = provider_result.get("request_id") or f"vg_{uuid4().hex[:12]}"
        asset_id = provider_result.get("asset_id") or f"asset_{uuid4().hex[:12]}"

        source_refs: dict[str, str] = {}
        if request.image_url:
            source_refs["image_url"] = request.image_url
        if request.reference_image_url:
            source_refs["reference_image_url"] = request.reference_image_url
        if request.source_clip_url:
            source_refs["source_clip_url"] = request.source_clip_url
        if request.source_asset_id:
            source_refs["source_asset_id"] = request.source_asset_id

        record = self.asset_store.create_asset(
            asset_id=asset_id,
            provider="lwa",
            asset_type=provider_result.get("asset_type", "generated_visual"),
            status=provider_result.get("status", "ready"),
            prompt=request.prompt,
            preview_url=provider_result.get("preview_url"),
            video_url=provider_result.get("video_url"),
            thumbnail_url=provider_result.get("thumbnail_url"),
            provider_job_id=provider_result.get("provider_job_id"),
            request_id=request_id,
            source_refs=source_refs,
            error=provider_result.get("error"),
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
