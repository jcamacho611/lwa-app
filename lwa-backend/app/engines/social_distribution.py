"""
SocialDistributionEngine — Post package, schedule plan.

Status: SCAFFOLDED
Safety: No actual social posting. Returns post package and schedule plan only.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any

from .base import (
    EngineCapability,
    EngineDemoResult,
    EngineStatus,
    LwaEngine,
    safe_payload,
    text_value,
)

_PLATFORM_SPECS = {
    "tiktok": {"max_duration": 60, "aspect_ratio": "9:16", "caption_limit": 2200},
    "instagram_reels": {"max_duration": 90, "aspect_ratio": "9:16", "caption_limit": 2200},
    "youtube_shorts": {"max_duration": 60, "aspect_ratio": "9:16", "caption_limit": 5000},
    "twitter": {"max_duration": 140, "aspect_ratio": "16:9", "caption_limit": 280},
    "linkedin": {"max_duration": 600, "aspect_ratio": "16:9", "caption_limit": 3000},
}


class SocialDistributionEngine(LwaEngine):
    """
    Packages posts and generates schedule plans for social distribution.
    Does NOT post to any social platform.
    """

    @property
    def engine_id(self) -> str:
        return "social_distribution"

    @property
    def display_name(self) -> str:
        return "Social Distribution Engine"

    @property
    def description(self) -> str:
        return "Post packaging and schedule planning for social distribution (no actual posting)."

    @property
    def status(self) -> EngineStatus:
        return EngineStatus.SCAFFOLDED

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability(
                name="post_package",
                description="Package a clip into a platform-ready post",
                local_safe=True,
            ),
            EngineCapability(
                name="schedule_plan",
                description="Generate an optimal posting schedule",
                local_safe=True,
            ),
            EngineCapability(
                name="social_post",
                description="Post content to social platforms (requires OAuth tokens)",
                local_safe=False,
                requires_provider=True,
            ),
        ]

    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        p = safe_payload(payload)
        clip_id = text_value(p, "clip_id", "demo-clip-001")
        caption = text_value(p, "caption", "Check out this amazing clip! #viral #content")
        platforms_raw = p.get("platforms", ["tiktok", "instagram_reels"])
        platforms = platforms_raw if isinstance(platforms_raw, list) else ["tiktok"]

        now = datetime.now(timezone.utc)
        post_packages = []
        schedule = []

        for i, platform in enumerate(platforms):
            spec = _PLATFORM_SPECS.get(platform, _PLATFORM_SPECS["tiktok"])
            truncated_caption = caption[: spec["caption_limit"]]
            post_packages.append(
                {
                    "platform": platform,
                    "clip_id": clip_id,
                    "caption": truncated_caption,
                    "aspect_ratio": spec["aspect_ratio"],
                    "max_duration": spec["max_duration"],
                    "hashtags": ["#viral", "#content", "#lwa"],
                    "post_blocked": True,
                    "post_blocked_reason": "SCAFFOLDED — no social OAuth tokens connected",
                }
            )
            schedule.append(
                {
                    "platform": platform,
                    "scheduled_at": (now + timedelta(hours=i * 2 + 1)).isoformat(),
                    "optimal_window": "18:00–21:00 local time",
                    "post_blocked": True,
                }
            )

        return EngineDemoResult(
            engine_id=self.engine_id,
            status=self.status,
            summary=f"Post package created for clip '{clip_id}' across {len(platforms)} platforms",
            input_echo=p,
            output={
                "clip_id": clip_id,
                "post_packages": post_packages,
                "schedule": schedule,
                "posting_blocked": True,
                "posting_blocked_reason": "SCAFFOLDED — no social OAuth tokens connected",
            },
            warnings=[
                "SCAFFOLDED: post package only — no actual social posting occurred",
                "Social OAuth tokens not connected",
            ],
            next_required_integrations=self.next_required_integrations(),
        )

    def next_required_integrations(self) -> list[str]:
        return [
            "TikTok OAuth (for TikTok posting)",
            "Instagram Graph API (for Reels posting)",
            "YouTube Data API (for Shorts posting)",
            "Scheduling queue (for deferred post dispatch)",
        ]

    def health_warnings(self) -> list[str]:
        return [
            "SCAFFOLDED: no social OAuth tokens connected",
            "All social posting is disabled",
        ]
