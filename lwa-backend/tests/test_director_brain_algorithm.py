from app.services.director_brain_algorithm import (
    AlgorithmInput,
    normalize_platform,
    score_clip_package,
    score_clip_package_dict,
)


def test_normalize_platform_aliases() -> None:
    assert normalize_platform("reels") == "instagram_reels"
    assert normalize_platform("shorts") == "youtube_shorts"
    assert normalize_platform("twitch") == "twitch_clips"


def test_score_clip_package_returns_component_breakdown() -> None:
    score = score_clip_package(
        AlgorithmInput(
            transcript="Stop making these 3 clipping mistakes. This framework turns one source into five strong short form angles.",
            target_platform="tiktok",
            category="education",
            source_type="video_upload",
            duration_seconds=45,
            caption_preset="crimson-pulse",
        )
    )
    assert score.overall >= 70
    assert score.components["hook_strength"] >= 70
    assert score.components["platform_fit"] >= 80
    assert score.selected_caption_preset == "crimson_pulse"
    assert score.safe_claim is True
    assert score.improvement_notes


def test_score_clip_package_flags_unsafe_claim_copy() -> None:
    score = score_clip_package(
        AlgorithmInput(
            transcript="This is guaranteed viral and guaranteed income for every creator.",
            target_platform="reels",
            source_type="prompt",
            duration_seconds=30,
        )
    )
    assert score.safe_claim is False
    assert score.components["safety"] < 90
    assert any("guarantee" in note.lower() for note in score.improvement_notes)


def test_score_clip_package_dict_is_ui_ready() -> None:
    payload = score_clip_package_dict(
        transcript="Here are five steps to turn a podcast into clips people understand quickly.",
        target_platform="linkedin",
        source_type="audio_upload",
        duration_seconds=80,
    )
    assert payload["overall"] >= 0
    assert payload["components"]
    assert payload["platform_goal"]
    assert payload["recommended_duration"]
    assert payload["rationale"]
