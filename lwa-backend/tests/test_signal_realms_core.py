import unittest

from app.services.signal_realms_core import (
    RealmClass,
    RealmFaction,
    XpEvent,
    award_xp,
    create_badge,
    create_character,
    create_relic,
    level_for_xp,
    realms_safety_disclosure,
    total_xp_for_level,
    xp_to_next_level,
)


def test_xp_curve_starts_at_level_one() -> None:
    assert xp_to_next_level(1) == 100
    assert total_xp_for_level(1) == 0
    assert level_for_xp(0) == 1


def test_level_for_xp_advances_after_threshold() -> None:
    assert level_for_xp(100) >= 2
    assert level_for_xp(total_xp_for_level(10)) == 10


def test_create_character_and_award_xp() -> None:
    character = create_character("user-1", RealmClass.HOOKWRIGHT, RealmFaction.CRIMSON_COURT)
    updated = award_xp(
        character,
        XpEvent(character_id=character.id, skill="hookwright", amount=125, reason="first clip shipped"),
    )

    assert updated.total_xp == 125
    assert updated.realm_class == RealmClass.HOOKWRIGHT
    assert updated.faction == RealmFaction.CRIMSON_COURT


def test_award_xp_rejects_paid_or_invalid_amounts() -> None:
    character = create_character("user-1", RealmClass.CAPTIONEER, RealmFaction.BLACK_LOOM)

    with unittest.TestCase().assertRaises(ValueError):
        award_xp(character, XpEvent(character_id=character.id, skill="captioneer", amount=0, reason="invalid"))


def test_badges_are_soulbound_and_relics_cosmetic() -> None:
    badge = create_badge("First Clip", "First Clip", "Ship one clip.")
    relic = create_relic("Crimson Caption", "Crimson Caption", "Cosmetic caption relic.")

    assert badge.soulbound is True
    assert relic.cosmetic_only is True
    assert relic.tradeable is True


def test_realms_disclosure_blocks_investment_framing() -> None:
    disclosure = realms_safety_disclosure().lower()

    assert "xp cannot be bought" in disclosure
    assert "no item has investment value" in disclosure
