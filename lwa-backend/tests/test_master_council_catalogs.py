from app.services.provenance_placeholder import build_provenance_record, provenance_snapshot
from app.services.realms_catalog import (
    list_realm_classes,
    list_realm_factions,
    list_realm_quests,
    total_xp_for_level,
    xp_to_next,
)
from app.services.social_provider_catalog import get_social_provider_plan, list_social_provider_plans


def test_realms_catalog_contains_classes_factions_and_quests() -> None:
    assert len(list_realm_classes()) == 12
    assert len(list_realm_factions()) == 12
    assert len(list_realm_quests()) >= 30
    assert xp_to_next(1) == 100
    assert total_xp_for_level(2) == 100


def test_social_provider_catalog_contains_expected_plans() -> None:
    provider_codes = {provider["code"] for provider in list_social_provider_plans()}
    assert "youtube" in provider_codes
    assert "tiktok" in provider_codes
    assert "instagram" in provider_codes
    assert "twitch" in provider_codes
    assert "polymarket" in provider_codes
    assert get_social_provider_plan("youtube") is not None


def test_provenance_placeholder_builds_stable_snapshot() -> None:
    record = build_provenance_record(
        kind="badge",
        subject_id="character_123",
        code="first_signal",
        evidence={"clip_id": "clip_1"},
    )
    snapshot = provenance_snapshot([record])
    assert snapshot["status"] == "off_chain_dry_run"
    assert snapshot["count"] == 1
    assert snapshot["root"]
    assert snapshot["records"][0]["code"] == "first_signal"
