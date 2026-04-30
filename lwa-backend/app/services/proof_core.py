from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any

# LWA PROOF FOUNDATION
# OFF-CHAIN ONLY
# PROVENANCE ONLY
# NO TOKENOMICS
# NO INVESTMENT LANGUAGE
# NO FEATURE UNLOCKS


@dataclass(frozen=True)
class ProofRecord:
    record_type: str
    subject_id: str
    owner_id: str
    issued_at: str
    evidence: dict[str, Any] = field(default_factory=dict)


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def hash_payload(payload: dict[str, Any]) -> str:
    return sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def proof_leaf(record: ProofRecord) -> str:
    return hash_payload(
        {
            "record_type": record.record_type,
            "subject_id": record.subject_id,
            "owner_id": record.owner_id,
            "issued_at": record.issued_at,
            "evidence": record.evidence,
        }
    )


def merkle_parent(left: str, right: str) -> str:
    ordered = sorted([left, right])
    return sha256((ordered[0] + ordered[1]).encode("utf-8")).hexdigest()


def merkle_root(leaves: list[str]) -> str | None:
    if not leaves:
        return None
    level = sorted(leaves)
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [merkle_parent(level[index], level[index + 1]) for index in range(0, len(level), 2)]
    return level[0]


def build_proof_snapshot(records: list[ProofRecord], day: str) -> dict[str, Any]:
    leaves = [proof_leaf(record) for record in records]
    return {
        "day": day,
        "root": merkle_root(leaves),
        "leaf_count": len(leaves),
        "leaves": leaves,
        "provenance_only": True,
        "disclosure": proof_disclosure(),
    }


def proof_disclosure() -> str:
    return "Proof records are provenance-only. They are not investments, payouts, tokens, or app-feature unlocks."
