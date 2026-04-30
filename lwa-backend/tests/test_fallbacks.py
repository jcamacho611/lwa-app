from app.services.fallbacks import (
    build_fallback_clip_result,
    caption_fallback,
    hook_fallback,
    moment_fallback,
    transcript_fallback,
)


def test_transcript_fallback_splits_into_labeled_windows() -> None:
    segments = transcript_fallback(duration_seconds=75)
    assert [segment["text"] for segment in segments] == ["Segment 1", "Segment 2", "Segment 3"]
    assert segments[0]["start"] == 0
    assert segments[-1]["end"] == 75


def test_moment_fallback_picks_three_evenly_spaced_windows() -> None:
    moments = moment_fallback(duration_seconds=120)
    assert len(moments) == 3
    assert moments[0]["start"] == 0
    assert moments[-1]["end"] == 120


def test_caption_and_hook_fallbacks_are_deterministic() -> None:
    text = "This is the exact sentence that should become a hook"
    assert caption_fallback(text) == text
    assert hook_fallback(text) == "This is the exact sentence that should"


def test_build_fallback_clip_result_returns_degraded_clips() -> None:
    result = build_fallback_clip_result(reason="provider unavailable", duration_seconds=90)
    assert result.status == "degraded"
    assert result.fallback_used is True
    assert len(result.clips) == 3
    assert all(clip["status"] == "degraded" for clip in result.clips)
