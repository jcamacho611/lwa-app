"""
Output Engine Service — Phase 2
Provides caption structure enrichment, edit-plan generation, platform-aware
output hints, creator-readiness scoring, output bundle logic, and export
metadata generation.
"""
from __future__ import annotations

import re
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Platform Output Profiles
# ---------------------------------------------------------------------------

PLATFORM_OUTPUT_PROFILES: dict[str, dict] = {
    "tiktok": {
        "label": "TikTok",
        "aspect_ratio": "9:16",
        "max_duration_seconds": 60,
        "ideal_duration_range": (15, 45),
        "caption_max_chars": 150,
        "caption_style": "Punchy proof-first",
        "overlay_style": "bold_center",
        "font_weight": "heavy",
        "color_palette": "high_contrast",
        "hook_position": "first_2_seconds",
        "cta_position": "last_3_seconds",
        "creator_tips": [
            "Hook must land in the first 2 seconds or viewers swipe away.",
            "Use bold, high-contrast text overlays for maximum readability.",
            "End with a comment-bait CTA to boost engagement signals.",
            "Keep captions under 150 characters for clean display.",
        ],
        "export_hints": {
            "resolution": "1080x1920",
            "fps": 30,
            "bitrate": "4M",
            "audio_normalize": True,
        },
    },
    "instagram": {
        "label": "Instagram Reels",
        "aspect_ratio": "9:16",
        "max_duration_seconds": 90,
        "ideal_duration_range": (15, 60),
        "caption_max_chars": 220,
        "caption_style": "Polished emotional",
        "overlay_style": "clean_lower_third",
        "font_weight": "medium",
        "color_palette": "aesthetic_warm",
        "hook_position": "first_3_seconds",
        "cta_position": "last_5_seconds",
        "creator_tips": [
            "Polished visuals and clean framing perform better on Reels.",
            "Use a save-worthy CTA — saves are the highest-value signal on Instagram.",
            "Captions can be slightly longer; use line breaks for readability.",
            "Aesthetic consistency across your feed amplifies Reels performance.",
        ],
        "export_hints": {
            "resolution": "1080x1920",
            "fps": 30,
            "bitrate": "5M",
            "audio_normalize": True,
        },
    },
    "youtube": {
        "label": "YouTube Shorts",
        "aspect_ratio": "9:16",
        "max_duration_seconds": 60,
        "ideal_duration_range": (20, 55),
        "caption_max_chars": 200,
        "caption_style": "Clarity-led payoff",
        "overlay_style": "subtitle_bottom",
        "font_weight": "medium",
        "color_palette": "clean_neutral",
        "hook_position": "first_3_seconds",
        "cta_position": "last_5_seconds",
        "creator_tips": [
            "Context-light openers work best — viewers don't need setup.",
            "Payoff-first structure drives the highest retention on Shorts.",
            "Use a subscribe CTA at the end to convert Shorts viewers to subscribers.",
            "Closed captions improve accessibility and watch time.",
        ],
        "export_hints": {
            "resolution": "1080x1920",
            "fps": 30,
            "bitrate": "5M",
            "audio_normalize": True,
        },
    },
    "facebook": {
        "label": "Facebook Reels",
        "aspect_ratio": "9:16",
        "max_duration_seconds": 60,
        "ideal_duration_range": (15, 45),
        "caption_max_chars": 250,
        "caption_style": "Story-first social",
        "overlay_style": "clean_lower_third",
        "font_weight": "medium",
        "color_palette": "clean_neutral",
        "hook_position": "first_3_seconds",
        "cta_position": "last_5_seconds",
        "creator_tips": [
            "Facebook audiences skew slightly older — clarity beats cleverness.",
            "Comment-friendly framing drives the most reach on Facebook.",
            "Longer captions with context perform well for Facebook's algorithm.",
            "Share-worthy content is the highest-value signal on Facebook.",
        ],
        "export_hints": {
            "resolution": "1080x1920",
            "fps": 30,
            "bitrate": "4M",
            "audio_normalize": True,
        },
    },
}

_DEFAULT_PLATFORM_PROFILE = PLATFORM_OUTPUT_PROFILES["tiktok"]


# ---------------------------------------------------------------------------
# Caption Structure Enrichment
# ---------------------------------------------------------------------------

