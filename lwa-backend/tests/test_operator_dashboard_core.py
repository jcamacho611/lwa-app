from app.services.operator_dashboard_core import (
    build_attention_cards,
    operator_disclosure,
    summarize_operator_runs,
)


def test_operator_summary_counts_real_run_data() -> None:
    summary = summarize_operator_runs(
        [
            {
                "request_id": "run-1",
                "clips": [
                    {"id": "clip-1", "score": 90, "preview_url": "https://cdn.example.com/a.mp4"},
                    {"id": "clip-2", "score": 72, "strategy_only": True},
                ],
            }
        ]
    )

    assert summary.total_runs == 1
    assert summary.total_clips == 2
    assert summary.rendered_clips == 1
    assert summary.strategy_only_clips == 1
    assert summary.best_score == 90


def test_attention_cards_include_quality_and_recovery_items() -> None:
    cards = build_attention_cards(
        [
            {
                "request_id": "run-1",
                "clips": [
                    {"id": "clip-1", "title": "Needs review", "score": 81, "quality_gate_status": "warning"},
                    {"id": "clip-2", "title": "Ready", "score": 91, "preview_url": "https://cdn.example.com/a.mp4"},
                ],
            }
        ]
    )

    assert len(cards) == 1
    assert cards[0]["clip_id"] == "clip-1"
    assert cards[0]["reason"] == "quality gate warning"


def test_operator_disclosure_blocks_fake_external_metrics() -> None:
    disclosure = operator_disclosure().lower()

    assert "available lwa run data" in disclosure
    assert "verified integrations" in disclosure
