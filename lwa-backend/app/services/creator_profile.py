from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CreatorProfile:
    creator_type: str = "creator"
    brand_voice: str = "clear"
    target_customer: str = "general audience"
    offer: str = ""
    preferred_platforms: tuple[str, ...] = ("tiktok", "instagram_reels", "youtube_shorts")
    banned_words: tuple[str, ...] = field(default_factory=tuple)
    winning_hooks: tuple[str, ...] = field(default_factory=tuple)
    bad_past_outputs: tuple[str, ...] = field(default_factory=tuple)


def normalize_creator_type(value: str | None) -> str:
    normalized = (value or "creator").strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "podcaster": "podcast",
        "streamer": "streamer",
        "agency_owner": "agency",
        "whop": "whop_seller",
        "local": "local_business",
    }
    return aliases.get(normalized, normalized or "creator")


def build_creator_profile(
    *,
    creator_type: str | None = None,
    brand_voice: str | None = None,
    target_customer: str | None = None,
    offer: str | None = None,
    preferred_platforms: list[str] | tuple[str, ...] | None = None,
    banned_words: list[str] | tuple[str, ...] | None = None,
) -> CreatorProfile:
    return CreatorProfile(
        creator_type=normalize_creator_type(creator_type),
        brand_voice=(brand_voice or "clear").strip() or "clear",
        target_customer=(target_customer or "general audience").strip() or "general audience",
        offer=(offer or "").strip(),
        preferred_platforms=tuple(preferred_platforms or ("tiktok", "instagram_reels", "youtube_shorts")),
        banned_words=tuple(banned_words or ()),
    )


def profile_fit_notes(*, profile: CreatorProfile, transcript: str) -> list[str]:
    notes: list[str] = []
    lowered = transcript.lower()
    if profile.offer and profile.offer.lower() in lowered:
        notes.append("Transcript directly supports the creator offer.")
    if profile.creator_type in {"agency", "local_business", "whop_seller"}:
        notes.append("Prioritize clips that explain value and drive action.")
    if any(word.lower() in lowered for word in profile.banned_words):
        notes.append("Transcript includes a banned or discouraged word; review copy before posting.")
    if not notes:
        notes.append("Use general creator packaging until more profile data exists.")
    return notes
