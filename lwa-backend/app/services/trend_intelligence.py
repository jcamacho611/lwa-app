from __future__ import annotations

import re
from typing import Iterable

from ..models.schemas import TrendItem

STOPWORDS = {
    "about",
    "after",
    "again",
    "before",
    "being",
    "could",
    "every",
    "first",
    "from",
    "have",
    "here",
    "into",
    "just",
    "more",
    "most",
    "only",
    "over",
    "that",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "today",
    "what",
    "when",
    "where",
    "which",
    "while",
    "with",
    "would",
    "your",
}

EVERGREEN_MARKERS = (
    "how to",
    "step",
    "system",
    "framework",
    "mistake",
    "lesson",
    "checklist",
    "playbook",
    "process",
    "method",
    "rule",
    "breakdown",
    "tutorial",
    "guide",
)

TIME_SENSITIVE_MARKERS = (
    "today",
    "this week",
    "right now",
    "breaking",
    "just dropped",
    "new update",
    "launch day",
    "yesterday",
    "tomorrow",
    "live now",
    "latest",
    "2026",
    "2025",
    "trend",
    "trending",
)


def _text_blob(clip: object) -> str:
    values: list[str] = []
    for key in ("title", "hook", "caption", "transcript_excerpt", "transcript", "why_this_matters"):
        value = getattr(clip, key, None)
        if value:
            values.append(str(value).strip())
    return " ".join(values).strip().lower()


def _extract_terms(text: str) -> set[str]:
    return {
        match
        for match in re.findall(r"[a-z0-9]{3,}", text.lower())
        if match not in STOPWORDS
    }


def _term_overlap_score(base_terms: set[str], candidate_terms: set[str]) -> int:
    if not base_terms or not candidate_terms:
        return 0
    overlap = len(base_terms & candidate_terms)
    if overlap <= 0:
        return 0
    return min(int((overlap / max(len(candidate_terms), 1)) * 100), 100)


def _contains_any_phrase(text: str, phrases: Iterable[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def build_trend_intelligence(
    *,
    clip: object,
    selected_trend: str | None,
    trend_context: list[TrendItem],
) -> dict[str, object]:
    text_blob = _text_blob(clip)
    clip_terms = _extract_terms(text_blob)

    selected_trend_text = (selected_trend or "").strip().lower()
    selected_trend_terms = _extract_terms(selected_trend_text)
    selected_trend_phrase_match = bool(selected_trend_text and selected_trend_text in text_blob)
    selected_trend_overlap = _term_overlap_score(clip_terms, selected_trend_terms)

    live_titles = [item.title.strip().lower() for item in trend_context[:6] if item.title]
    live_scores: list[int] = []
    live_phrase_match = False
    for title in live_titles:
        if title in text_blob:
            live_phrase_match = True
        live_scores.append(_term_overlap_score(clip_terms, _extract_terms(title)))
    live_trend_overlap = max(live_scores or [0])

    trend_match_score = max(selected_trend_overlap, live_trend_overlap // 2)
    if selected_trend_phrase_match:
        trend_match_score = max(trend_match_score, 82)
    elif selected_trend_overlap >= 55:
        trend_match_score = max(trend_match_score, 72)
    elif live_phrase_match:
        trend_match_score = max(trend_match_score, 70)
    elif selected_trend_overlap >= 30 or live_trend_overlap >= 45:
        trend_match_score = max(trend_match_score, 54)

    evergreen_hits = sum(1 for marker in EVERGREEN_MARKERS if marker in text_blob)
    explicit_time_markers = sum(1 for marker in TIME_SENSITIVE_MARKERS if marker in text_blob)

    time_sensitivity = "low"
    if explicit_time_markers >= 2 or trend_match_score >= 80:
        time_sensitivity = "high"
    elif explicit_time_markers == 1 or trend_match_score >= 55:
        time_sensitivity = "medium"

    reuse_potential = 68 + (evergreen_hits * 8)
    if time_sensitivity == "medium":
        reuse_potential -= 10
    elif time_sensitivity == "high":
        reuse_potential -= 22
    if trend_match_score >= 75:
        reuse_potential -= 12
    elif trend_match_score >= 55:
        reuse_potential -= 6
    reuse_potential = max(0, min(reuse_potential, 100))

    if time_sensitivity == "high":
        evergreen_status = "time_sensitive"
    elif reuse_potential >= 78:
        evergreen_status = "evergreen"
    elif trend_match_score >= 55:
        evergreen_status = "trend_aware"
    else:
        evergreen_status = "mixed"

    if selected_trend_phrase_match:
        trend_alignment_reason = f"Strongly aligned to the selected trend '{selected_trend}'."
    elif trend_match_score >= 55 and selected_trend:
        trend_alignment_reason = f"Partially aligned to the selected trend '{selected_trend}' through shared language and framing."
    elif trend_match_score >= 55:
        trend_alignment_reason = "Aligned to live trend context through overlapping framing and subject language."
    elif evergreen_status == "evergreen":
        trend_alignment_reason = "Built more like evergreen packaging than a timely trend response."
    else:
        trend_alignment_reason = "Only light overlap with current trend context. Treat this as a durable supporting clip."

    return {
        "trend_match_score": trend_match_score,
        "trend_alignment_reason": trend_alignment_reason,
        "reuse_potential": reuse_potential,
        "evergreen_status": evergreen_status,
        "time_sensitivity": time_sensitivity,
    }
