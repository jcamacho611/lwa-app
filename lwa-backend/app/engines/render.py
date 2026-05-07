from __future__ import annotations

from typing import Any

from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    return build_demo_result(
        summary="Render engine preserves strategy-only fallback and local preview safety.",
        output={
            "render_requested": bool(payload.get("render_requested", False)),
            "rendered": False,
            "strategy_only": True,
            "paid_provider_called": False,
            "fallback_path": "local_preview",
        },
        warnings=["No paid rendering provider was called."],
    )


ENGINE = BackendEngine(
    engine_id="render",
    name="Render Engine",
    status="backend_ready",
    capabilities_list=(
        capability("render_preview", "Preview render", "Prepare a preview render path without external spend.", local_only=False),
        capability("strategy_fallback", "Strategy fallback", "Keep strategy-only output alive when render is unavailable."),
        capability("export_path", "Export path", "Describe how rendered clips become export bundles.", local_only=False),
    ),
    next_required_integrations_list=("render queue", "provider routing", "asset retention watchdog"),
    demo_summary="Render engine demonstrates the strategy-only fallback path.",
    demo_runner=_demo,
)

engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
