from app.services.director_brain import director_brain_package


def test_director_brain_returns_platform_recommendation_fields() -> None:
    package = director_brain_package(
        transcript="Stop making this mistake before you post your next clip. Here are 3 reasons it hurts retention.",
        target_platform="youtube_shorts",
        category="business",
    )

    assert package["algorithm_version"].startswith("director-brain")
    assert package["recommended_platform"] == "youtube_shorts"
    assert package["recommended_content_type"] == "Business"
    assert package["recommended_output_style"]
    assert package["platform_recommendation_reason"]
    assert package["hook_formula_codes"]
    assert package["score"] >= 35


def test_director_brain_applies_risk_warning_without_crashing() -> None:
    package = director_brain_package(
        transcript="This is guaranteed passive income and a risk free investment.",
        target_platform="tiktok",
    )

    assert package["quality_gate_status"] == "warning"
    assert package["quality_gate_warnings"]
    assert package["risk_penalty"] > 0
    assert package["hooks"]


def test_director_brain_normalizes_platform_and_keeps_output_shape() -> None:
    package = director_brain_package(
        transcript="How to make a better clip with a stronger opening question?",
        target_platform="Instagram Reels",
        caption_preset="clean_op",
    )

    assert package["target_platform"] == "instagram_reels"
    assert package["caption_preset"] == "clean_op"
    assert isinstance(package["moments"], list)
    assert package["moments"][0]["hook_window_seconds"] == 2
