from __future__ import annotations

from typing import Any

from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    destination = str(payload.get("destination") or "manual_review")
    return build_demo_result(
        summary="Social distribution engine stays in local preview and does not post externally.",
        output={
            "destination": destination,
            "external_posted": False,
            "manual_review_required": True,
            "publish_allowed": False,
        },
        warnings=["No external social API call was made."],
    )


ENGINE = BackendEngine(
    engine_id="social_distribution",
    name="Social Distribution Engine",
    status="scaffolded",
    capabilities_list=(
        capability("destination_preview", "Destination preview", "Show a future posting destination without publishing."),
        capability("manual_review", "Manual review", "Keep social distribution behind a review gate."),
    ),
    next_required_integrations_list=("social provider catalog", "posting permissions", "scheduler review"),
    demo_summary="Social distribution engine never posts externally in demo mode.",
    demo_runner=_demo,
)

engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
