"""Deterministic Director Brain scoring and learning service for LWA.

This v0 intentionally avoids external ML dependencies and binary model files.
It provides explainable scores that can be upgraded later with persisted proof,
style memory, embeddings, or trained models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Literal, Optional
from uuid import uuid4

ContentType = Literal[
    "hook",
    "caption",
    "title",
    "offer",
    "description",
    "clip_summary",
    "opportunity",
    "campaign_angle",
]
Goal = Literal["engagement", "conversion", "viral", "personal", "balanced"]
LearningLabel = Literal["winning", "rejected", "neutral"]
SignalType = Literal["save", "share", "click", "export", "purchase", "manual_feedback"]

DEFAULT_WEIGHTS = {
    "viral_hook_strength": 0.25,
    "retention_engagement": 0.25,
    "conversion_offer_fit": 0.20,
    "user_style_preference": 0.20,
    "proof_history_signal": 0.10,
}

GOAL_WEIGHTS = {
    "viral": {
        "viral_hook_strength": 0.35,
        "retention_engagement": 0.30,
        "conversion_offer_fit": 0.10,
        "user_style_preference": 0.15,
        "proof_history_signal": 0.10,
    },
    "engagement": {
        "viral_hook_strength": 0.25,
        "retention_engagement": 0.35,
        "conversion_offer_fit": 0.10,
        "user_style_preference": 0.20,
        "proof_history_signal": 0.10,
    },
    "conversion": {
        "viral_hook_strength": 0.18,
        "retention_engagement": 0.20,
        "conversion_offer_fit": 0.34,
        "user_style_preference": 0.18,
        "proof_history_signal": 0.10,
    },
    "personal": {
        "viral_hook_strength": 0.15,
        "retention_engagement": 0.20,
        "conversion_offer_fit": 0.15,
        "user_style_preference": 0.35,
        "proof_history_signal": 0.15,
    },
    "balanced": DEFAULT_WEIGHTS,
}

VIRAL_TERMS = {
    "stop",
    "secret",
    "truth",
    "mistake",
    "nobody",
    "everyone",
    "before",
    "after",
    "watch",
    "why",
    "how",
    "money",
    "proof",
    "system",
    "breakthrough",
    "hidden",
    "wrong",
}

CONVERSION_TERMS = {
    "buy",
    "book",
    "join",
    "download",
    "start",
    "try",
    "save",
    "follow",
    "comment",
    "learn",
    "offer",
    "client",
    "sales",
    "revenue",
    "money",
    "pay",
}

RETENTION_TERMS = {
    "first",
    "next",
    "then",
    "because",
    "but",
    "until",
    "moment",
    "watch",
    "story",
    "reason",
    "part",
    "finally",
}

GENERIC_WEAK_TERMS = {
    "check this out",
    "you won't believe",
    "interesting",
    "cool",
    "nice",
    "good",
    "amazing",
    "awesome",
}

LEARNING_EVENTS: List[Dict[str, Any]] = []


def _words(text: str) -> List[str]:
    return [word.strip(".,!?;:'\"()[]{}<>#@$").lower() for word in text.split() if word.strip()]


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _keyword_score(words: Iterable[str], keywords: set[str]) -> float:
    word_list = list(words)
    if not word_list:
        return 0.0
    hits = len([word for word in word_list if word in keywords])
    return _clamp(0.35 + hits * 0.12, 0.0, 1.0)


def _phrase_penalty(text: str) -> float:
    lowered = text.lower()
    return 0.14 if any(phrase in lowered for phrase in GENERIC_WEAK_TERMS) else 0.0


def _style_memory_score(text: str, style_memory: Optional[Dict[str, Any]]) -> float:
    if not style_memory:
        return 0.55

    lowered = text.lower()
    approved = [str(value).lower() for value in style_memory.get("approved_hook_patterns", [])]
    rejected = [str(value).lower() for value in style_memory.get("rejected_hook_patterns", [])]
    preferred_words = [str(value).lower() for value in style_memory.get("preferred_words", [])]
    avoid_words = [str(value).lower() for value in style_memory.get("avoid_words", [])]

    score = 0.55
    if any(pattern and pattern in lowered for pattern in approved):
        score += 0.22
    if any(word and word in lowered for word in preferred_words):
        score += 0.12
    if any(pattern and pattern in lowered for pattern in rejected):
        score -= 0.20
    if any(word and word in lowered for word in avoid_words):
        score -= 0.12
    return _clamp(score)


def _proof_history_score(text: str, proof_signals: Optional[Dict[str, Any]]) -> float:
    if not proof_signals:
        return 0.50

    lowered = text.lower()
    winning = [str(value).lower() for value in proof_signals.get("winning_keywords", [])]
    rejected = [str(value).lower() for value in proof_signals.get("rejected_keywords", [])]

    score = 0.50
    score += 0.10 * len([word for word in winning if word and word in lowered])
    score -= 0.10 * len([word for word in rejected if word and word in lowered])
    return _clamp(score)


def _content_type_adjustment(content_type: ContentType, score: float, words: List[str]) -> float:
    word_count = len(words)
    if content_type == "hook":
        if 4 <= word_count <= 14:
            score += 0.08
        if word_count > 22:
            score -= 0.12
    elif content_type == "caption":
        if word_count >= 8:
            score += 0.04
    elif content_type == "offer":
        if any(word in CONVERSION_TERMS for word in words):
            score += 0.08
    return _clamp(score)


def _component_scores(
    text: str,
    content_type: ContentType,
    style_memory: Optional[Dict[str, Any]],
    proof_signals: Optional[Dict[str, Any]],
) -> Dict[str, float]:
    words = _words(text)
    word_count = len(words)
    penalty = _phrase_penalty(text)

    viral = _keyword_score(words, VIRAL_TERMS)
    if text.strip().endswith("?"):
        viral += 0.08
    if word_count <= 3:
        viral -= 0.18
    viral -= penalty

    retention = _keyword_score(words, RETENTION_TERMS)
    if 6 <= word_count <= 18:
        retention += 0.10
    if word_count > 35:
        retention -= 0.10
    retention -= penalty / 2

    conversion = _keyword_score(words, CONVERSION_TERMS)
    if any(word in words for word in {"you", "your", "creators", "clients"}):
        conversion += 0.05

    style = _style_memory_score(text, style_memory)
    proof = _proof_history_score(text, proof_signals)

    return {
        "viral_hook_strength": round(_content_type_adjustment(content_type, viral, words), 3),
        "retention_engagement": round(_clamp(retention), 3),
        "conversion_offer_fit": round(_clamp(conversion), 3),
        "user_style_preference": round(style, 3),
        "proof_history_signal": round(proof, 3),
    }


def _weighted_score(component_scores: Dict[str, float], goal: Goal) -> float:
    weights = GOAL_WEIGHTS.get(goal, DEFAULT_WEIGHTS)
    return round(sum(component_scores[key] * weights[key] for key in DEFAULT_WEIGHTS), 3)


def _reasons(text: str, component_scores: Dict[str, float]) -> List[str]:
    reasons: List[str] = []
    if component_scores["viral_hook_strength"] >= 0.75:
        reasons.append("Strong hook signal with curiosity, urgency, or contradiction.")
    if component_scores["retention_engagement"] >= 0.75:
        reasons.append("Good retention language that can carry a viewer into the next beat.")
    if component_scores["conversion_offer_fit"] >= 0.75:
        reasons.append("Clear action or value language that can support conversion.")
    if component_scores["user_style_preference"] >= 0.70:
        reasons.append("Matches the creator's saved style memory or preferred language.")
    if component_scores["proof_history_signal"] >= 0.70:
        reasons.append("Overlaps with proof/history signals from prior winning content.")
    if _phrase_penalty(text):
        reasons.append("Contains a generic phrase; make it more specific before publishing.")
    if not reasons:
        reasons.append("Usable starting point, but it needs a sharper promise, conflict, or action.")
    return reasons[:5]


def _suggested_improvement(text: str, content_type: ContentType, component_scores: Dict[str, float]) -> str:
    if component_scores["viral_hook_strength"] < 0.62 and content_type == "hook":
        return "Add a stronger curiosity gap, contradiction, or specific outcome in the first 8 words."
    if component_scores["conversion_offer_fit"] < 0.55:
        return "Add a clearer action, offer, or viewer payoff so the clip drives behavior."
    if component_scores["retention_engagement"] < 0.55:
        return "Add a tension word like 'but', 'until', 'because', or 'watch' to create forward motion."
    if _phrase_penalty(text):
        return "Replace generic hype with a more concrete promise or proof point."
    return "Strong v0 score. Pair it with a clear caption, thumbnail text, and post order."


def _lee_wuh_recommendation(score: float, content_type: ContentType) -> str:
    if score >= 0.84:
        return f"Boss-level {content_type}. Use this near the front of the pack and test it first."
    if score >= 0.70:
        return f"Solid {content_type}. Keep it, but tighten the promise before export."
    if score >= 0.55:
        return f"Useful draft. Add specificity, stakes, or a clearer viewer payoff."
    return f"Not ready yet. Rework this before it touches a real campaign."


def score_text(
    text: str,
    content_type: ContentType = "hook",
    platform: Optional[str] = None,
    goal: Goal = "balanced",
    style_memory: Optional[Dict[str, Any]] = None,
    proof_signals: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cleaned = " ".join(text.strip().split())
    component_scores = _component_scores(cleaned, content_type, style_memory, proof_signals)
    score = _weighted_score(component_scores, goal)

    return {
        "success": True,
        "text": cleaned,
        "content_type": content_type,
        "platform": platform or "all",
        "goal": goal,
        "score": score,
        "component_scores": component_scores,
        "reasons": _reasons(cleaned, component_scores),
        "lee_wuh_recommendation": _lee_wuh_recommendation(score, content_type),
        "suggested_improvement": _suggested_improvement(cleaned, content_type, component_scores),
        "confidence": round(_clamp(0.58 + abs(score - 0.5) * 0.55), 3),
        "mode": "heuristic_v0",
        "algorithm_version": "director_brain_heuristic_v0.1",
    }


def rank_candidates(
    candidates: List[str],
    content_type: ContentType = "hook",
    platform: Optional[str] = None,
    goal: Goal = "balanced",
    style_memory: Optional[Dict[str, Any]] = None,
    proof_signals: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    scored = [
        score_text(
            candidate,
            content_type=content_type,
            platform=platform,
            goal=goal,
            style_memory=style_memory,
            proof_signals=proof_signals,
        )
        for candidate in candidates
        if candidate and candidate.strip()
    ]
    scored.sort(key=lambda item: item["score"], reverse=True)

    ranked = []
    for index, item in enumerate(scored, start=1):
        ranked.append({**item, "rank": index, "post_rank": index})

    return {
        "success": True,
        "ranked_candidates": ranked,
        "best_candidate": ranked[0] if ranked else None,
        "count": len(ranked),
        "mode": "heuristic_v0",
    }


def learn_event(
    text: str,
    label: LearningLabel,
    signal_type: SignalType,
    weight: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    event = {
        "id": f"learn_{uuid4().hex[:12]}",
        "text": " ".join(text.strip().split()),
        "label": label,
        "signal_type": signal_type,
        "weight": _clamp(weight, 0.0, 5.0),
        "metadata": metadata or {},
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    LEARNING_EVENTS.append(event)
    return {
        "success": True,
        "event": event,
        "message": "Learning event stored as metadata for Director Brain v0.",
    }


def get_status() -> Dict[str, Any]:
    return {
        "success": True,
        "mode": "heuristic_v0",
        "algorithm_version": "director_brain_heuristic_v0.1",
        "learning_event_count": len(LEARNING_EVENTS),
        "weights": DEFAULT_WEIGHTS,
        "supported_content_types": [
            "hook",
            "caption",
            "title",
            "offer",
            "description",
            "clip_summary",
            "opportunity",
            "campaign_angle",
        ],
        "supported_goals": ["engagement", "conversion", "viral", "personal", "balanced"],
        "live_paid_providers_enabled": False,
        "binary_model_required": False,
    }
