"""
WorldGameEngine — Mission progress, XP preview, Lee-Wuh guidance.

Status: LOCAL_READY
Safety: No persistent ledger writes. Returns mission/reward preview only.
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

_MISSIONS = [
    {
        "mission_id": "mission_001",
        "title": "First Clip",
        "description": "Generate your first clip",
        "xp_reward": 100,
        "badge": "clip_starter",
        "completed": False,
    },
    {
        "mission_id": "mission_002",
        "title": "Hook Master",
        "description": "Generate 5 hooks in one session",
        "xp_reward": 250,
        "badge": "hook_master",
        "completed": False,
    },
    {
        "mission_id": "mission_003",
        "title": "Platform Pioneer",
        "description": "Export to 3 different platforms",
        "xp_reward": 500,
        "badge": "platform_pioneer",
        "completed": False,
    },
]

_LEE_WUH_GUIDANCE = [
    "Every great clip starts with a hook that stops the scroll.",
    "Consistency beats perfection — ship the clip.",
    "Your audience is waiting. The algorithm rewards action.",
    "One viral moment can change everything. Keep creating.",
]


class WorldGameEngine(LwaEngine):
    """
    Tracks mission progress, previews XP rewards, and surfaces Lee-Wuh guidance.
    Does NOT write to any persistent ledger or game state store.
    """

    @property
    def engine_id(self) -> str:
        return "world_game"

    @property
    def display_name(self) -> str:
        return "World & Game Engine"

    @property
    def description(self) -> str:
        return "Mission progress, XP preview, and Lee-Wuh guidance (no persistent ledger writes)."

    @property
    def status(self) -> EngineStatus:
        return EngineStatus.LOCAL_READY

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability(
                name="mission_progress",
                description="Preview mission progress and completion status",
                local_safe=True,
            ),
            EngineCapability(
                name="xp_preview",
                description="Preview XP rewards for actions",
                local_safe=True,
            ),
            EngineCapability(
                name="lee_wuh_guidance",
                description="Surface Lee-Wuh motivational guidance",
                local_safe=True,
            ),
            EngineCapability(
                name="ledger_write",
                description="Write XP and mission state to persistent ledger (requires DB)",
                local_safe=False,
                requires_provider=True,
            ),
        ]

    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        p = safe_payload(payload)
        creator_id = text_value(p, "creator_id", "demo-creator")
        current_xp = number_value(p, "current_xp", 0.0)
        action = text_value(p, "action", "clip_generated")

        xp_gain = 100 if action == "clip_generated" else 50
        new_xp_preview = current_xp + xp_gain
        level = int(new_xp_preview // 500) + 1
        guidance_index = int(current_xp) % len(_LEE_WUH_GUIDANCE)

        return EngineDemoResult(
            engine_id=self.engine_id,
            status=self.status,
            summary=f"Mission preview for creator '{creator_id}' — action '{action}' earns {xp_gain} XP",
            input_echo=p,
            output={
                "creator_id": creator_id,
                "action": action,
                "xp_gain_preview": xp_gain,
                "current_xp": current_xp,
                "new_xp_preview": new_xp_preview,
                "level_preview": level,
                "missions": _MISSIONS,
                "lee_wuh_guidance": _LEE_WUH_GUIDANCE[guidance_index],
                "ledger_write_blocked": True,
                "ledger_write_blocked_reason": "LOCAL_READY — no persistent game state store connected",
            },
            warnings=["XP and mission state are preview only — no ledger write occurred"],
            next_required_integrations=self.next_required_integrations(),
        )

    def next_required_integrations(self) -> list[str]:
        return [
            "Game state database (PostgreSQL for XP and mission persistence)",
            "Leaderboard service (real-time ranking)",
            "Badge/NFT minting (optional blockchain integration)",
        ]

    def health_warnings(self) -> list[str]:
        return []
