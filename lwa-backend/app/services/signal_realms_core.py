from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import uuid4

# LWA SIGNAL REALMS FOUNDATION
# NO BLOCKCHAIN IN THIS PHASE
# XP CANNOT BE BOUGHT
# BADGES ARE EARNED
# RELICS ARE COSMETIC ONLY
# NO INVESTMENT LANGUAGE


class RealmClass(StrEnum):
    HOOKWRIGHT = "hookwright"
    CAPTIONEER = "captioneer"
    REFRAMER = "reframer"
    TRENDSEER = "trendseer"
    LOREMASTER = "loremaster"
    VOICEWRIGHT = "voicewright"
    IRONFORGER = "ironforger"
    PRICER = "pricer"
    AUDITOR = "auditor"
    DIPLOMAT = "diplomat"
    CARTOGRAPHER = "cartographer"
    ORACLE = "oracle"


class RealmFaction(StrEnum):
    CRIMSON_COURT = "crimson_court"
    BLACK_LOOM = "black_loom"
    VERDANT_PACT = "verdant_pact"
    IRON_CHOIR = "iron_choir"
    SAFFRON_WAKE = "saffron_wake"
    GLASS_SYNOD = "glass_synod"
    TIDE_MARSHAL = "tide_marshal"
    DRIFTBORN = "driftborn"
    EMBERKIN = "emberkin"
    CHORUS_OF_THOTH = "chorus_of_thoth"
    HOUSE_POLIS = "house_polis"
    OUTER_SIGNAL = "outer_signal"


@dataclass(frozen=True)
class RealmCharacter:
    id: str
    user_id: str
    realm_class: RealmClass
    faction: RealmFaction
    total_xp: int = 0


@dataclass(frozen=True)
class XpEvent:
    character_id: str
    skill: str
    amount: int
    reason: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RealmBadge:
    code: str
    name: str
    description: str
    soulbound: bool = True


@dataclass(frozen=True)
class RealmRelic:
    code: str
    name: str
    description: str
    tradeable: bool = True
    cosmetic_only: bool = True


def xp_to_next_level(level: int) -> int:
    if level < 1:
        raise ValueError("level must be at least 1")
    return int(100 * (1.12 ** (level - 1)))


def total_xp_for_level(level: int) -> int:
    if level < 1:
        raise ValueError("level must be at least 1")
    return sum(xp_to_next_level(current) for current in range(1, level))


def level_for_xp(total_xp: int) -> int:
    if total_xp < 0:
        raise ValueError("total_xp cannot be negative")
    level = 1
    while level < 99 and total_xp >= total_xp_for_level(level + 1):
        level += 1
    return level


def create_character(user_id: str, realm_class: RealmClass, faction: RealmFaction) -> RealmCharacter:
    if not user_id.strip():
        raise ValueError("user_id is required")
    return RealmCharacter(id=str(uuid4()), user_id=user_id, realm_class=realm_class, faction=faction)


def award_xp(character: RealmCharacter, event: XpEvent) -> RealmCharacter:
    if event.amount <= 0:
        raise ValueError("XP amount must be positive")
    if event.character_id != character.id:
        raise ValueError("XP event character mismatch")
    return RealmCharacter(
        id=character.id,
        user_id=character.user_id,
        realm_class=character.realm_class,
        faction=character.faction,
        total_xp=character.total_xp + event.amount,
    )


def create_badge(code: str, name: str, description: str) -> RealmBadge:
    return RealmBadge(code=code.strip().lower().replace(" ", "_"), name=name.strip(), description=description.strip())


def create_relic(code: str, name: str, description: str) -> RealmRelic:
    return RealmRelic(code=code.strip().lower().replace(" ", "_"), name=name.strip(), description=description.strip())


def realms_safety_disclosure() -> str:
    return "Signal Realms items are progression and cosmetic only. XP cannot be bought and no item has investment value."
