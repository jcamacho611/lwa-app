from app.services.proof_core import ProofRecord, build_proof_snapshot, merkle_root, proof_disclosure, proof_leaf


def test_proof_leaf_is_deterministic_for_same_record() -> None:
    record = ProofRecord(
        record_type="badge_award",
        subject_id="first_clip",
        owner_id="user-1",
        issued_at="2026-04-30",
        evidence={"clip_id": "clip-1"},
    )

    assert proof_leaf(record) == proof_leaf(record)


def test_merkle_root_is_stable_with_unsorted_leaves() -> None:
    leaves = ["b" * 64, "a" * 64, "c" * 64]

    assert merkle_root(leaves) == merkle_root(list(reversed(leaves)))


def test_build_proof_snapshot_is_provenance_only() -> None:
    snapshot = build_proof_snapshot(
        [
            ProofRecord(
                record_type="relic_holding",
                subject_id="crimson_caption",
                owner_id="user-1",
                issued_at="2026-04-30",
            )
        ],
        day="2026-04-30",
    )

    assert snapshot["leaf_count"] == 1
    assert snapshot["root"]
    assert snapshot["provenance_only"] is True


def test_proof_disclosure_blocks_investment_claims() -> None:
    disclosure = proof_disclosure().lower()

    assert "provenance-only" in disclosure
    assert "not investments" in disclosure
    assert "app-feature unlocks" in disclosure
