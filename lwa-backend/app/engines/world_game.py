from __future__ import annotations

from typing import Any

from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    return build_demo_result(
        summary="World game engine turns creator work into missions, XP, and realm progression.",
        output={
            "current_realm": payload.get("current_realm") or "signal_realm",
            "mission": "Signal Sprint",
            "xp_awarded": 50,
            "realm_unlocked": "proof_vault",
        },
        warnings=["Game progression is local-demo first; no anti-cheat or persistent profile yet."],
    )


ENGINE = BackendEngine(
    engine_id="world_game",
    name="World Game Engine",
    status="local_ready",
    capabilities_list=(
        capability("mission_flow", "Mission flow", "Move the user through creator missions and game states."),
        capability("realm_progression", "Realm progression", "Describe realm unlocks and current world context."),
        capability("reward_preview", "Reward preview", "Preview XP and relic rewards without claiming money."),
    ),
    next_required_integrations_list=("persistent player profile", "realm unlock API", "event history"),
    demo_summary="World game engine tracks the creator game loop locally.",
    demo_runner=_demo,
)

engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
