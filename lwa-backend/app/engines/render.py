"""
RenderEngine — Render plan, asset selection, queue handoff.

Status: SCAFFOLDED
Safety: No actual render execution. No paid provider calls.
        Returns a render plan only.
"""

from __future__ import annotations

from typing import Any

from .base import (
    EngineCapability,
    EngineDemoResult,
    EngineStatus,
    LwaEngine,
    safe_payload,
    text_value,
    number_value,
)


class RenderEngine(LwaEngine):
    """
    Produces a render plan and asset selection manifest.
    Does NOT execute any render or call a paid provider.
    """

    @property
    def engine_id(self) -> str:
        return "render"

    @property
    def display_name(self) -> str:
        return "Render Engine"

    @property
    def description(self) -> str:
        return "Render plan generation, asset selection, and queue handoff (no execution)."

    @property
    def status(self) -> EngineStatus:
        return EngineStatus.SCAFFOLDED

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability(
                name="render_plan",
                description="Generate a render plan for a clip",
                local_safe=True,
            ),
            EngineCapability(
                name="asset_selection",
                description="Select assets required for rendering",
                local_safe=True,
            ),
            EngineCapability(
                name="queue_handoff",
                description="Prepare a job for the render queue",
                local_safe=True,
                requires_provider=True,
            ),
        ]

    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        p = safe_payload(payload)
        clip_id = text_value(p, "clip_id", "demo-clip-001")
        platform = text_value(p, "platform", "tiktok")
        duration = number_value(p, "duration_seconds", 30.0)
        quality = text_value(p, "quality", "standard")

        render_plan = {
            "clip_id": clip_id,
            "platform": platform,
            "duration_seconds": duration,
            "quality": quality,
            "resolution": "1080x1920" if platform in ("tiktok", "instagram_reels") else "1920x1080",
            "fps": 30,
            "codec": "h264",
            "estimated_render_seconds": round(duration * 0.5, 1),
            "assets_required": [
                {"type": "source_video", "id": f"src_{clip_id}"},
                {"type": "caption_overlay", "id": f"cap_{clip_id}"},
                {"type": "thumbnail", "id": f"thumb_{clip_id}"},
            ],
            "queue_position": None,
            "execution_blocked": True,
            "execution_blocked_reason": "Engine is SCAFFOLDED — no render provider connected",
        }

        return EngineDemoResult(
            engine_id=self.engine_id,
            status=self.status,
            summary=f"Render plan created for clip '{clip_id}' on {platform} ({quality})",
            input_echo=p,
            output={"render_plan": render_plan},
            warnings=[
                "SCAFFOLDED: render plan only — no actual render executed",
                "Paid render provider not connected",
            ],
            next_required_integrations=self.next_required_integrations(),
        )

    def next_required_integrations(self) -> list[str]:
        return [
            "Render provider (Seedance, Runway, or local FFmpeg worker)",
            "Asset store (source video retrieval)",
            "Job queue (async render dispatch)",
        ]

    def health_warnings(self) -> list[str]:
        return [
            "SCAFFOLDED: no render provider connected",
            "Render execution is disabled until BACKEND_READY",
        ]
