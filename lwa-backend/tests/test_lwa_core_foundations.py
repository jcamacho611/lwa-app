from app.services.editing_core import build_edit_manifest
from app.services.semantic_cut_graph import semantic_overrides
from app.services.twitch_intelligence_core import rank_twitch_moments, score_twitch_moment


def test_build_edit_manifest_returns_nonfatal_segments() -> None:
    manifest = build_edit_manifest({"id": "source-1", "duration_seconds": 90})

    assert manifest["status"] == "ready"
    assert manifest["source_id"] == "source-1"
    assert manifest["segments"]
    assert manifest["segments"][0]["end_seconds"] > manifest["segments"][0]["start_seconds"]


def test_semantic_overrides_prefers_hook_language() -> None:
    overrides = semantic_overrides(
        [
            {"text": "welcome back to the show", "start": 0, "end": 10},
            {"text": "stop making this mistake with your content", "start": 10, "end": 25},
        ]
    )

    assert overrides[0]["score"] >= overrides[-1]["score"]
    assert overrides[0]["role"] in {"hook", "proof", "payoff"}


def test_twitch_score_uses_chat_and_viewer_signals() -> None:
    score = score_twitch_moment(
        {
            "title": "amazing clutch clip",
            "chat_messages": ["wow", "clip", "again"],
            "viewer_delta": 8,
        }
    )

    assert score.score > 40
    assert "chat-reacted" in score.tags


def test_rank_twitch_moments_orders_highest_first() -> None:
    ranked = rank_twitch_moments(
        [
            {"title": "quiet moment", "chat_messages": [], "viewer_delta": 0},
            {"title": "amazing clip", "chat_messages": ["wow", "clip"], "viewer_delta": 10},
        ]
    )

    assert ranked[0]["twitch_score"] >= ranked[1]["twitch_score"]
