"""
ProofHistoryEngine — Proof record shape, audit summary.

Status: LOCAL_READY
Safety: No database writes. Returns proof record preview only.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from .base import (
    EngineCapability,
    EngineDemoResult,
    EngineStatus,
    LwaEngine,
    safe_payload,
    text_value,
)


def _deterministic_hash(value: str) -> str:
    """Produce a deterministic SHA-256 hex digest (first 16 chars)."""
    return hashlib.sha256(value.encode()).hexdigest()[:16]


class ProofHistoryEngine(LwaEngine):
    """
    Generates proof record shapes and audit summaries.
    Does NOT write to any database or ledger.
    """

    @property
    def engine_id(self) -> str:
        return "proof_history"

    @property
    def display_name(self) -> str:
        return "Proof History Engine"

    @property
    def description(self) -> str:
        return "Proof record shaping and audit summary generation (no database writes)."

    @property
    def status(self) -> EngineStatus:
        return EngineStatus.LOCAL_READY

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability(
                name="proof_record_shape",
                description="Generate the shape of a proof record for a clip or action",
                local_safe=True,
            ),
            EngineCapability(
                name="audit_summary",
                description="Summarise audit history for a creator or clip",
                local_safe=True,
            ),
            EngineCapability(
                name="proof_write",
                description="Write a proof record to the ledger (requires DB)",
                local_safe=False,
                requires_provider=True,
            ),
        ]

    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        p = safe_payload(payload)
        clip_id = text_value(p, "clip_id", "demo-clip-001")
        creator_id = text_value(p, "creator_id", "demo-creator")
        action = text_value(p, "action", "clip_generated")

        proof_hash = _deterministic_hash(f"{clip_id}:{creator_id}:{action}")
        timestamp = datetime.now(timezone.utc).isoformat()

        proof_record = {
            "proof_id": f"proof_{proof_hash}",
            "clip_id": clip_id,
            "creator_id": creator_id,
            "action": action,
            "timestamp": timestamp,
            "hash": proof_hash,
            "chain": "local_preview",
            "written": False,
            "write_blocked_reason": "LOCAL_READY — no database connected for writes",
        }

        audit_summary = {
            "creator_id": creator_id,
            "total_proofs": 0,
            "last_action": action,
            "last_timestamp": timestamp,
            "audit_status": "preview_only",
            "note": "No real audit data — demo preview only",
        }

        return EngineDemoResult(
            engine_id=self.engine_id,
            status=self.status,
            summary=f"Proof record preview for clip '{clip_id}' action '{action}'",
            input_echo=p,
            output={
                "proof_record": proof_record,
                "audit_summary": audit_summary,
            },
            warnings=["Proof record is a preview only — no database write occurred"],
            next_required_integrations=self.next_required_integrations(),
        )

    def next_required_integrations(self) -> list[str]:
        return [
            "Proof database (PostgreSQL or append-only ledger)",
            "Blockchain anchor (optional — for immutable proof)",
        ]

    def health_warnings(self) -> list[str]:
        return []