def enrich_caption_structure(
    *,
    caption: str,
    hook: str,
    cta_suggestion: str,
    target_platform: str,
    packaging_angle: str,
    caption_style: str,
) -> dict:
    """
    Returns a structured caption bundle with platform-aware formatting.
    """
    profile = _resolve_platform_profile(target_platform)
    max_chars = profile["caption_max_chars"]

    # Trim caption to platform limit
    trimmed_caption = caption[:max_chars].rstrip() if len(caption) > max_chars else caption

    # Build structured caption parts
    hook_line = hook.strip()
    body_line = trimmed_caption.strip()
    cta_line = cta_suggestion.strip()

    # Compose full caption
    parts = [p for p in [hook_line, body_line, cta_line] if p]
    full_caption = " ".join(parts)
    if len(full_caption) > max_chars:
        full_caption = full_caption[:max_chars].rstrip()

    return {
        "hook_line": hook_line,
        "body_line": body_line,
        "cta_line": cta_line,
        "full_caption": full_caption,
        "char_count": len(full_caption),
        "platform_limit": max_chars,
        "within_limit": len(full_caption) <= max_chars,
        "style": caption_style or profile["caption_style"],
        "overlay_style": profile["overlay_style"],
    }


# ---------------------------------------------------------------------------
# Edit Plan Structure Generation
# ---------------------------------------------------------------------------

def generate_edit_plan(
    *,
    clip_id: str,
    title: str,
    hook: str,
    packaging_angle: str,
    target_platform: str,
    duration_seconds: int | None,
    transcript_excerpt: str | None,
    category: str = "",
    primary_trigger: str = "curiosity",
) -> dict:
    """
    Returns a structured edit plan for the clip.
    """
    profile = _resolve_platform_profile(target_platform)
    ideal_min, ideal_max = profile["ideal_duration_range"]
    duration = duration_seconds or 30

    # Determine edit beats
    beats = _build_edit_beats(
        duration=duration,
        packaging_angle=packaging_angle,
        hook=hook,
        transcript_excerpt=transcript_excerpt,
        primary_trigger=primary_trigger,
    )

    return {
        "clip_id": clip_id,
        "title": title,
        "target_platform": profile["label"],
        "aspect_ratio": profile["aspect_ratio"],
        "duration_seconds": duration,
        "ideal_duration_range": f"{ideal_min}–{ideal_max}s",
        "within_ideal_range": ideal_min <= duration <= ideal_max,
        "packaging_angle": packaging_angle,
        "overlay_style": profile["overlay_style"],
        "font_weight": profile["font_weight"],
        "color_palette": profile["color_palette"],
        "hook_position": profile["hook_position"],
        "cta_position": profile["cta_position"],
        "edit_beats": beats,
        "category": category,
        "primary_trigger": primary_trigger,
    }


def _build_edit_beats(
    *,
    duration: int,
    packaging_angle: str,
    hook: str,
    transcript_excerpt: str | None,
    primary_trigger: str,
) -> list[dict]:
    """
    Returns a list of edit beat dicts describing the clip's structure.
    """
    beats: list[dict] = []

    # Beat 1: Hook (always first 2–3 seconds)
    beats.append({
        "beat": "hook",
        "start_seconds": 0,
        "end_seconds": min(3, duration),
        "description": f"Cold open with the {packaging_angle} hook — no setup, straight to the point.",
        "overlay": hook[:60] if hook else "Hook text here",
        "priority": "critical",
    })

    if duration <= 10:
        # Very short clip — just hook + payoff
        beats.append({
            "beat": "payoff",
            "start_seconds": 3,
            "end_seconds": duration,
            "description": "Immediate payoff — no filler.",
            "overlay": None,
            "priority": "high",
        })
        return beats

    # Beat 2: Setup / context (seconds 3–40% of duration)
    setup_end = max(int(duration * 0.4), 5)
    beats.append({
        "beat": "setup",
        "start_seconds": 3,
        "end_seconds": setup_end,
        "description": _setup_description(packaging_angle, primary_trigger),
        "overlay": None,
        "priority": "medium",
    })

    # Beat 3: Core content / payoff (40%–80% of duration)
    payoff_end = max(int(duration * 0.8), setup_end + 3)
    beats.append({
        "beat": "payoff",
        "start_seconds": setup_end,
        "end_seconds": payoff_end,
        "description": _payoff_description(packaging_angle, transcript_excerpt),
        "overlay": None,
        "priority": "critical",
    })

    # Beat 4: CTA (last 20% or last 5 seconds, whichever is smaller)
    cta_start = max(payoff_end, duration - 5)
    beats.append({
        "beat": "cta",
        "start_seconds": cta_start,
        "end_seconds": duration,
        "description": "Close with the CTA — comment bait, save prompt, or follow ask.",
        "overlay": None,
        "priority": "high",
    })

    return beats


