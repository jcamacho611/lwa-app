from app.services.caption_presets import list_caption_presets, normalize_caption_preset
from app.services.director_brain import director_brain_package
from app.services.hook_formula_library import get_hook_formula, list_hook_formulas


def test_hook_formula_library_contains_master_formulas() -> None:
    formulas = list_hook_formulas()
    assert len(formulas) == 20
    assert get_hook_formula("contrarian_claim") is not None
    assert get_hook_formula("dataset-pattern") is not None


def test_caption_preset_library_contains_expected_presets() -> None:
    preset_codes = {preset["code"] for preset in list_caption_presets()}
    assert "crimson_pulse" in preset_codes
    assert "clean_op" in preset_codes
    assert "karaoke_neon" in preset_codes
    assert "signal_low" in preset_codes
    assert "bigframe" in preset_codes
    assert "soft_safe" in preset_codes
    assert "dev_brutal" in preset_codes
    assert normalize_caption_preset("unknown") == "clean_op"


def test_director_brain_package_returns_structured_payload() -> None:
    package = director_brain_package(
        transcript="This clip explains how one source becomes multiple short form angles for creators.",
        target_platform="reels",
        caption_preset="crimson-pulse",
    )
    assert package["target_platform"] == "reels"
    assert package["caption_preset"] == "crimson_pulse"
    assert package["hooks"]
    assert package["captions"]
    assert package["moments"]
    assert package["score"] >= 55
    assert "Director Brain" in package["rationale"]
