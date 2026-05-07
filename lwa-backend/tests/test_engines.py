"""
Tests for the LWA backend engine foundation.

Verifies:
- All 10 engines are registered
- Each engine has a health snapshot
- Invalid engine IDs are handled correctly
- Every engine's demo_run() returns a valid EngineDemoResult
- No engine claims PRODUCTION_READY status by default
- Safety gates: wallet engine does not execute payouts
- Safety gates: social engine does not post externally
- Safety gates: render engine does not call paid providers
"""

from __future__ import annotations

import pytest

from app.engines import (
    EngineStatus,
    engine_ids,
    get_engine,
    get_engine_health,
    get_engine_registry,
    run_engine_demo,
)
from app.engines.base import EngineDemoResult, EngineHealth

# ---------------------------------------------------------------------------
# Expected engine IDs
# ---------------------------------------------------------------------------

EXPECTED_ENGINE_IDS = [
    "creator",
    "brain",
    "render",
    "marketplace",
    "wallet_entitlements",
    "proof_history",
    "world_game",
    "safety",
    "social_distribution",
    "operator_admin",
]


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------

def test_registry_returns_all_10_engines() -> None:
    """The registry must contain exactly 10 engines."""
    ids = engine_ids()
    assert len(ids) == 10, f"Expected 10 engines, got {len(ids)}: {ids}"
    for expected_id in EXPECTED_ENGINE_IDS:
        assert expected_id in ids, f"Missing engine: {expected_id}"


def test_get_engine_registry_returns_metadata_list() -> None:
    """get_engine_registry() returns a list of metadata dicts."""
    registry = get_engine_registry()
    assert isinstance(registry, list)
    assert len(registry) == 10
    for entry in registry:
        assert "engine_id" in entry
        assert "display_name" in entry
        assert "description" in entry
        assert "status" in entry
        assert "capabilities" in entry


def test_each_engine_has_health() -> None:
    """Every engine must return a valid EngineHealth snapshot."""
    health_list = get_engine_health()
    assert len(health_list) == 10
    for h in health_list:
        assert isinstance(h, EngineHealth)
        assert h.engine_id in EXPECTED_ENGINE_IDS
        assert isinstance(h.healthy, bool)
        assert isinstance(h.warnings, list)
        assert h.status in EngineStatus


def test_invalid_engine_id_returns_none_and_demo_raises() -> None:
    """get_engine() returns None for unknown IDs; run_engine_demo() raises KeyError."""
    assert get_engine("nonexistent_engine_xyz") is None

    with pytest.raises(KeyError):
        run_engine_demo("nonexistent_engine_xyz", {})


# ---------------------------------------------------------------------------
# Per-engine demo tests (parametrized)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("eid", EXPECTED_ENGINE_IDS)
def test_demo_run_works_for_each_engine(eid: str) -> None:
    """Every engine's demo_run() must return a valid EngineDemoResult."""
    result = run_engine_demo(eid, {"demo": True})

    assert isinstance(result, EngineDemoResult), f"{eid}: expected EngineDemoResult"
    assert result.engine_id == eid, f"{eid}: engine_id mismatch"
    assert isinstance(result.summary, str) and result.summary, f"{eid}: empty summary"
    assert isinstance(result.input_echo, dict), f"{eid}: input_echo must be dict"
    assert isinstance(result.output, dict), f"{eid}: output must be dict"
    assert isinstance(result.warnings, list), f"{eid}: warnings must be list"
    assert isinstance(result.next_required_integrations, list), f"{eid}: integrations must be list"
    assert result.status in EngineStatus, f"{eid}: invalid status"


@pytest.mark.parametrize("eid", EXPECTED_ENGINE_IDS)
def test_demo_run_accepts_empty_payload(eid: str) -> None:
    """Every engine must handle an empty payload without raising."""
    result = run_engine_demo(eid, {})
    assert isinstance(result, EngineDemoResult)


@pytest.mark.parametrize("eid", EXPECTED_ENGINE_IDS)
def test_demo_run_accepts_none_like_payload(eid: str) -> None:
    """Every engine must handle a non-dict payload gracefully (safe_payload coercion)."""
    engine = get_engine(eid)
    assert engine is not None
    # safe_payload coerces non-dicts to {}
    result = engine.demo_run(None)  # type: ignore[arg-type]
    assert isinstance(result, EngineDemoResult)


# ---------------------------------------------------------------------------
# Status / safety gate tests
# ---------------------------------------------------------------------------

def test_no_engine_claims_production_ready_by_default() -> None:
    """No engine should be PRODUCTION_READY in the initial foundation."""
    for eid in EXPECTED_ENGINE_IDS:
        engine = get_engine(eid)
        assert engine is not None
        assert engine.status != EngineStatus.PRODUCTION_READY, (
            f"Engine '{eid}' claims PRODUCTION_READY — this must be earned, not assumed"
        )


def test_wallet_engine_does_not_execute_payouts() -> None:
    """WalletEntitlementsEngine demo must block payment and payout execution."""
    result = run_engine_demo("wallet_entitlements", {"user_id": "test-user", "plan": "pro"})

    assert result.output.get("payment_blocked") is True, "payment_blocked must be True"
    assert result.output.get("payout_blocked") is True, "payout_blocked must be True"
    assert "SCAFFOLDED" in result.output.get("payment_blocked_reason", ""), (
        "payment_blocked_reason must mention SCAFFOLDED"
    )
    assert "SCAFFOLDED" in result.output.get("payout_blocked_reason", ""), (
        "payout_blocked_reason must mention SCAFFOLDED"
    )


