"""
OperatorAdminEngine — System summary, launch gate.

Status: LOCAL_READY
Safety: No external mutations. Returns readiness summary and blockers only.
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

_LAUNCH_GATES = [
    {
        "gate": "engine_foundation",
        "description": "All 10 backend engines scaffolded",
        "passed": True,
    },
    {
        "gate": "route_coverage",
        "description": "Engine routes registered and tested",
        "passed": True,
    },
    {
        "gate": "payment_provider",
        "description": "Payment provider connected (Stripe/Whop)",
        "passed": False,
    },
    {
        "gate": "social_oauth",
        "description": "Social OAuth tokens configured",
        "passed": False,
    },
    {
        "gate": "render_provider",
        "description": "Render provider connected",
        "passed": False,
    },
    {
        "gate": "production_database",
        "description": "Production database connected and migrated",
        "passed": False,
    },
    {
        "gate": "monitoring",
        "description": "Error monitoring and alerting configured",
        "passed": False,
    },
]


class OperatorAdminEngine(LwaEngine):
    """
    Provides system readiness summaries and launch gate status for operators.
    Does NOT mutate any system state.
    """

    @property
    def engine_id(self) -> str:
        return "operator_admin"

    @property
    def display_name(self) -> str:
        return "Operator & Admin Engine"

    @property
    def description(self) -> str:
        return "System readiness summary and launch gate status for operators."

    @property
    def status(self) -> EngineStatus:
        return EngineStatus.LOCAL_READY

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability(
                name="system_summary",
                description="Summarise the current system readiness state",
                local_safe=True,
            ),
            EngineCapability(
                name="launch_gate",
                description="Check all launch gates and surface blockers",
                local_safe=True,
            ),
            EngineCapability(
                name="operator_action",
                description="Execute operator actions (requires admin auth)",
                local_safe=False,
                requires_provider=True,
            ),
        ]

    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        p = safe_payload(payload)
        operator_id = text_value(p, "operator_id", "demo-operator")

        passed_gates = [g for g in _LAUNCH_GATES if g["passed"]]
        failed_gates = [g for g in _LAUNCH_GATES if not g["passed"]]
        readiness_pct = round(len(passed_gates) / len(_LAUNCH_GATES) * 100, 1)

        blockers = [
            f"{g['gate']}: {g['description']}" for g in failed_gates
        ]

        system_summary = {
            "operator_id": operator_id,
            "total_gates": len(_LAUNCH_GATES),
            "passed_gates": len(passed_gates),
            "failed_gates": len(failed_gates),
            "readiness_percent": readiness_pct,
            "launch_ready": len(failed_gates) == 0,
            "blockers": blockers,
            "gates": _LAUNCH_GATES,
        }

        return EngineDemoResult(
            engine_id=self.engine_id,
            status=self.status,
            summary=f"System readiness: {readiness_pct}% — {len(failed_gates)} blockers remaining",
            input_echo=p,
            output={
                "system_summary": system_summary,
                "launch_ready": len(failed_gates) == 0,
                "blockers": blockers,
            },
            warnings=blockers if blockers else [],
            next_required_integrations=self.next_required_integrations(),
        )

    def next_required_integrations(self) -> list[str]:
        return [
            "Admin authentication (JWT with operator role)",
            "System metrics store (for live readiness data)",
            "Alerting integration (PagerDuty/Slack for operator notifications)",
        ]

    def health_warnings(self) -> list[str]:
        return []
