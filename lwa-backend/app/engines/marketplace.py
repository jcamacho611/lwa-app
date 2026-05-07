from __future__ import annotations

from typing import Any

from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    return build_demo_result(
        summary="Marketplace engine surfaces teaser lanes without claims of real money flow.",
        output={
            "teaser_only": True,
            "marketplace_ready": False,
            "campaign_claims_enabled": False,
            "preview_offer": payload.get("preview_offer") or "Creator growth lane",
        },
        warnings=["Marketplace remains teaser-only until verification gates exist."],
    )


ENGINE = BackendEngine(
    engine_id="marketplace",
    name="Marketplace Engine",
    status="scaffolded",
    capabilities_list=(
        capability("teaser_lane", "Teaser lane", "Preview marketplace surfaces without claiming production commerce."),
        capability("eligibility_preview", "Eligibility preview", "Show what a future campaign match would need."),
    ),
    next_required_integrations_list=("verified campaign contracts", "marketplace entitlement rules", "payment review"),
    demo_summary="Marketplace engine exposes teaser-only opportunities.",
    demo_runner=_demo,
)

engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
