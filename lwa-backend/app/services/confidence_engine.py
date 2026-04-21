from __future__ import annotations

from typing import Any, Mapping


def _read_value(source: Any, key: str) -> Any:
    if isinstance(source, Mapping):
        return source.get(key)
    return getattr(source, key, None)


def _coerce_score(value: Any, fallback: int = 70) -> int:
    try:
        return max(0, min(int(round(float(value))), 100))
    except (TypeError, ValueError):
        return fallback


def resolve_confidence_score(clip: Any) -> int:
    confidence_score = _read_value(clip, "confidence_score")
    if confidence_score is not None:
        return _coerce_score(confidence_score)

    confidence = _read_value(clip, "confidence")
    if confidence is not None:
        try:
            confidence_float = float(confidence)
            if 0 <= confidence_float <= 1:
                return _coerce_score(confidence_float * 100)
            return _coerce_score(confidence_float)
        except (TypeError, ValueError):
            pass

    return _coerce_score(_read_value(clip, "score"))


def build_confidence_label(clip: Any) -> str:
    score = resolve_confidence_score(clip)

    if score >= 88:
        return "High viral potential"
    if score >= 76:
        return "Strong early signal"
    if score >= 64:
        return "Worth testing"
    return "Needs stronger packaging"


def enrich_confidence(clip: dict[str, Any]) -> dict[str, Any]:
    clip["confidence_score"] = resolve_confidence_score(clip)
    clip["confidence_label"] = build_confidence_label(clip)
    return clip