def _setup_description(packaging_angle: str, primary_trigger: str) -> str:
    descriptions = {
        "shock": "Brief context that makes the reveal land harder.",
        "story": "Set the scene — who, what, when — in as few words as possible.",
        "curiosity": "Deepen the open loop without giving away the answer yet.",
        "controversy": "State the contrarian position clearly before the evidence.",
        "value": "Frame the problem or question the viewer already has.",
    }
    return descriptions.get(packaging_angle, f"Build context for the {primary_trigger} payoff.")


def _payoff_description(packaging_angle: str, transcript_excerpt: str | None) -> str:
    focus = _compact_phrase(transcript_excerpt or "")
    descriptions = {
        "shock": f"Deliver the {focus} reveal — this is the moment the clip exists for.",
        "story": f"Land the {focus} turning point — the emotional payoff of the narrative.",
        "curiosity": f"Answer the open loop with the {focus} insight — make it feel earned.",
        "controversy": f"Present the {focus} evidence — make the contrarian case undeniable.",
        "value": f"Deliver the {focus} takeaway — the actionable insight the viewer came for.",
    }
    return descriptions.get(packaging_angle, f"Core {focus} content — the reason this clip exists.")


# ---------------------------------------------------------------------------
# Platform-Aware Output Hints
# ---------------------------------------------------------------------------

def generate_platform_output_hints(
    *,
    target_platform: str,
    packaging_angle: str,
    category: str = "",
    duration_seconds: int | None = None,
    has_transcript: bool = False,
) -> dict:
    """
    Returns platform-specific output hints for the creator.
    """
    profile = _resolve_platform_profile(target_platform)
    ideal_min, ideal_max = profile["ideal_duration_range"]
    duration = duration_seconds or 0

    duration_status = "unknown"
    duration_advice = ""
    if duration > 0:
        if duration < ideal_min:
            duration_status = "short"
            duration_advice = f"At {duration}s this clip is shorter than the ideal {ideal_min}–{ideal_max}s range for {profile['label']}. Consider extending the window slightly."
        elif duration > ideal_max:
            duration_status = "long"
            duration_advice = f"At {duration}s this clip exceeds the ideal {ideal_min}–{ideal_max}s range for {profile['label']}. Trim to the core payoff for better retention."
        else:
            duration_status = "ideal"
            duration_advice = f"At {duration}s this clip is in the ideal range for {profile['label']}."

    return {
        "platform": profile["label"],
        "aspect_ratio": profile["aspect_ratio"],
        "resolution": profile["export_hints"]["resolution"],
        "fps": profile["export_hints"]["fps"],
        "bitrate": profile["export_hints"]["bitrate"],
        "caption_style": profile["caption_style"],
        "caption_max_chars": profile["caption_max_chars"],
        "overlay_style": profile["overlay_style"],
        "hook_position": profile["hook_position"],
        "cta_position": profile["cta_position"],
        "duration_status": duration_status,
        "duration_advice": duration_advice,
        "creator_tips": profile["creator_tips"],
        "has_captions": has_transcript,
        "caption_recommendation": (
            "Captions are available from transcript — enable for accessibility and retention."
            if has_transcript
            else "No transcript available — consider adding manual captions for better reach."
        ),
    }


# ---------------------------------------------------------------------------
# Creator-Readiness Scoring
# ---------------------------------------------------------------------------

