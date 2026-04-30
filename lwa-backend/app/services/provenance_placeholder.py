from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class ProvenanceRecord:
    kind: str
    subject_id: str
    code: str
    evidence_hash: str


def stable_hash(payload: str) -> str:
    return sha256(payload.encode("utf-8")).hexdigest()


def build_provenance_record(*, kind: str, subject_id: str, code: str, evidence: dict[str, Any] | None = None) -> ProvenanceRecord:
    evidence_items = evidence or {}
    evidence_text = "|".join(f"{key}={evidence_items[key]}" for key in sorted(evidence_items))
    return ProvenanceRecord(
        kind=kind,
        subject_id=subject_id,
        code=code,
        evidence_hash=stable_hash(f"{kind}|{subject_id}|{code}|{evidence_text}"),
    )


def build_daily_root(records: list[ProvenanceRecord]) -> str:
    if not records:
        return stable_hash("lwa-empty-day")
    leaf_hashes = sorted(record.evidence_hash for record in records)
    return stable_hash("|".join(leaf_hashes))


def provenance_snapshot(records: list[ProvenanceRecord]) -> dict[str, object]:
    return {
        "root": build_daily_root(records),
        "count": len(records),
        "records": [record.__dict__.copy() for record in records],
        "status": "off_chain_dry_run",
    }
