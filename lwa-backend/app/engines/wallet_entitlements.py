from __future__ import annotations

from typing import Any

from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    return build_demo_result(
        summary="Wallet and entitlements engine exposes credits and gates without payout execution.",
        output={
            "credits": int(payload.get("credits") or 120),
            "entitlements": ["demo_access", "local_rewards"],
            "payouts_executed": False,
            "payment_mutation": False,
        },
        warnings=["No payouts, crypto actions, or external payment execution occurred."],
    )


ENGINE = BackendEngine(
    engine_id="wallet_entitlements",
    name="Wallet Entitlements Engine",
    status="backend_ready",
    capabilities_list=(
        capability("credits", "Credits", "Track demo credits and usage gates.", local_only=False, requires_persistence=True),
        capability("entitlements", "Entitlements", "Resolve local access permissions for demo features.", local_only=False, requires_persistence=True),
        capability("payout_guard", "Payout guard", "Guarantee no payout execution occurs in the local engine."),
    ),
    next_required_integrations_list=("payment provider review", "whop entitlement verification", "ledger persistence"),
    demo_summary="Wallet entitlements engine tracks demo credits without moving money.",
    demo_runner=_demo,
)

engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
