from __future__ import annotations

from typing import Any

from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    request_type = str(payload.get("request_type") or "clip_review")
    allowed = request_type not in {"payout", "crypto", "external_post"}
    return build_demo_result(
        summary="Safety engine blocks risky paths and explains why.",
        output={
            "request_type": request_type,
            "allowed": allowed,
            "blocked_reasons": [] if allowed else ["unsafe_request_type"],
            "claim_guard": "active",
        },
        warnings=["Safety checks remain local-safe and nonfatal."],
    )


ENGINE = BackendEngine(
    engine_id="safety",
    name="Safety Engine",
    status="backend_ready",
    capabilities_list=(
        capability("claim_guard", "Claim guard", "Block unsafe public claims and unsupported promises.", local_only=False),
        capability("rights_guard", "Rights guard", "Flag content that should not be used without proper rights."),
        capability("payout_guard", "Payout guard", "Prevent any money movement from the demo layer."),
    ),
    next_required_integrations_list=("policy review API", "campaign verification gates", "provider spend policy"),
    demo_summary="Safety engine blocks unsafe public claims and payout requests.",
    demo_runner=_demo,
)

engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