def score_creator_readiness(
    *,
    clip_id: str,
    has_rendered_media: bool,
    has_transcript: bool,
    has_hook: bool,
    has_caption: bool,
    has_cta: bool,
    has_thumbnail_text: bool,
    has_hook_variants: bool,
    has_caption_variants: bool,
    duration_seconds: int | None,
    target_platform: str,
    packaging_angle: str,
) -> dict:
    """
    Returns a creator-readiness score (0–100) and a breakdown of what's ready.
    """
    profile = _resolve_platform_profile(target_platform)
    ideal_min, ideal_max = profile["ideal_duration_range"]

    checks: list[dict] = []
    total_weight = 0
    earned_weight = 0

    def add_check(name: str, passed: bool, weight: int, tip: str) -> None:
        nonlocal total_weight, earned_weight
        total_weight += weight
        if passed:
            earned_weight += weight
        checks.append({"check": name, "passed": passed, "weight": weight, "tip": tip if not passed else ""})

    add_check("rendered_media", has_rendered_media, 25, "Render the clip to get a playable preview.")
    add_check("hook_present", has_hook, 15, "Add a hook to grab attention in the first 2 seconds.")
    add_check("caption_present", has_caption, 10, "Add a caption for platform display.")
    add_check("cta_present", has_cta, 10, "Add a CTA to drive engagement at the end.")
    add_check("thumbnail_text", has_thumbnail_text, 8, "Add thumbnail text for scroll-stopping visuals.")
    add_check("transcript_available", has_transcript, 10, "Transcript enables caption overlays and better scoring.")
    add_check("hook_variants", has_hook_variants, 7, "Add hook variants to A/B test your opening.")
    add_check("caption_variants", has_caption_variants, 7, "Add caption variants for multi-platform posting.")

    # Duration check
    duration_ok = duration_seconds is not None and ideal_min <= duration_seconds <= ideal_max
    add_check(
        "ideal_duration",
        duration_ok,
        8,
        f"Trim to {ideal_min}–{ideal_max}s for best performance on {profile['label']}.",
    )

    score = int(round((earned_weight / max(total_weight, 1)) * 100))

    if score >= 85:
        readiness_label = "Creator-ready"
        readiness_tip = "This clip is fully packaged and ready to post."
    elif score >= 65:
        readiness_label = "Nearly ready"
        readiness_tip = "A few small additions will make this clip post-ready."
    elif score >= 40:
        readiness_label = "Needs work"
        readiness_tip = "Complete the missing elements before posting."
    else:
        readiness_label = "Draft"
        readiness_tip = "This clip needs significant packaging before it's ready to post."

    missing = [c["tip"] for c in checks if not c["passed"] and c["tip"]]

    return {
        "clip_id": clip_id,
        "score": score,
        "label": readiness_label,
        "tip": readiness_tip,
        "checks": checks,
        "missing_elements": missing,
        "platform": profile["label"],
    }


# ---------------------------------------------------------------------------
# Output Bundle Logic
# ---------------------------------------------------------------------------

def build_output_bundle(
    *,
    clip_id: str,
    title: str,
    hook: str,
    caption: str,
    cta_suggestion: str,
    packaging_angle: str,
    target_platform: str,
    duration_seconds: int | None,
    transcript_excerpt: str | None,
    has_rendered_media: bool,
    category: str = "",
    primary_trigger: str = "curiosity",
    caption_style: str = "",
    hook_variants: list[str] | None = None,
    caption_variants: dict[str, str] | None = None,
    thumbnail_text: str = "",
) -> dict:
    """
    Assembles the full output bundle for a clip, combining all output engine signals.
    """
    caption_structure = enrich_caption_structure(
        caption=caption,
        hook=hook,
        cta_suggestion=cta_suggestion,
        target_platform=target_platform,
        packaging_angle=packaging_angle,
        caption_style=caption_style,
    )

    edit_plan = generate_edit_plan(
        clip_id=clip_id,
        title=title,
        hook=hook,
        packaging_angle=packaging_angle,
        target_platform=target_platform,
        duration_seconds=duration_seconds,
        transcript_excerpt=transcript_excerpt,
        category=category,
        primary_trigger=primary_trigger,
    )

    platform_hints = generate_platform_output_hints(
        target_platform=target_platform,
        packaging_angle=packaging_angle,
        category=category,
        duration_seconds=duration_seconds,
        has_transcript=bool(transcript_excerpt),
    )

    readiness = score_creator_readiness(
        clip_id=clip_id,
        has_rendered_media=has_rendered_media,
        has_transcript=bool(transcript_excerpt),
        has_hook=bool(hook),
        has_caption=bool(caption),
        has_cta=bool(cta_suggestion),
        has_thumbnail_text=bool(thumbnail_text),
        has_hook_variants=bool(hook_variants),
        has_caption_variants=bool(caption_variants),
        duration_seconds=duration_seconds,
        target_platform=target_platform,
        packaging_angle=packaging_angle,
    )

    return {
        "caption_structure": caption_structure,
        "edit_plan": edit_plan,
        "platform_hints": platform_hints,
        "creator_readiness": readiness,
    }


# ---------------------------------------------------------------------------
# Export Metadata Generation
# ---------------------------------------------------------------------------

