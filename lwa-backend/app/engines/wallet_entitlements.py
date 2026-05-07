"""
WalletEntitlementsEngine — Credit check, plan gate.

Status: SCAFFOLDED
Safety: No actual payment processing, no payouts, no crypto transactions.
        Returns entitlement check shape only.
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

_PLAN_LIMITS = {
    "free": {"clips_per_day": 5, "render_credits": 0, "marketplace_access": False},
    "creator": {"clips_per_day": 50, "render_credits": 100, "marketplace_access": True},
    "pro": {"clips_per_day": 500, "render_credits": 1000, "marketplace_access": True},
    "scale": {"clips_per_day": -1, "render_credits": -1, "marketplace_access": True},
}


class WalletEntitlementsEngine(LwaEngine):
    """
    Checks credit balances and enforces plan gates.
    Does NOT process payments, issue payouts, or touch crypto.
    """

    @property
    def engine_id(self) -> str:
        return "wallet_entitlements"

    @property
    def display_name(self) -> str:
        return "Wallet & Entitlements Engine"

    @property
    def description(self) -> str:
        return "Credit checking and plan gate enforcement (no payment execution)."

    @property
    def status(self) -> EngineStatus:
        return EngineStatus.SCAFFOLDED

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability(
                name="credit_check",
                description="Check available credits for a user",
                local_safe=True,
            ),
            EngineCapability(
                name="plan_gate",
                description="Enforce feature access based on subscription plan",
                local_safe=True,
            ),
            EngineCapability(
                name="payment_processing",
                description="Process payments and issue credits (requires payment provider)",
                local_safe=False,
                requires_provider=True,
                requires_payment=True,
            ),
            EngineCapability(
                name="payout_execution",
                description="Execute creator payouts (requires payment provider)",
                local_safe=False,
                requires_provider=True,
                requires_payment=True,
            ),
        ]

    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        p = safe_payload(payload)
        user_id = text_value(p, "user_id", "demo-user")
        plan = text_value(p, "plan", "free")
        requested_credits = number_value(p, "requested_credits", 1.0)

        plan_config = _PLAN_LIMITS.get(plan, _PLAN_LIMITS["free"])
        demo_balance = 10.0 if plan == "free" else 250.0
        has_credits = demo_balance >= requested_credits
        gate_passed = plan in ("creator", "pro", "scale")

        return EngineDemoResult(
            engine_id=self.engine_id,
            status=self.status,
            summary=f"Entitlement check for user '{user_id}' on plan '{plan}'",
            input_echo=p,
            output={
                "user_id": user_id,
                "plan": plan,
                "demo_balance": demo_balance,
                "requested_credits": requested_credits,
                "has_credits": has_credits,
                "gate_passed": gate_passed,
                "plan_limits": plan_config,
                "payment_blocked": True,
                "payment_blocked_reason": "SCAFFOLDED — no payment provider connected",
                "payout_blocked": True,
                "payout_blocked_reason": "SCAFFOLDED — no payout provider connected",
                "disclaimer": "Demo balance only. No real funds involved.",
            },
            warnings=[
                "SCAFFOLDED: demo balance only — no real wallet connected",
                "Payment processing disabled",
                "Payout execution disabled",
            ],
            next_required_integrations=self.next_required_integrations(),
        )

    def next_required_integrations(self) -> list[str]:
        return [
            "Payment provider (Stripe/Whop) for credit purchases",
            "Payout provider (Stripe Connect) for creator earnings",
            "User wallet store (persistent credit ledger)",
        ]

    def health_warnings(self) -> list[str]:
        return [
            "SCAFFOLDED: no payment provider connected",
            "All payment and payout operations are disabled",
        ]
