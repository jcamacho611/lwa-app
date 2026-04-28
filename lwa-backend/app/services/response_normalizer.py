from typing import Any, Dict, List

from .confidence_engine import enrich_confidence


def _coerce_score(value: Any, fallback: int) -> int:
    try:
        return max(0, min(int(round(float(value))), 100))
    except (TypeError, ValueError):
        return fallback


def _fallback_hook_score(clip: Dict[str, Any], score: int) -> int:
    hook = str(clip.get("hook") or "").strip()
    if not hook:
        return max(score - 8, 30)
    bonus = 0
    lowered = hook.lower()
    if any(lowered.startswith(prefix) for prefix in ("stop", "why", "how", "most", "this", "here")):
        bonus += 12
    if any(keyword in lowered for keyword in ("exact", "secret", "mistake", "wrong", "before", "nobody")):
        bonus += 12
    if any(char.isdigit() for char in hook):
        bonus += 8
    if "?" in hook or "!" in hook:
        bonus += 6
    return min(max(42, score + bonus - 10), 100)


def is_rendered(clip: Dict[str, Any]) -> bool:
    """Check if a clip has playable rendered video assets."""
    return any(
        [
            clip.get("preview_url"),
            clip.get("edited_clip_url"),
            clip.get("clip_url"),
            clip.get("raw_clip_url"),
        ]
    )


def has_preview_asset(clip: Dict[str, Any]) -> bool:
    """Check if a clip has any useful preview surface, playable or still."""
    return any(
        [
            clip.get("preview_url"),
            clip.get("edited_clip_url"),
            clip.get("clip_url"),
            clip.get("raw_clip_url"),
            clip.get("thumbnail_url"),
            clip.get("preview_image_url"),
        ]
    )


def normalize_clip(clip: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Normalize a single clip to ensure consistent schema."""
    thumbnail_url = clip.get("thumbnail_url") or clip.get("preview_image_url")
    raw_score = _coerce_score(clip.get("score"), 70)
    reason = (
        clip.get("why_this_matters")
        or clip.get("reason")
        or "Strong early signal. Keep this in your posting plan while the preview finishes."
    )
    rendered = is_rendered(clip)
    hook_score = _coerce_score(clip.get("hook_score"), _fallback_hook_score(clip, raw_score))
    render_readiness_score = _coerce_score(
        clip.get("render_readiness_score"),
        _coerce_score(clip.get("render_quality_score"), 78 if rendered else 42),
    )
    score_breakdown = clip.get("score_breakdown") or {
        "hook_score": hook_score,
        "retention_score": raw_score,
        "emotional_spike_score": max(raw_score - 8, 0),
        "clarity_score": raw_score,
        "platform_fit_score": max(raw_score - 4, 0),
        "visual_energy_score": max(raw_score - 12, 0),
        "audio_energy_score": max(raw_score - 10, 0),
        "controversy_score": max(raw_score - 18, 0),
        "educational_value_score": max(raw_score - 14, 0),
        "share_comment_score": max(raw_score - 16, 0),
        "render_readiness_score": render_readiness_score,
        "commercial_value_score": max(raw_score - 20, 0),
    }
    normalized = {
        "id": clip.get("id") or f"clip_{index}",
        "title": clip.get("title") or clip.get("hook") or "Untitled clip",
        "hook": clip.get("hook") or "",
        "caption": clip.get("caption") or "",
        "score": raw_score,
        "hook_score": hook_score,
        "rank": clip.get("rank") or index,
        "post_rank": clip.get("post_rank") or index,
        "reason": reason,
        "why_this_matters": clip.get("why_this_matters") or reason,
        "score_breakdown": score_breakdown,
        "scoring_explanation": clip.get("scoring_explanation")
        or "Score led by hook strength, clarity, and platform fit. Review readiness separately before posting.",
        "category": clip.get("category") or "General",
        "emotional_trigger": clip.get("emotional_trigger"),
        "thumbnail_text": clip.get("thumbnail_text") or "",
        "cta_suggestion": clip.get("cta_suggestion") or "",
        "packaging_angle": clip.get("packaging_angle") or "",
        "platform_fit": clip.get("platform_fit") or "Short-form",
        "caption_style": clip.get("caption_style"),
        "hook_variants": clip.get("hook_variants") or [],
        "caption_variants": clip.get("caption_variants") or {},
        "clip_url": clip.get("clip_url"),
        "raw_clip_url": clip.get("raw_clip_url"),
        "edited_clip_url": clip.get("edited_clip_url"),
        "preview_url": clip.get("preview_url"),
        "preview_image_url": clip.get("preview_image_url") or thumbnail_url,
        "thumbnail_url": thumbnail_url,
        "download_url": clip.get("download_url"),
        "render_readiness_score": render_readiness_score,
        "render_quality_score": clip.get("render_quality_score") or render_readiness_score,
        "is_rendered": rendered,
        "is_strategy_only": not rendered,
        "render_status": clip.get("render_status") or ("ready" if rendered else "pending"),
        "strategy_only_reason": clip.get("strategy_only_reason"),
        "recovery_recommendation": clip.get("recovery_recommendation"),
        "approval_state": clip.get("approval_state") or ("approved" if rendered and render_readiness_score >= 72 else "needs_edit" if not rendered else "new"),
        "campaign_requirement_checks": clip.get("campaign_requirement_checks") or [],
        "request_id": clip.get("request_id"),
    }
    return enrich_confidence(normalized)


def normalize_response(clips: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalize a list of clips and separate rendered from strategy-only.
    """
    normalized = [normalize_clip(c, i + 1) for i, c in enumerate(clips)]

    rendered = [c for c in normalized if has_preview_asset(c)]
    strategy = [c for c in normalized if not has_preview_asset(c)]

    return {
        "clips": normalized,
        "rendered_count": len(rendered),
        "strategy_count": len(strategy),
    }
