from __future__ import annotations

from typing import Any

from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    proof_id = str(payload.get("proof_id") or "proof_demo_001")
    return build_demo_result(
        summary="Proof history engine records what was created and what was saved.",
        output={
            "proof_id": proof_id,
            "saved": True,
            "audit_trail_ready": True,
            "dispute_context_ready": True,
        },
        warnings=["This is a demo proof record; no legal or monetary claim is implied."],
    )


ENGINE = BackendEngine(
    engine_id="proof_history",
    name="Proof History Engine",
    status="backend_ready",
    capabilities_list=(
        capability("proof_log", "Proof log", "Record generation, export, and copy events.", local_only=False, requires_persistence=True),
        capability("audit_trail", "Audit trail", "Expose a durable sequence of proof events.", local_only=False, requires_persistence=True),
    ),
    next_required_integrations_list=("persistent event store", "proof query API", "user history views"),
    demo_summary="Proof history engine stores a demo proof record.",
    demo_runner=_demo,
)

engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