def test_social_engine_does_not_post_externally() -> None:
    """SocialDistributionEngine demo must block all social posting."""
    result = run_engine_demo(
        "social_distribution",
        {"clip_id": "test-clip", "platforms": ["tiktok", "instagram_reels"]},
    )

    assert result.output.get("posting_blocked") is True, "posting_blocked must be True"
    assert "SCAFFOLDED" in result.output.get("posting_blocked_reason", ""), (
        "posting_blocked_reason must mention SCAFFOLDED"
    )
    # Each post package must also be blocked
    for pkg in result.output.get("post_packages", []):
        assert pkg.get("post_blocked") is True, (
            f"post_packages entry for {pkg.get('platform')} must have post_blocked=True"
        )


def test_render_engine_does_not_call_paid_providers() -> None:
    """RenderEngine demo must block render execution and not call paid providers."""
    result = run_engine_demo("render", {"clip_id": "test-clip", "platform": "tiktok"})

    render_plan = result.output.get("render_plan", {})
    assert render_plan.get("execution_blocked") is True, "execution_blocked must be True"
    assert "SCAFFOLDED" in render_plan.get("execution_blocked_reason", ""), (
        "execution_blocked_reason must mention SCAFFOLDED"
    )
    # Warnings must mention no render execution
    warning_text = " ".join(result.warnings).lower()
    assert "scaffolded" in warning_text, "Warnings must mention SCAFFOLDED status"


# ---------------------------------------------------------------------------
# Capability tests
# ---------------------------------------------------------------------------

def test_each_engine_has_at_least_one_capability() -> None:
    """Every engine must declare at least one capability."""
    for eid in EXPECTED_ENGINE_IDS:
        engine = get_engine(eid)
        assert engine is not None
        caps = engine.capabilities()
        assert len(caps) >= 1, f"Engine '{eid}' has no capabilities"


def test_payment_capabilities_are_not_local_safe() -> None:
    """Any capability that requires payment must not be marked local_safe."""
    for eid in EXPECTED_ENGINE_IDS:
        engine = get_engine(eid)
        assert engine is not None
        for cap in engine.capabilities():
            if cap.requires_payment:
                assert not cap.local_safe, (
                    f"Engine '{eid}' capability '{cap.name}' requires_payment=True "
                    f"but is also marked local_safe=True — this is a contradiction"
                )


def test_engine_metadata_is_serialisable() -> None:
    """Every engine's metadata() must return a JSON-serialisable dict."""
    import json

    for eid in EXPECTED_ENGINE_IDS:
        engine = get_engine(eid)
        assert engine is not None
        meta = engine.metadata()
        # Should not raise
        serialised = json.dumps(meta)
        assert len(serialised) > 0


# ---------------------------------------------------------------------------
# Creator engine specific
# ---------------------------------------------------------------------------

def test_creator_engine_returns_hooks_and_captions() -> None:
    """CreatorEngine demo must return hooks, captions, and scores."""
    result = run_engine_demo("creator", {"topic": "gaming", "platform": "tiktok"})

    assert "hooks" in result.output
    assert "captions" in result.output
    assert "scores" in result.output
    assert len(result.output["hooks"]) > 0
    assert result.output.get("export_ready") is True


# ---------------------------------------------------------------------------
# Brain engine specific
# ---------------------------------------------------------------------------

def test_brain_engine_returns_route_and_confidence() -> None:
    """BrainEngine demo must return a recommended route and confidence score."""
    result = run_engine_demo("brain", {"content_type": "video", "category": "gaming"})

    assert "recommended_route" in result.output
    assert "confidence" in result.output
    assert "reasoning" in result.output
    confidence = result.output["confidence"]
    assert 0.0 <= confidence <= 1.0, f"Confidence {confidence} out of range [0, 1]"


# ---------------------------------------------------------------------------
# Safety engine specific
# ---------------------------------------------------------------------------

def test_safety_engine_flags_risky_source() -> None:
    """SafetyEngine must flag a source containing a known risk pattern."""
    result = run_engine_demo(
        "safety",
        {"source_url": "https://piracy-site.example.com/stolen-video.mp4"},
    )

    assert result.output["overall_safe"] is False
    assert len(result.output["source_check"]["risk_flags"]) > 0


def test_safety_engine_passes_clean_source() -> None:
    """SafetyEngine must pass a clean source with no risk flags."""
    result = run_engine_demo(
        "safety",
        {"source_url": "https://cdn.example.com/my-original-video.mp4"},
    )

    assert result.output["overall_safe"] is True
    assert result.output["source_check"]["safe"] is True
    assert result.output["no_external_action_taken"] is True


# ---------------------------------------------------------------------------
# Operator admin specific
# ---------------------------------------------------------------------------

def test_operator_admin_reports_blockers() -> None:
    """OperatorAdminEngine must report unresolved launch gate blockers."""
    result = run_engine_demo("operator_admin", {"operator_id": "test-operator"})

    summary = result.output.get("system_summary", {})
    assert summary.get("total_gates", 0) > 0
    assert summary.get("failed_gates", 0) > 0, "Some gates should be unresolved"
    assert len(result.output.get("blockers", [])) > 0
    assert summary.get("launch_ready") is False