def generate_export_metadata(
    *,
    clip_id: str,
    title: str,
    target_platform: str,
    packaging_angle: str,
    category: str = "",
    duration_seconds: int | None = None,
    request_id: str = "",
    rank: int = 1,
) -> dict:
    """
    Returns export metadata including creator-ready filename and platform tags.
    """
    profile = _resolve_platform_profile(target_platform)
    platform_slug = _slugify(profile["label"])
    title_slug = _slugify(title)[:40]
    angle_slug = packaging_angle[:12]

    filename = f"{title_slug}_{platform_slug}_{angle_slug}_rank{rank}.mp4"
    if request_id:
        filename = f"{request_id[:8]}_{filename}"

    return {
        "clip_id": clip_id,
        "filename": filename,
        "platform": profile["label"],
        "aspect_ratio": profile["aspect_ratio"],
        "resolution": profile["export_hints"]["resolution"],
        "fps": profile["export_hints"]["fps"],
        "bitrate": profile["export_hints"]["bitrate"],
        "duration_seconds": duration_seconds,
        "packaging_angle": packaging_angle,
        "category": category,
        "rank": rank,
        "tags": _build_export_tags(
            platform=profile["label"],
            packaging_angle=packaging_angle,
            category=category,
        ),
    }


def _build_export_tags(*, platform: str, packaging_angle: str, category: str) -> list[str]:
    tags = [platform.lower().replace(" ", "_"), packaging_angle]
    if category:
        tags.append(category.lower().replace(" / ", "_").replace(" ", "_"))
    return tags


# ---------------------------------------------------------------------------
# Enrichment Entry Point (called from video_service)
# ---------------------------------------------------------------------------

def enrich_exported_clip(
    *,
    clip: Any,
    target_platform: str,
    request_id: str = "",
) -> Any:
    """
    Enriches an exported clip with output engine metadata.
    Returns a new clip instance with output_enrichment populated.
    """
    packaging_angle = getattr(clip, "packaging_angle", None) or "value"
    category = getattr(clip, "category", "") or ""
    duration_seconds = getattr(clip, "duration", None)
    transcript_excerpt = getattr(clip, "transcript_excerpt", None)
    hook = getattr(clip, "hook", "") or ""
    caption = getattr(clip, "caption", "") or ""
    cta_suggestion = getattr(clip, "cta_suggestion", "") or ""
    caption_style = getattr(clip, "caption_style", "") or ""
    hook_variants = getattr(clip, "hook_variants", None)
    caption_variants = getattr(clip, "caption_variants", None)
    thumbnail_text = getattr(clip, "thumbnail_text", "") or ""
    title = getattr(clip, "title", "") or ""
    clip_id = getattr(clip, "id", "") or ""
    rank = getattr(clip, "rank", 1) or 1
    has_rendered = bool(
        getattr(clip, "edited_clip_url", None)
        or getattr(clip, "clip_url", None)
        or getattr(clip, "raw_clip_url", None)
    )

    # Detect primary trigger from packaging intelligence if available
    packaging_intel = getattr(clip, "packaging_intelligence", None) or {}
    primary_trigger = "curiosity"
    if isinstance(packaging_intel, dict):
        primary_trigger = packaging_intel.get("primary_trigger", "curiosity").lower()

    output_bundle = build_output_bundle(
        clip_id=clip_id,
        title=title,
        hook=hook,
        caption=caption,
        cta_suggestion=cta_suggestion,
        packaging_angle=packaging_angle,
        target_platform=target_platform,
        duration_seconds=duration_seconds,
        transcript_excerpt=transcript_excerpt,
        has_rendered_media=has_rendered,
        category=category,
        primary_trigger=primary_trigger,
        caption_style=caption_style,
        hook_variants=hook_variants,
        caption_variants=caption_variants,
        thumbnail_text=thumbnail_text,
    )

    export_meta = generate_export_metadata(
        clip_id=clip_id,
        title=title,
        target_platform=target_platform,
        packaging_angle=packaging_angle,
        category=category,
        duration_seconds=duration_seconds,
        request_id=request_id,
        rank=rank,
    )

    output_enrichment = {
        **output_bundle,
        "export_metadata": export_meta,
    }

    return clip.model_copy(update={"output_enrichment": output_enrichment})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_platform_profile(target_platform: str) -> dict:
    normalized = target_platform.lower()
    if "tiktok" in normalized:
        return PLATFORM_OUTPUT_PROFILES["tiktok"]
    if "instagram" in normalized or "reels" in normalized:
        return PLATFORM_OUTPUT_PROFILES["instagram"]
    if "youtube" in normalized or "shorts" in normalized:
        return PLATFORM_OUTPUT_PROFILES["youtube"]
    if "facebook" in normalized:
        return PLATFORM_OUTPUT_PROFILES["facebook"]
    return _DEFAULT_PLATFORM_PROFILE


def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "_", value)
    return value.strip("_")


def _compact_phrase(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9']+", value)
    return " ".join(words[:3]).lower() if words else "this clip"
