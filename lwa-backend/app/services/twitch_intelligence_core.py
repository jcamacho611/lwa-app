from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# LWA OMEGA
# CLAUDE HANDOFF
# TWITCH INTELLIGENCE FOUNDATION
# LOCAL-FIRST FALLBACK
# NONFATAL PIPELINE

CHAT_SPIKE_TERMS = {"clip", "no way", "amazing", "funny", "again", "wow", "huge", "crazy"}


@dataclass(frozen=True)
class TwitchMomentScore:
    score: int
    reason: str
    tags: list[str]


def score_twitch_moment(moment: dict[str, Any]) -> TwitchMomentScore:
    title = str(moment.get("title") or moment.get("text") or "").lower()
    chat_messages = [str(item).lower() for item in moment.get("chat_messages", []) if item]
    viewer_delta = moment.get("viewer_delta") if isinstance(moment.get("viewer_delta"), (int, float)) else 0

    tags: list[str] = []
    score = 40

    if any(term in title for term in CHAT_SPIKE_TERMS):
        score += 15
        tags.append("title-spike")

    chat_blob = " ".join(chat_messages)
    chat_hits = sum(1 for term in CHAT_SPIKE_TERMS if term in chat_blob)
    if chat_hits:
        score += min(chat_hits * 8, 24)
        tags.append("chat-reacted")

    if viewer_delta and viewer_delta > 0:
        score += min(int(viewer_delta), 20)
        tags.append("viewer-rise")

    score = max(0, min(100, score))
    return TwitchMomentScore(
        score=score,
        reason="Twitch score based on chat spike terms, title signal, and viewer movement.",
        tags=tags,
    )


def rank_twitch_moments(moments: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for moment in moments:
        scored = score_twitch_moment(moment)
        ranked.append({**moment, "twitch_score": scored.score, "twitch_reason": scored.reason, "twitch_tags": scored.tags})
    return sorted(ranked, key=lambda item: item.get("twitch_score", 0), reverse=True)[:limit]
