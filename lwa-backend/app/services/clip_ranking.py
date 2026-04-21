from typing import List, Dict
from app.services.platform_fit import infer_platform_fit
from app.services.packaging_angle import infer_packaging_angle

PUNCH_WORDS = [
    "stop", "watch", "crazy", "nobody", "never", "exact", "why",
    "how", "this", "secret", "wrong", "best", "first", "mistake",
]


def opening_strength_score(clip: Dict) -> float:
    """
    Score the opening strength of a clip based on hook/title keywords.
    """
    hook = (clip.get("hook") or "").lower()
    title = (clip.get("title") or "").lower()

    score = 0.0
    for word in PUNCH_WORDS:
        if word in hook:
            score += 3
        if word in title:
            score += 1

    # Optimal hook length for short-form (8-20 words)
    if 8 <= len(hook.split()) <= 20:
        score += 5

    return score


def pacing_score(clip: Dict) -> float:
    """
    Score the pacing quality of a clip based on hook structure.
    """
    hook = clip.get("hook") or ""
    words = hook.split()

    score = 0.0

    # Tight short-form hooks tend to work better.
    if 8 <= len(words) <= 18:
        score += 8
    elif len(words) <= 24:
        score += 4

    # Strong punctuation can help interruption energy.
    if "?" in hook or ":" in hook:
        score += 2

    return score


def ending_quality_score(clip: Dict) -> float:
    """
    Score the ending quality based on why_this_matters and CTA presence.
    """
    why = (clip.get("why_this_matters") or "").lower()
    cta = (clip.get("cta_suggestion") or "").lower()

    score = 0.0
    if why:
        score += 2
    if cta:
        score += 3
    return score


def rank_clips(clips: List[Dict]) -> List[Dict]:
    """
    Rank clips by combining base score with opening, pacing, and ending quality.
    Also adds platform_fit and packaging_angle if not present.
    """
    ranked = []

    for idx, clip in enumerate(clips):
        base = float(clip.get("score") or 0)

        open_score = opening_strength_score(clip)
        pace_score = pacing_score(clip)
        end_score = ending_quality_score(clip)

        total = base + open_score + pace_score + end_score

        # Add platform_fit and packaging_angle if not present
        clip["platform_fit"] = clip.get("platform_fit") or infer_platform_fit(
            clip.get("title", ""),
            clip.get("hook", ""),
            30.0,
        )
        clip["packaging_angle"] = clip.get("packaging_angle") or infer_packaging_angle(
            clip.get("title", ""),
            clip.get("hook", ""),
        )
        clip["confidence_score"] = clip.get("confidence_score") or min(int(total), 100)
        clip["_rank_score"] = total
        ranked.append(clip)

    # Sort by rank score descending
    ranked.sort(key=lambda c: c["_rank_score"], reverse=True)

    # Assign rank and post_rank
    for idx, clip in enumerate(ranked, start=1):
        clip["rank"] = idx
        clip["post_rank"] = idx
        clip.pop("_rank_score", None)

    return ranked