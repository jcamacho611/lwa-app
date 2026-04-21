from __future__ import annotations

from typing import Any


def _duration(clip: dict[str, Any]) -> float:
    if clip.get("duration") is not None:
        return max(float(clip.get("duration") or 0), 0.0)
    return max(float(clip.get("end_time") or 0) - float(clip.get("start_time") or 0), 0.0)


def score_clip(clip: dict[str, Any]) -> int:
    score = 50
    duration = _duration(clip)
    transcript = str(clip.get("transcript") or clip.get("transcript_excerpt") or "")
    hook = str(clip.get("hook") or "")

    if hook:
        score += 12
    if clip.get("emotional_trigger"):
        score += 14
    if transcript:
        words = transcript.split()
        score += 8
        speech_density = len(words) / max(duration, 1.0)
        if 2.0 <= speech_density <= 4.8:
            score += 8
        elif speech_density > 4.8:
            score += 4
    if 12 <= duration <= 35:
        score += 14
    elif 8 <= duration <= 45:
        score += 8
    if clip.get("category") in {"Story", "Debate", "Payoff"}:
        score += 4

    return min(max(score, 1), 100)


def build_reason(clip: dict[str, Any]) -> str:
    if clip.get("emotional_trigger"):
        return f"Strong emotional trigger: {clip['emotional_trigger']}"
    if clip.get("transcript_excerpt"):
        excerpt = str(clip["transcript_excerpt"]).strip()
        return f"Speech-first moment with a clear setup: {excerpt[:90]}"
    if clip.get("hook"):
        return f"Hook-driven clip: {str(clip['hook'])[:70]}"
    return "Speech-first segment with strong pacing potential."


def build_category(clip: dict[str, Any]) -> str:
    text = str(clip.get("transcript") or clip.get("transcript_excerpt") or "").lower()
    if any(token in text for token in {"argument", "debate", "disagree", "wrong"}):
        return "Debate"
    if any(token in text for token in {"story", "happened", "remember", "when i"}):
        return "Story"
    if any(token in text for token in {"why", "because", "realize", "truth"}):
        return "Payoff"
    return "General"
