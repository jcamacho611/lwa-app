from typing import Any, Dict, List

from .confidence_engine import enrich_confidence


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
    reason = (
        clip.get("why_this_matters")
        or clip.get("reason")
        or "Strong early signal. Keep this in your posting plan while the preview finishes."
    )
    normalized = {
        "id": clip.get("id") or f"clip_{index}",
        "title": clip.get("title") or clip.get("hook") or "Untitled clip",
        "hook": clip.get("hook") or "",
        "caption": clip.get("caption") or "",
        "score": clip.get("score") or 70,
        "rank": clip.get("rank") or index,
        "post_rank": clip.get("post_rank") or index,
        "reason": reason,
        "why_this_matters": clip.get("why_this_matters") or reason,
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
        "is_rendered": is_rendered(clip),
        "is_strategy_only": not is_rendered(clip),
        "render_status": clip.get("render_status") or ("ready" if is_rendered(clip) else "pending"),
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
