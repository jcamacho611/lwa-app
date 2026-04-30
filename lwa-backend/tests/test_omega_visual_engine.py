from app.models.schemas import ClipResult
from app.services.render_quality import evaluate_render_quality
from app.services.shot_planner import build_shot_plan_for_clip
from app.services.visual_render_provider import VisualRenderPayload, visual_render_provider_status
from app.core.config import Settings


def test_shot_planner_returns_required_roles() -> None:
    clip = ClipResult(
        id="clip-1",
        title="Stop making this mistake",
        hook="Stop making this mistake before you post again",
        caption="caption",
        score=88,
    )

    blueprint = build_shot_plan_for_clip(clip, target_platform="TikTok")
    roles = [step.role for step in blueprint.shot_plan]

    assert roles == ["hook", "context", "payoff", "loop_end"]
    assert blueprint.shot_plan_confidence >= 55
    assert blueprint.visual_engine_prompt
    assert blueprint.motion_prompt


def test_visual_provider_status_disabled(monkeypatch) -> None:
    monkeypatch.setenv("LWA_VISUAL_ENGINE_ENABLED", "false")
    settings = Settings()

    status = visual_render_provider_status(settings)

    assert status["provider_state"] == "disabled"
    assert status["can_render"] is False


def test_visual_provider_status_missing_key(monkeypatch) -> None:
    monkeypatch.setenv("LWA_VISUAL_ENGINE_ENABLED", "true")
    monkeypatch.delenv("LWA_VISUAL_ENGINE_API_KEY", raising=False)
    settings = Settings()

    status = visual_render_provider_status(settings)

    assert status["provider_state"] == "missing-key"
    assert status["can_render"] is False


def test_render_quality_strategy_only_when_no_media() -> None:
    clip = ClipResult(
        id="clip-2",
        title="Strategy clip",
        hook="This is the plan",
        caption="caption",
        score=70,
    )

    quality = evaluate_render_quality(clip=clip)

    assert quality.visual_engine_status == "strategy_only"
    assert quality.render_readiness_score < 60
    assert quality.strategy_only_reason


def test_visual_render_payload_is_stable() -> None:
    payload = VisualRenderPayload(
        clip_id="clip-3",
        title="title",
        hook="hook",
        caption="caption",
        shot_plan=[],
    )

    assert payload.aspect_ratio == "9:16"
    assert payload.clip_id == "clip-3"
