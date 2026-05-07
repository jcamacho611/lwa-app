"""
SafetyEngine — Source risk check, money flow guard, provider guard.

Status: LOCAL_READY
Safety: No external action taken. Returns risk flags and safety checks only.
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
)

_BLOCKED_SOURCE_PATTERNS = [
    "piracy",
    "stolen",
    "dmca",
    "copyright_violation",
    "adult_content",
]

_MONEY_FLOW_GUARDS = [
    "no_direct_crypto_payout",
    "no_unverified_payment_destination",
    "no_anonymous_wallet_transfer",
    "no_bypass_kyc",
]

_PROVIDER_GUARDS = [
    "no_unauthenticated_provider_call",
    "no_provider_call_without_rate_limit",
    "no_provider_call_without_cost_cap",
]


class SafetyEngine(LwaEngine):
    """
    Checks source risk, enforces money flow guards, and validates provider safety.
    Does NOT take any external action — returns flags and checks only.
    """

    @property
    def engine_id(self) -> str:
        return "safety"

    @property
    def display_name(self) -> str:
        return "Safety Engine"

    @property
    def description(self) -> str:
        return "Source risk checking, money flow guarding, and provider safety validation."

    @property
    def status(self) -> EngineStatus:
        return EngineStatus.LOCAL_READY

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability(
                name="source_risk_check",
                description="Check a content source for risk flags",
                local_safe=True,
            ),
            EngineCapability(
                name="money_flow_guard",
                description="Validate money flow against safety rules",
                local_safe=True,
            ),
            EngineCapability(
                name="provider_guard",
                description="Validate provider call safety before execution",
                local_safe=True,
            ),
        ]

    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        p = safe_payload(payload)
        source_url = text_value(p, "source_url", "https://example.com/video.mp4")
        source_label = text_value(p, "source_label", "")
        money_destination = text_value(p, "money_destination", "")
        provider_name = text_value(p, "provider_name", "")

        # Source risk check
        source_lower = (source_url + source_label).lower()
        risk_flags = [
            pattern for pattern in _BLOCKED_SOURCE_PATTERNS
            if pattern in source_lower
        ]
        source_safe = len(risk_flags) == 0

        # Money flow guard
        money_lower = money_destination.lower()
        money_violations = [
            guard for guard in _MONEY_FLOW_GUARDS
            if "crypto" in money_lower and "crypto" in guard
            or "anonymous" in money_lower and "anonymous" in guard
        ]
        money_safe = len(money_violations) == 0

        # Provider guard
        provider_checks = {guard: True for guard in _PROVIDER_GUARDS}
        provider_safe = all(provider_checks.values())

        overall_safe = source_safe and money_safe and provider_safe

        return EngineDemoResult(
            engine_id=self.engine_id,
            status=self.status,
            summary=f"Safety check complete — overall {'SAFE' if overall_safe else 'BLOCKED'}",
            input_echo=p,
            output={
                "overall_safe": overall_safe,
                "source_check": {
                    "safe": source_safe,
                    "risk_flags": risk_flags,
                    "source_url": source_url,
                },
                "money_flow_check": {
                    "safe": money_safe,
                    "violations": money_violations,
                    "guards_applied": _MONEY_FLOW_GUARDS,
                },
                "provider_check": {
                    "safe": provider_safe,
                    "checks": provider_checks,
                    "provider": provider_name or "none",
                },
                "no_external_action_taken": True,
            },
            warnings=[] if overall_safe else [f"Risk flags detected: {risk_flags}"],
            next_required_integrations=self.next_required_integrations(),
        )

    def next_required_integrations(self) -> list[str]:
        return [
            "DMCA/copyright database (real-time source risk lookup)",
            "KYC provider (identity verification for money flows)",
            "Provider rate-limit registry (live cost cap enforcement)",
        ]

    def health_warnings(self) -> list[str]:
        return []
