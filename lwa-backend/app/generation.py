from __future__ import annotations

import json
import logging
import re
from typing import List, Optional

import httpx
from openai import OpenAI

from .config import Settings
from .mock_data import build_mock_clips
from .processor import ClipSeed, SourceContext
from .schemas import ClipResult, TrendItem

logger = logging.getLogger("uvicorn.error")


def determine_provider(settings: Settings) -> str:
    provider = settings.ai_provider.lower()

    if provider == "auto":
        if settings.openai_api_key:
            return "openai"
        if settings.ollama_base_url:
            return "ollama"
        return "heuristic"

    return provider


async def generate_clips(
    *,
    settings: Settings,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> tuple[List[ClipResult], str]:
    provider = determine_provider(settings)

    if provider == "openai" and settings.openai_api_key:
        try:
            clips, used_provider = await generate_with_openai(
                settings=settings,
                video_url=video_url,
                target_platform=target_platform,
                selected_trend=selected_trend,
                content_angle=content_angle,
                trend_context=trend_context,
                source_context=source_context,
            )
            logger.info("clip_intelligence_mode mode=%s clips_scored=%s", used_provider, len(clips))
            return clips, used_provider
        except Exception as error:
            logger.warning("clip_intelligence_fallback mode=openai reason=%s", error)

    if provider == "ollama":
        try:
            clips, used_provider = await generate_with_ollama(
                settings=settings,
                video_url=video_url,
                target_platform=target_platform,
                selected_trend=selected_trend,
                content_angle=content_angle,
                trend_context=trend_context,
                source_context=source_context,
            )
            logger.info("clip_intelligence_mode mode=%s clips_scored=%s", used_provider, len(clips))
            return clips, used_provider
        except Exception as error:
            logger.warning("clip_intelligence_fallback mode=ollama reason=%s", error)

    clips = build_mock_clips(
        video_url=video_url,
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        trend_context=trend_context,
        clip_urls=[seed.clip_url for seed in source_context.clip_seeds] if source_context else None,
        start_end_pairs=[(seed.start_time, seed.end_time) for seed in source_context.clip_seeds] if source_context else None,
        source_title=source_context.title if source_context else None,
        transcript_excerpts=[seed.transcript_excerpt for seed in source_context.clip_seeds] if source_context else None,
    )
    logger.info("clip_intelligence_mode mode=fallback clips_scored=%s", len(clips))
    logger.info("clip_ranking_complete mode=fallback ranked=%s", len(clips))
    return clips, "fallback"


async def generate_with_ollama(
    *,
    settings: Settings,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> tuple[List[ClipResult], str]:
    prompt = build_generation_prompt(video_url, target_platform, selected_trend, content_angle, trend_context, source_context)

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
        )
        response.raise_for_status()
        payload = response.json()
        raw = payload.get("response", "{}")

    return parse_generated_clips(
        raw,
        video_url,
        target_platform,
        selected_trend,
        content_angle,
        trend_context,
        source_context,
    ), "ollama"


async def generate_with_openai(
    *,
    settings: Settings,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> tuple[List[ClipResult], str]:
    prompt = build_generation_prompt(video_url, target_platform, selected_trend, content_angle, trend_context, source_context)
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        input=prompt,
    )
    raw = response.output_text
    return parse_generated_clips(
        raw,
        video_url,
        target_platform,
        selected_trend,
        content_angle,
        trend_context,
        source_context,
    ), "openai"


def parse_generated_clips(
    raw: str,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> List[ClipResult]:
    try:
        payload = json.loads(raw)
        clips = payload.get("clips", [])
    except Exception as error:
        logger.warning("clip_intelligence_fallback mode=model_response reason=%s", error)
        clips = []

    if not clips:
        logger.warning("clip_intelligence_fallback mode=model_response reason=empty_clip_payload")
        return build_mock_clips(
            video_url=video_url,
            target_platform=target_platform,
            selected_trend=selected_trend,
            content_angle=content_angle,
            trend_context=trend_context,
            clip_urls=[seed.clip_url for seed in source_context.clip_seeds] if source_context else None,
            start_end_pairs=[(seed.start_time, seed.end_time) for seed in source_context.clip_seeds] if source_context else None,
            source_title=source_context.title if source_context else None,
            transcript_excerpts=[seed.transcript_excerpt for seed in source_context.clip_seeds] if source_context else None,
        )

    normalized: list[ClipResult] = []
    for index, clip in enumerate(clips[:3], start=1):
        seed = source_context.clip_seeds[index - 1] if source_context and len(source_context.clip_seeds) >= index else None
        hook = str(clip.get("hook", "Lead with a strong hook."))
        title = str(clip.get("title", f"{target_platform} Clip {index}"))
        caption = str(clip.get("caption", "Use a short value-focused caption."))
        score = clamp_score(clip.get("score"), fallback=max(70, 95 - (index * 4)))
        confidence = clamp_confidence(
            clip.get("confidence"),
            fallback=max(min(score / 100.0, 0.99), 0.55),
        )
        packaging_angle = parse_packaging_angle(
            clip.get("packaging_angle"),
            title=title,
            hook=hook,
            transcript_excerpt=seed.transcript_excerpt if seed else clip.get("transcript_excerpt"),
        )
        platform_fit = str_or_fallback(
            clip.get("platform_fit"),
            default_platform_fit(target_platform=target_platform, packaging_angle=packaging_angle),
        )
        reason = str_or_fallback(
            clip.get("reason"),
            default_reason(
                title=title,
                target_platform=target_platform,
                packaging_angle=packaging_angle,
            ),
        )
        normalized.append(
            ClipResult(
                id=seed.id if seed else f"clip_{index:03d}",
                title=title,
                hook=hook,
                caption=caption,
                start_time=seed.start_time if seed else str(clip.get("start_time", "00:00")),
                end_time=seed.end_time if seed else str(clip.get("end_time", "00:15")),
                score=score,
                confidence=confidence,
                reason=reason,
                format=str(clip.get("format", seed.format if seed else "Trend First")),
                clip_url=seed.clip_url if seed else clip.get("clip_url"),
                raw_clip_url=seed.raw_clip_url if seed else clip.get("raw_clip_url"),
                preview_image_url=seed.preview_image_url if seed else clip.get("preview_image_url"),
                transcript_excerpt=seed.transcript_excerpt if seed else clip.get("transcript_excerpt"),
                edit_profile=clip.get("edit_profile"),
                aspect_ratio=clip.get("aspect_ratio"),
                why_this_matters=str_or_fallback(
                    clip.get("why_this_matters"),
                    reason,
                ),
                confidence_score=clamp_score(
                    clip.get("confidence_score"),
                    fallback=max(int(round(confidence * 100)), 55),
                ),
                thumbnail_text=str_or_fallback(
                    clip.get("thumbnail_text"),
                    default_thumbnail_text(title=title, hook=hook),
                ),
                cta_suggestion=str_or_fallback(
                    clip.get("cta_suggestion"),
                    default_cta_suggestion(target_platform=target_platform, post_rank=index),
                ),
                hook_variants=parse_hook_variants(
                    clip.get("hook_variants"),
                    hook=hook,
                    title=title,
                    selected_trend=selected_trend,
                    target_platform=target_platform,
                    packaging_angle=packaging_angle,
                ),
                caption_style=str_or_fallback(
                    clip.get("caption_style"),
                    default_caption_style(target_platform),
                ),
                platform_fit=platform_fit,
                packaging_angle=packaging_angle,
            )
        )

    ranked = sorted(
        normalized,
        key=lambda current: (-(current.score or 0), -(current.confidence or 0.0), current.start_time),
    )
    finalized: list[ClipResult] = []
    for rank, clip in enumerate(ranked, start=1):
        finalized.append(
            clip.model_copy(
                update={
                    "rank": rank,
                    "post_rank": rank,
                    "best_post_order": rank,
                    "cta_suggestion": clip.cta_suggestion or default_cta_suggestion(target_platform=target_platform, post_rank=rank),
                    "why_this_matters": clip.why_this_matters or default_why_this_matters(
                        title=clip.title,
                        target_platform=target_platform,
                        post_rank=rank,
                    ),
                }
            )
        )

    logger.info("clip_scoring_complete mode=ai clips_scored=%s", len(finalized))
    logger.info("clip_ranking_complete ranked=%s", len(finalized))
    return finalized


def build_generation_prompt(
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> str:
    trend_lines = "\n".join(f"- {item.source}: {item.title} ({item.detail})" for item in trend_context[:5])
    source_title = source_context.title if source_context else "Unknown source"
    source_description = source_context.description[:500] if source_context and source_context.description else "No description available."
    source_duration = source_context.duration_seconds if source_context and source_context.duration_seconds else "unknown"
    seed_lines = build_seed_lines(source_context.clip_seeds if source_context else None)
    return f"""
Generate exactly 3 short-form video clip ideas as JSON.

Video URL: {video_url}
Source title: {source_title}
Source duration seconds: {source_duration}
Source description: {source_description}
Target platform: {target_platform}
Selected trend: {selected_trend or "none"}
Preferred packaging angle: {content_angle or "none"}
Trend context:
{trend_lines}
Clip windows:
{seed_lines}

Return valid JSON in this shape:
{{
  "clips": [
    {{
      "title": "...",
      "hook": "...",
      "hook_variants": ["...", "...", "..."],
      "caption": "...",
      "caption_style": "...",
      "reason": "...",
      "thumbnail_text": "...",
      "cta_suggestion": "...",
      "score": 90,
      "confidence": 0.86,
      "platform_fit": "...",
      "packaging_angle": "value",
      "format": "Hook First"
    }}
  ]
}}

Rules:
- Evaluate each clip using the transcript excerpt, timing, and target platform.
- If preferred packaging angle is present, bias the response toward it unless the clip clearly fits a stronger angle.
- reason must explain in one short sentence why the clip will work.
- thumbnail_text must be 2 to 5 words and punchy.
- hook_variants must contain exactly 3 alternate hook options.
- packaging_angle must be one of: shock, story, value, curiosity, controversy.
- confidence must be a float between 0.0 and 1.0.
""".strip()


def build_seed_lines(clip_seeds: Optional[List[ClipSeed]]) -> str:
    if not clip_seeds:
        return "- no precomputed clip windows"
    return "\n".join(
        (
            f"- {seed.id}: {seed.start_time} to {seed.end_time} ({seed.format})"
            + (f" | transcript: {seed.transcript_excerpt}" if seed.transcript_excerpt else "")
        )
        for seed in clip_seeds
    )


def parse_int(value: object, fallback: int) -> int:
    try:
        return int(value)
    except Exception:
        return fallback


def clamp_score(value: object, fallback: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        parsed = fallback
    return max(0, min(parsed, 100))


def str_or_fallback(value: object, fallback: str) -> str:
    if isinstance(value, str):
        normalized = value.strip()
        if normalized:
            return normalized
    return fallback


def parse_hook_variants(
    value: object,
    *,
    hook: str,
    title: str,
    selected_trend: Optional[str],
    target_platform: str,
    packaging_angle: str,
) -> List[str]:
    if isinstance(value, list):
        variants = [str(item).strip() for item in value if str(item).strip()]
        if variants:
            return variants[:3]
    return default_hook_variants(
        hook=hook,
        title=title,
        selected_trend=selected_trend,
        target_platform=target_platform,
        packaging_angle=packaging_angle,
    )


def default_hook_variants(
    *,
    hook: str,
    title: str,
    selected_trend: Optional[str],
    target_platform: str,
    packaging_angle: str,
) -> List[str]:
    focus = selected_trend or compact_phrase(title or hook)
    platform_label = target_platform or "short-form"
    angle = packaging_angle.replace("-", " ")
    return [
        f"Why {focus} is the highest-upside {platform_label} {angle} angle right now.",
        f"The {focus} moment most creators skip is the one driving this clip.",
        f"If you post one {angle} clip for {platform_label}, start with this one.",
    ]


def default_why_this_matters(*, title: str, target_platform: str, post_rank: int) -> str:
    if post_rank == 1:
        return f"This is the first-post candidate because {title.lower()} lands fast and needs the least setup for {target_platform} viewers."
    if post_rank == 2:
        return f"This works as the second post because it deepens the angle once the opening concept has already earned attention on {target_platform}."
    return f"This is the closer clip: use it after the first two to convert attention into comments, saves, or follow-through on {target_platform}."


def default_reason(*, title: str, target_platform: str, packaging_angle: str) -> str:
    return f"{title} works for {target_platform} because the {packaging_angle} framing is easy to understand and fast to react to."


def default_thumbnail_text(*, title: str, hook: str) -> str:
    source = hook if len(hook.strip()) >= len(title.strip()) else title
    words = [
        word
        for word in re.findall(r"[A-Za-z0-9']+", source)
        if word.lower() not in {"the", "and", "that", "with", "this", "your", "from", "into"}
    ]
    if not words:
        return "Best Clip"

    return " ".join(words[:4]).title()


def default_cta_suggestion(*, target_platform: str, post_rank: int) -> str:
    platform = target_platform.lower()
    if post_rank == 1:
        return (
            "End by asking viewers if they want the full breakdown next."
            if platform == "youtube"
            else "End by asking viewers if they want part two."
        )
    if platform == "instagram":
        return "Close by asking people to save this and send it to a creator friend."
    if platform == "facebook":
        return "Close by inviting people to comment with the part they agreed with most."
    return "Close by asking viewers which angle they want you to break down next."


def default_caption_style(target_platform: str) -> str:
    normalized = target_platform.lower()
    if normalized == "tiktok":
        return "Punchy proof-first"
    if normalized == "instagram":
        return "Polished emotional"
    if normalized == "youtube":
        return "Clarity-led payoff"
    if normalized == "facebook":
        return "Story-first social"
    return "Short-form native"


def default_platform_fit(*, target_platform: str, packaging_angle: str) -> str:
    normalized = target_platform.lower()
    if normalized == "tiktok":
        return f"TikTok-friendly pacing with a {packaging_angle} opening and fast payoff."
    if normalized == "instagram":
        return f"Reels-ready packaging with cleaner framing and a {packaging_angle} angle."
    if normalized == "youtube":
        return f"Shorts-ready structure with context-light setup and a {packaging_angle} hook."
    if normalized == "facebook":
        return f"Facebook-native framing that makes the {packaging_angle} point easier to comment on."
    return f"Short-form native packaging built around a {packaging_angle} angle."


def parse_packaging_angle(
    value: object,
    *,
    title: str,
    hook: str,
    transcript_excerpt: object,
) -> str:
    aliases = {
        "storytelling": "story",
        "educational": "value",
        "contrarian": "controversy",
        "emotional": "story",
    }
    allowed = {"shock", "story", "value", "curiosity", "controversy"}
    if isinstance(value, str):
        normalized = value.strip().lower()
        normalized = aliases.get(normalized, normalized)
        if normalized in allowed:
            return normalized
    return default_packaging_angle(title=title, hook=hook, transcript_excerpt=transcript_excerpt)


def default_packaging_angle(*, title: str, hook: str, transcript_excerpt: object) -> str:
    content = " ".join(
        [
            title.lower(),
            hook.lower(),
            str(transcript_excerpt or "").lower(),
        ]
    )
    if any(keyword in content for keyword in {"wrong", "never", "nobody", "skip", "myth"}):
        return "controversy"
    if any(keyword in content for keyword in {"story", "moment", "started", "then", "when"}):
        return "story"
    if any(keyword in content for keyword in {"feel", "care", "pain", "afraid", "love", "hate"}):
        return "story"
    if any(keyword in content for keyword in {"stop", "crazy", "wild", "shocking", "secret"}):
        return "shock"
    if any(keyword in content for keyword in {"why", "how", "before", "exact", "mistake"}):
        return "curiosity"
    return "value"


def clamp_confidence(value: object, fallback: float) -> float:
    try:
        parsed = float(value)
    except Exception:
        parsed = fallback
    return max(0.0, min(parsed, 1.0))


def compact_phrase(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9']+", value)
    if not words:
        return "this angle"
    return " ".join(words[:3]).lower()
