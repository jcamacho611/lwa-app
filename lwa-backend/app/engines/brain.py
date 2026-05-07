from __future__ import annotations

from typing import Any

from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    return build_demo_result(
        summary="Brain engine ranks signals and recommends the next best action.",
        output={
            "decision": "rank retention behavior before keywords",
            "recommended_action": payload.get("recommended_action") or "Focus on the strongest hook",
            "explanation": "The brain engine stays explainable and local-safe.",
        },
        warnings=["This is a deterministic backend preview; no AI provider call was made."],
    )


ENGINE = BackendEngine(
    engine_id="brain",
    name="Brain Engine",
    status="local_ready",
    capabilities_list=(
        capability("ranking", "Signal ranking", "Order clip opportunities by retention behavior."),
        capability("explanation", "Explainability", "Return a simple reason for the chosen path."),
        capability("mission_guidance", "Mission guidance", "Suggest the next user action from engine context."),
    ),
    next_required_integrations_list=("attention compiler", "persistent recommendation memory"),
    demo_summary="Brain engine provides an explainable next-best-action preview.",
    demo_runner=_demo,
)

engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
