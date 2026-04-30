from app.services.quality_gate import evaluate_quality_gate, quality_gate_dict


def test_quality_gate_passes_with_rendered_asset_and_valid_timing() -> None:
    result = evaluate_quality_gate(
        rendered_url="https://cdn.example.com/clip.mp4",
        start=0,
        end=30,
        duration_seconds=30,
    )

    assert result.quality_gate_status == "pass"
    assert result.render_readiness_score >= 75
    assert result.warnings == []
    assert result.strategy_only is False


def test_quality_gate_warns_for_strategy_only_package() -> None:
    result = evaluate_quality_gate(
        start=0,
        end=30,
        duration_seconds=30,
        strategy_only=True,
    )

    assert result.quality_gate_status == "warning"
    assert result.strategy_only is True
    assert "Strategy-only package" in result.warnings[0]


def test_quality_gate_fails_invalid_timestamps_without_asset() -> None:
    result = evaluate_quality_gate(start=30, end=30, duration_seconds=0)

    assert result.quality_gate_status == "fail"
    assert any("timestamps" in warning for warning in result.warnings)
    assert any("duration" in warning for warning in result.warnings)


def test_quality_gate_dict_returns_frontend_ready_fields() -> None:
    payload = quality_gate_dict(
        rendered_url="https://cdn.example.com/clip.mp4",
        start=0,
        end=15,
        duration_seconds=15,
    )

    assert payload["quality_gate_status"] == "pass"
    assert "render_readiness_score" in payload
    assert "warnings" in payload
    assert payload["strategy_only"] is False
