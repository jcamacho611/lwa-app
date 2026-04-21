from typing import List, Dict


def is_rendered(clip: Dict) -> bool:
    """Check if a clip has any rendered video assets."""
    return any([
        clip.get("preview_url"),
        clip.get("edited_clip_url"),
        clip.get("clip_url"),
        clip.get("raw_clip_url"),
        clip.get("download_url"),
    ])


def normalize_clip(clip: Dict, index: int) -> Dict:
    """Normalize a single clip to ensure consistent schema."""
    return {
        "id": clip.get("id") or f"clip_{index}",
        "title": clip.get("title") or "Untitled clip",
        "hook": clip.get("hook") or "",
        "caption": clip.get("caption") or "",
        "score": clip.get("score") or 0,
        "confidence_score": clip.get("confidence_score"),
        "rank": clip.get("rank") or index,
        "post_rank": clip.get("post_rank") or index,
        "why_this_matters": clip.get("why_this_matters") or "",
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
        "preview_image_url": clip.get("preview_image_url"),
        "download_url": clip.get("download_url"),
        "is_rendered": is_rendered(clip),
    }


def normalize_response(clips: List[Dict]) -> Dict:
    """
    Normalize a list of clips and separate rendered from strategy-only.
    """
    normalized = [normalize_clip(c, i + 1) for i, c in enumerate(clips)]

    rendered = [c for c in normalized if c["is_rendered"]]
    strategy = [c for c in normalized if not c["is_rendered"]]

    return {
        "clips": normalized,
        "rendered_count": len(rendered),
        "strategy_count": len(strategy),
    }