from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RealmClass:
    code: str
    name: str
    specialty: str
    xp_source: str


@dataclass(frozen=True)
class RealmFaction:
    code: str
    name: str
    tagline: str
    aesthetic: str


REALM_CLASSES: tuple[RealmClass, ...] = (
    RealmClass("hookwright", "Hookwright", "Cold opens and attention capture", "first-3-second retention signals"),
    RealmClass("captioneer", "Captioneer", "Caption craft and on-screen text", "caption performance signals"),
    RealmClass("reframer", "Reframer", "9:16 framing and composition", "reframe quality signals"),
    RealmClass("trendseer", "Trendseer", "Trend timing and signal reading", "posts shipped near trend rise"),
    RealmClass("loremaster", "Loremaster", "Storytelling and narrative arcs", "watch duration signals"),
    RealmClass("voicewright", "Voicewright", "Voice, dubbing, and multilingual packaging", "multilingual reach signals"),
    RealmClass("ironforger", "Ironforger", "Pipelines and automation", "shared workflow signals"),
    RealmClass("pricer", "Pricer", "Marketplace pricing and conversion", "listing conversion signals"),
    RealmClass("auditor", "Auditor", "Trust, disputes, and moderation", "accepted review signals"),
    RealmClass("diplomat", "Diplomat", "Cross-platform amplification", "cross-posting signals"),
    RealmClass("cartographer", "Cartographer", "Niche mapping and audience research", "targeting accuracy signals"),
    RealmClass("oracle", "Oracle", "Trend and cultural signal reading", "signal accuracy signals"),
)

REALM_FACTIONS: tuple[RealmFaction, ...] = (
    RealmFaction("crimson_court", "Crimson Court", "Sell the moment", "crimson and ivory"),
    RealmFaction("black_loom", "Black Loom", "Quiet mastery", "onyx and threadwork"),
    RealmFaction("verdant_pact", "Verdant Pact", "Slow, evergreen, owned", "forest green and brass"),
    RealmFaction("iron_choir", "Iron Choir", "Automation, scale", "gunmetal and choral motifs"),
    RealmFaction("saffron_wake", "Saffron Wake", "Bright, viral, fast", "saffron and lightning"),
    RealmFaction("glass_synod", "Glass Synod", "Transparency and trust", "frosted glass and silver"),
    RealmFaction("tide_marshal", "Tide Marshal", "Cross-channel distribution", "cobalt and currents"),
    RealmFaction("driftborn", "Driftborn", "Indie, anti-algorithm", "bone and wind"),
    RealmFaction("emberkin", "Emberkin", "Reaction, debate, heat", "ember and ash"),
    RealmFaction("chorus_of_thoth", "Chorus of Thoth", "Education and memory", "lapis and cyan"),
    RealmFaction("house_polis", "House Polis", "Local and place-based", "terracotta and civic crest"),
    RealmFaction("outer_signal", "Outer Signal", "Trend frontier", "black and neon green"),
)

REALM_QUESTS: tuple[str, ...] = (
    "First Signal",
    "Voice of the Realm",
    "The Hook is Mightier",
    "Caption Cantata",
    "Frame Discipline",
    "Multitongue",
    "Cross the Veil",
    "The Patron's Mark",
    "The Glass Eye",
    "The Naming Ceremony",
    "List the First Stone",
    "Patron Found",
    "Honest Coin",
    "The Watermark Vow",
    "The Tally",
    "The Tenfold Patron",
    "The Auditor's Nod",
    "The Refund Returned",
    "The Bundle",
    "The Hundred",
    "The Director's Whisper",
    "Per-Platform Voice",
    "The Trend Reading",
    "The Polymarket Glance",
    "The Reddit Pulse",
    "The Algorithm Pact",
    "The DM Whisper",
    "The Depth Score",
    "The Engaged View",
    "The Director's Crown",
)


def list_realm_classes() -> list[dict[str, str]]:
    return [item.__dict__.copy() for item in REALM_CLASSES]


def list_realm_factions() -> list[dict[str, str]]:
    return [item.__dict__.copy() for item in REALM_FACTIONS]


def list_realm_quests() -> list[str]:
    return list(REALM_QUESTS)


def xp_to_next(level: int) -> int:
    safe_level = max(level, 1)
    return int(100 * (1.12 ** (safe_level - 1)))


def total_xp_for_level(level: int) -> int:
    return sum(xp_to_next(current) for current in range(1, max(level, 1)))
