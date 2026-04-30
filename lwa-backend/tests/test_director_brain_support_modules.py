from app.services.campaign_engine import build_campaign_plan, infer_campaign_role
from app.services.caption_style_engine import recommend_caption_style
from app.services.creator_profile import build_creator_profile, profile_fit_notes
from app.services.fallback_engine import recovery_plan_dict
from app.services.hook_engine import build_hook_variants
from app.services.learning_loop import aggregate_learning_score, score_user_action
from app.services.offer_detector import detect_offer_fit
from app.services.platform_signals import get_platform_signal, platform_fit_score
from app.services.quality_gate import evaluate_quality_gate


def test_platform_signals_return_frontend_friendly_payload() -> None:
    signal = get_platform_signal("reels")
    assert signal.platform == "Instagram Reels"
    fit = platform_fit_score(platform="shorts", duration_seconds=45, has_captions=True)
    assert fit["score"] >= 80
    assert fit["recommended_length"]


def test_hook_engine_builds_variants() -> None:
    result = build_hook_variants(transcript="Stop making these 3 clipping mistakes before you post again.")
    assert result.primary_hook
    assert len(result.variants) == 3
    assert result.formula_code in {"specific_number", "numbered_list", "contrarian_claim"}


def test_caption_style_engine_recommends_safe_payload() -> None:
    result = recommend_caption_style(transcript="This method fixes the clip fast", category="podcast")
    assert result.caption_style == "signal_low"
    assert result.safe_area == "bottom_third"
    assert result.burned_in_ready is True


def test_offer_detector_scores_offer_fit() -> None:
    result = detect_offer_fit(
        transcript="This problem keeps creators stuck. Book a demo to see the system.",
        creator_type="agency",
        offer="demo",
    )
    assert result.offer_fit_score >= 60
    assert "problem" in result.signals
    assert "offer" in result.signals


def test_quality_gate_keeps_strategy_only_honest() -> None:
    result = evaluate_quality_gate(strategy_only=True, start=0, end=30, duration_seconds=30)
    assert result.strategy_only is True
    assert result.quality_gate_status in {"warning", "fail"}
    assert result.warnings


def test_fallback_engine_returns_recovery_options() -> None:
    result = recovery_plan_dict(reason="render unavailable", duration_seconds=90)
    assert result["output_type"] == "strategy_only"
    assert result["fallback_clip_count"] == 3
    assert result["recovery_options"]


def test_creator_profile_personalizes_notes() -> None:
    profile = build_creator_profile(creator_type="agency", offer="demo", banned_words=["forbidden"])
    notes = profile_fit_notes(profile=profile, transcript="This demo explains the system.")
    assert notes
    assert any("offer" in note.lower() or "value" in note.lower() for note in notes)


def test_campaign_engine_assigns_roles() -> None:
    role = infer_campaign_role(transcript="Here are the steps in our framework", index=0, platform="tiktok")
    assert role.campaign_role == "educational_clip"
    plan = build_campaign_plan(transcripts=["Book a call", "Before and after proof"], platform="reels")
    assert len(plan) == 2
    assert plan[0]["suggested_post_order"] == 1


def test_learning_loop_scores_user_actions() -> None:
    assert score_user_action("download_clip")["weight"] > 0
    aggregate = aggregate_learning_score(["play_clip", "download_clip", "reject_clip"])
    assert aggregate["signals"]
    assert "interpretation" in aggregate
