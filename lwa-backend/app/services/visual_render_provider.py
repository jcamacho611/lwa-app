from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from ..core.config import Settings

RENDER_PROVIDER_PUBLIC_ID = "lwa_visual_engine"
RENDERED_BY_PUBLIC_LABEL = "LWA Omega Visual Engine"

ProviderState = Literal["disabled", "missing-key", "failed", "ready"]


@dataclass(frozen=True)
class VisualRenderPayload:
    clip_id: str
    title: str
    hook: str
    caption: str
    shot_plan: list[dict[str, Any]] | list[Any] = field(default_factory=list)
    visual_engine_prompt: str | None = None
    motion_prompt: str | None = None
    duration_seconds: int | None = None
    aspect_ratio: str = "9:16"
    target_platform: str | None = None
    source_clip_url: str | None = None


@dataclass(frozen=True)
class VisualRenderProviderResult:
    provider_state: ProviderState
    render_provider: str = RENDER_PROVIDER_PUBLIC_ID
    rendered_by: str = RENDERED_BY_PUBLIC_LABEL
    attempted: bool = False
    success: bool = False
    asset_url: str | None = None
    preview_url: str | None = None
    download_url: str | None = None
    message: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_clip_update(self) -> dict[str, object]:
        return {
            "render_provider": self.render_provider,
            "rendered_by": self.rendered_by,
            "render_status": "ready" if self.success else "failed" if self.attempted else "pending",
            "preview_url": self.preview_url,
            "clip_url": self.asset_url,
            "download_url": self.download_url,
            "render_error": self.error,
        }


def resolve_visual_render_provider_state(settings: Settings) -> ProviderState:
    if not getattr(settings, "visual_engine_enabled", False):
        return "disabled"
    if not getattr(settings, "visual_engine_api_key", "").strip():
        return "missing-key"
    return "ready"


def visual_render_provider_status(
    settings: Settings,
    *,
    last_error: str | None = None,
) -> dict[str, object]:
    state = resolve_visual_render_provider_state(settings)
    if last_error:
        state = "failed"
    messages = {
        "disabled": "LWA Omega Visual Engine is disabled for this environment.",
        "missing-key": "LWA Omega Visual Engine is enabled but no visual engine key is configured.",
        "failed": "LWA Omega Visual Engine failed before a visual asset was produced.",
        "ready": "LWA Omega Visual Engine is configured for future provider wiring.",
    }
    return {
        "provider_state": state,
        "render_provider": RENDER_PROVIDER_PUBLIC_ID,
        "rendered_by": RENDERED_BY_PUBLIC_LABEL,
        "enabled": bool(getattr(settings, "visual_engine_enabled", False)),
        "configured": bool(getattr(settings, "visual_engine_api_key", "").strip()),
        "can_render": state == "ready",
        "message": messages[state],
        "last_error": last_error,
    }


async def render_visual_clip(
    *,
    settings: Settings,
    payload: VisualRenderPayload,
) -> VisualRenderProviderResult:
    state = resolve_visual_render_provider_state(settings)
    if state == "disabled":
        return VisualRenderProviderResult(
            provider_state="disabled",
            message="Visual rendering is turned off. Keep the clip strategy-only and preserve the shot plan.",
        )
    if state == "missing-key":
        return VisualRenderProviderResult(
            provider_state="missing-key",
            message="Visual rendering key is missing. Keep the strategy-only clip and surface a recover render action.",
        )

    try:
        response = await call_configured_visual_provider(payload=payload, settings=settings)
    except Exception as error:
        return VisualRenderProviderResult(
            provider_state="failed",
            attempted=True,
            message="Visual rendering is not wired yet. Preserve the director plan and return a recoverable strategy-only clip.",
            error="visual render provider not wired yet",
            metadata={
                "clip_id": payload.clip_id,
                "target_platform": payload.target_platform,
                "provider_exception": str(error),
            },
        )

    return VisualRenderProviderResult(
        provider_state="ready",
        attempted=True,
        success=bool(response.get("success")),
        asset_url=response.get("asset_url"),
        preview_url=response.get("preview_url"),
        download_url=response.get("download_url"),
        message=response.get("message"),
        error=response.get("error"),
        metadata=response.get("metadata") or {},
    )


async def call_configured_visual_provider(
    *,
    payload: VisualRenderPayload,
    settings: Settings,
) -> dict[str, Any]:
    raise NotImplementedError(
        "TODO: wire the configured visual vendor inside visual_render_provider.call_configured_visual_provider "
        "without exposing third-party provider names through the LWA app contract."
    )
