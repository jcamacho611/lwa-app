from __future__ import annotations

from typing import Any

from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    return build_demo_result(
        summary="Operator admin engine surfaces a safe system snapshot and next actions.",
        output={
            "snapshot": {
                "engines": 10,
                "demo_mode": True,
                "alerts": len(payload.get("alerts") or []),
            },
            "recommended_action": "Review engine health and demo readiness",
        },
        warnings=["Operator admin actions are read-only in this local demo."],
    )


ENGINE = BackendEngine(
    engine_id="operator_admin",
    name="Operator Admin Engine",
    status="local_ready",
    capabilities_list=(
        capability("health_snapshot", "Health snapshot", "Summarize engine readiness for operators."),
        capability("feature_flag_preview", "Feature flag preview", "Preview safe feature toggles without mutating production data."),
        capability("demo_readiness", "Demo readiness", "Surface whether the product is safe to show."),
    ),
    next_required_integrations_list=("operator dashboard API", "feature flag store", "status telemetry"),
    demo_summary="Operator admin engine provides a read-only system snapshot.",
    demo_runner=_demo,
)

engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
