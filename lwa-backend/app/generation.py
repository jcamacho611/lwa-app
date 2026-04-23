from __future__ import annotations

import json
import logging
import re
from typing import List, Optional

import httpx
from openai import OpenAI

from .config import Settings
from .mock_data import build_mock_clips
from .processor import ClipSeed, SourceContext, score_excerpt
from .schemas import ClipResult, TrendItem
from .services.anthropic_service import (
    anthropic_available,
    generate_clip_packaging_with_opus,
    generate_clip_packaging_with_sonnet,
)

logger = logging.getLogger("uvicorn.error")


def determine_provider(settings: Settings) -> str:
    provider = settings.ai_provider.lower()

    if provider == "auto":
        if anthropic_available(settings):
            return "anthropic"
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
    premium_reasoning: bool = False,
) -> tuple[List[ClipResult], str]:
    provider = determine_provider(settings)

    if provider == "anthropic":
        try:
            clips, used_provider = await generate_with_anthropic(
                settings=settings,
                video_url=video_url,
                target_platform=target_platform,
                selected_trend=selected_trend,
                content_angle=content_angle,
                trend_context=trend_context,
                source_context=source_context,
                premium_reasoning=premium_reasoning,
            )
            logger.info("clip_intelligence_mode mode=%s clips_scored=%s", used_provider, len(clips))
            return clips, used_provider
        except Exception as error:
            logger.warning("clip_intelligence_fallback mode=anthropic reason=%s", error)

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

    clips = build_fallback_clips(
        video_url=video_url,
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        trend_context=trend_context,
        source_context=source_context,
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


async def generate_with_anthropic(
    *,
    settings: Settings,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
    premium_reasoning: bool = False,
) -> tuple[List[ClipResult], str]:
    prompt = build_generation_prompt(
        video_url,
        target_platform,
        selected_trend,
        content_angle,
        trend_context,
        source_context,
    )
    if premium_reasoning:
        raw = generate_clip_packaging_with_opus(settings=settings, prompt=prompt)
        used_provider = "anthropic-opus"
    else:
        raw = generate_clip_packaging_with_sonnet(settings=settings, prompt=prompt)
        used_provider = "anthropic-sonnet"

    return parse_generated_clips(
        raw,
        video_url,
        target_platform,
        selected_trend,
        content_angle,
        trend_context,
        source_context,
    ), used_provider


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
        return build_fallback_clips(
            video_url=video_url,
            target_platform=target_platform,
            selected_trend=selected_trend,
            content_angle=content_angle,
            trend_context=trend_context,
            source_context=source_context,
        )

    normalized: list[ClipResult] = []
    for index, clip in enumerate(clips, start=1):
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
                    default_why_this_matters(
                        title=title,
                        target_platform=target_platform,
                        post_rank=index,
                        packaging_angle=packaging_angle,
                        transcript_excerpt=seed.transcript_excerpt if seed else clip.get("transcript_excerpt"),
                    ),
                ),
                confidence_score=clamp_score(
                    clip.get("confidence_score"),
                    fallback=fallback_confidence_score(
                        score=score,
                        confidence=confidence,
                        transcript_excerpt=seed.transcript_excerpt if seed else clip.get("transcript_excerpt"),
                        source_context=source_context,
                    ),
                ),
                thumbnail_text=str_or_fallback(
                    clip.get("thumbnail_text"),
                    default_thumbnail_text(
                        title=title,
                        hook=hook,
                        packaging_angle=packaging_angle,
                        target_platform=target_platform,
                        post_rank=index,
                    ),
                ),
                cta_suggestion=str_or_fallback(
                    clip.get("cta_suggestion"),
                    default_cta_suggestion(
                        target_platform=target_platform,
                        post_rank=index,
                        packaging_angle=packaging_angle,
                    ),
                ),
                post_rank=max(parse_int(clip.get("post_rank"), fallback=index), 1),
                best_post_order=max(parse_int(clip.get("post_rank"), fallback=index), 1),
                hook_variants=parse_hook_variants(
                    clip.get("hook_variants"),
                    hook=hook,
                    title=title,
                    selected_trend=selected_trend,
                    target_platform=target_platform,
                    packaging_angle=packaging_angle,
                    transcript_excerpt=seed.transcript_excerpt if seed else clip.get("transcript_excerpt"),
                ),
                caption_variants=parse_caption_variants(
                    clip.get("caption_variants"),
                    caption=caption,
                    target_platform=target_platform,
                    packaging_angle=packaging_angle,
                ),
                caption_style=str_or_fallback(
                    clip.get("caption_style"),
                    default_caption_style(target_platform, packaging_angle=packaging_angle),
                ),
                platform_fit=platform_fit,
                packaging_angle=packaging_angle,
            )
        )

    normalized = supplement_source_grounded_clips(
        normalized,
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        trend_context=trend_context,
        source_context=source_context,
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
                    "post_rank": clip.post_rank or rank,
                    "best_post_order": clip.best_post_order or clip.post_rank or rank,
                    "cta_suggestion": clip.cta_suggestion
                    or default_cta_suggestion(
                        target_platform=target_platform,
                        post_rank=clip.post_rank or rank,
                        packaging_angle=clip.packaging_angle,
                    ),
                    "why_this_matters": clip.why_this_matters or default_why_this_matters(
                        title=clip.title,
                        target_platform=target_platform,
                        post_rank=clip.post_rank or rank,
                        packaging_angle=clip.packaging_angle,
                        transcript_excerpt=clip.transcript_excerpt,
                    ),
                }
            )
        )

    logger.info("clip_scoring_complete mode=ai clips_scored=%s", len(finalized))
    logger.info("clip_ranking_complete ranked=%s", len(finalized))
    return finalized


def supplement_source_grounded_clips(
    clips: List[ClipResult],
    *,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext],
) -> List[ClipResult]:
    if not source_context or not source_context.clip_seeds:
        return clips

    desired_count = desired_clip_count_for_source(source_context)
    if len(clips) >= desired_count:
        return clips

    existing_ids = {clip.id for clip in clips}
    supplemented = list(clips)
    for candidate in build_source_grounded_fallback_clips(
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        trend_context=trend_context,
        source_context=source_context,
    ):
        if candidate.id in existing_ids:
            continue
        supplemented.append(candidate)
        existing_ids.add(candidate.id)
        if len(supplemented) >= desired_count:
            break

    return supplemented


def build_fallback_clips(
    *,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> List[ClipResult]:
    if source_context and source_context.clip_seeds:
        return build_source_grounded_fallback_clips(
            target_platform=target_platform,
            selected_trend=selected_trend,
            content_angle=content_angle,
            trend_context=trend_context,
            source_context=source_context,
        )

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


def build_source_grounded_fallback_clips(
    *,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    trend_context: List[TrendItem],
    source_context: SourceContext,
) -> List[ClipResult]:
    preferred_angle = (content_angle or "").strip().lower()
    lead_trend = selected_trend or (trend_context[0].title if trend_context else None)
    normalized: list[ClipResult] = []

    for index, seed in enumerate(source_context.clip_seeds, start=1):
        source_phrase = str_or_fallback(
            seed.transcript_excerpt,
            source_context.visual_summary or source_context.description or source_context.title,
        )
        packaging_angle = preferred_angle if preferred_angle in {"shock", "story", "value", "curiosity", "controversy"} else default_packaging_angle(
            title=source_context.title or target_platform,
            hook=source_phrase,
            transcript_excerpt=source_phrase,
        )
        title_focus = default_thumbnail_text(
            title=source_context.title or target_platform,
            hook=source_phrase,
            packaging_angle=packaging_angle,
            target_platform=target_platform,
            post_rank=index,
        )
        title = build_source_grounded_title(
            title_focus=title_focus,
            target_platform=target_platform,
            packaging_angle=packaging_angle,
            post_rank=index,
        )
        score = clamp_score(None, fallback=max(64, 95 - ((index - 1) * 3)))
        confidence = clamp_confidence(None, fallback=max(min(score / 100.0, 0.96), 0.58))
        hook = build_source_grounded_hook(
            source_phrase=source_phrase,
            packaging_angle=packaging_angle,
            target_platform=target_platform,
            lead_trend=lead_trend,
            post_rank=index,
        )
        caption = build_source_grounded_caption(
            source_phrase=source_phrase,
            target_platform=target_platform,
            source_context=source_context,
        )
        reason = build_source_grounded_reason(
            source_phrase=source_phrase,
            target_platform=target_platform,
            packaging_angle=packaging_angle,
            post_rank=index,
        )

        normalized.append(
            ClipResult(
                id=seed.id,
                title=title,
                hook=hook,
                caption=caption,
                start_time=seed.start_time,
                end_time=seed.end_time,
                score=score,
                virality_score=score,
                confidence=confidence,
                rank=index,
                reason=reason,
                format=seed.format or "Ranked cut",
                clip_url=seed.clip_url,
                raw_clip_url=seed.raw_clip_url,
                preview_image_url=seed.preview_image_url,
                transcript_excerpt=seed.transcript_excerpt,
                edit_profile="Source-grounded fallback",
                aspect_ratio="source",
                why_this_matters=default_why_this_matters(
                    title=title_focus,
                    target_platform=target_platform,
                    post_rank=index,
                    packaging_angle=packaging_angle,
                    transcript_excerpt=source_phrase,
                ),
                confidence_score=fallback_confidence_score(
                    score=score,
                    confidence=confidence,
                    transcript_excerpt=source_phrase,
                    source_context=source_context,
                ),
                thumbnail_text=default_thumbnail_text(
                    title=title,
                    hook=hook,
                    packaging_angle=packaging_angle,
                    target_platform=target_platform,
                    post_rank=index,
                ),
                cta_suggestion=default_cta_suggestion(
                    target_platform=target_platform,
                    post_rank=index,
                    packaging_angle=packaging_angle,
                ),
                post_rank=index,
                best_post_order=index,
                hook_variants=default_hook_variants(
                    hook=hook,
                    title=title,
                    selected_trend=lead_trend,
                    target_platform=target_platform,
                    packaging_angle=packaging_angle,
                    transcript_excerpt=source_phrase,
                ),
                caption_variants={
                    "viral": caption,
                    "story": f"{source_context.title or 'This source'} lands because the payoff shows up fast and the framing stays tight.",
                },
                caption_style=default_caption_style(target_platform, packaging_angle=packaging_angle),
                platform_fit=default_platform_fit(target_platform=target_platform, packaging_angle=packaging_angle),
                packaging_angle=packaging_angle,
                duration=seed.duration,
            )
        )

    logger.info("clip_intelligence_mode mode=source_grounded_fallback clips_scored=%s", len(normalized))
    return normalized


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
    source_type = source_context.source_type if source_context else "url"
    transcript_text = (source_context.transcript[:1800] if source_context and source_context.transcript else "No transcript available.")
    visual_summary = (source_context.visual_summary[:800] if source_context and source_context.visual_summary else "No visual summary available.")
    seed_lines = build_seed_lines(source_context.clip_seeds if source_context else None)
    desired_clip_count = desired_clip_count_for_source(source_context)
    return f"""
Generate exactly {desired_clip_count} short-form video clip ideas as JSON.

Video URL: {video_url}
Source type: {source_type}
Source title: {source_title}
Source duration seconds: {source_duration}
Source description: {source_description}
Transcript: {transcript_text}
Visual summary: {visual_summary}
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
      "why_this_matters": "...",
      "hook_variants": ["...", "...", "..."],
      "caption": "...",
      "caption_variants": {{
        "viral": "...",
        "story": "...",
        "educational": "...",
        "controversial": "..."
      }},
      "caption_style": "...",
      "reason": "...",
      "thumbnail_text": "...",
      "cta_suggestion": "...",
      "post_rank": 1,
      "score": 90,
      "confidence": 0.86,
      "platform_fit": "...",
      "packaging_angle": "value",
      "format": "Hook First"
    }}
  ]
}}

Rules:
- Evaluate each clip using the actual transcript excerpt or visual summary, timing, and target platform.
- Use the provided clip windows as the media boundaries; prefer tight starts and stop shortly after the payoff.
- If preferred packaging angle is present, bias the response toward it unless the clip clearly fits a stronger angle.
- reason must explain in one short sentence why the clip will work.
- why_this_matters must explain why this clip should be posted in the stack.
- post_rank must recommend where this clip should appear in the posting sequence.
- thumbnail_text must be 2 to 5 words and punchy.
- hook_variants must contain exactly 3 alternate hook options.
- caption_variants must include viral, story, educational, and controversial keys.
- packaging_angle must be one of: shock, story, value, curiosity, controversy.
- confidence must be a float between 0.0 and 1.0.
""".strip()


def desired_clip_count_for_source(source_context: Optional[SourceContext]) -> int:
    if not source_context or not source_context.clip_seeds:
        return 3
    return min(max(len(source_context.clip_seeds), 10), 16)


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


def build_source_grounded_hook(
    *,
    source_phrase: str,
    packaging_angle: str,
    target_platform: str,
    lead_trend: Optional[str],
    post_rank: int,
) -> str:
    focus = compact_phrase(source_phrase)
    trend = lead_trend or focus

    if packaging_angle == "controversy":
        return f"Most creators still frame {trend} the wrong way. This cut gets to the point fast."
    if packaging_angle == "story":
        return f"This is the moment {trend} actually turns into a clip worth posting."
    if packaging_angle == "shock":
        return f"Stop scrolling. This {target_platform} cut gets the payoff on screen immediately."
    if packaging_angle == "curiosity":
        return f"Here is the {trend} moment most people skip before the payoff hits."
    if post_rank == 1:
        return f"If you post one {target_platform} clip first, make it the {trend} cut."
    return f"This {target_platform} clip keeps the {trend} angle moving without extra setup."


def build_source_grounded_caption(
    *,
    source_phrase: str,
    target_platform: str,
    source_context: SourceContext,
) -> str:
    source_label = source_context.title or source_context.source_platform or "the source"
    summary = source_phrase.strip()
    if len(summary) > 180:
        summary = f"{summary[:177].rstrip()}..."
    return f"Pulled from {source_label} for {target_platform}: {summary}"


def build_source_grounded_reason(
    *,
    source_phrase: str,
    target_platform: str,
    packaging_angle: str,
    post_rank: int,
) -> str:
    focus = compact_phrase(source_phrase)
    if post_rank == 1:
        return f"This is the strongest opener because the {focus} payoff lands quickly with a clear {packaging_angle} frame for {target_platform}."
    return f"This works later in the stack because it keeps the {focus} angle moving with a cleaner {packaging_angle} follow-through for {target_platform}."


def build_source_grounded_title(
    *,
    title_focus: str,
    target_platform: str,
    packaging_angle: str,
    post_rank: int,
) -> str:
    platform = platform_display_name(target_platform)
    if post_rank == 1:
        return f"{title_focus}: Lead {platform} Cut"
    if packaging_angle == "curiosity":
        return f"{title_focus}: Curiosity Cut"
    if packaging_angle == "controversy":
        return f"{title_focus}: Tension Cut"
    if packaging_angle == "story":
        return f"{title_focus}: Payoff Cut"
    if packaging_angle == "shock":
        return f"{title_focus}: Interrupt Cut"
    return f"{title_focus}: Value Cut"


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
    transcript_excerpt: object = None,
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
        transcript_excerpt=transcript_excerpt,
    )


def parse_caption_variants(
    value: object,
    *,
    caption: str,
    target_platform: str,
    packaging_angle: str,
) -> dict[str, str]:
    if isinstance(value, dict):
        normalized = {str(key): str(item).strip() for key, item in value.items() if str(item).strip()}
        if normalized:
            defaults = default_caption_variants(
                caption=caption,
                target_platform=target_platform,
                packaging_angle=packaging_angle,
            )
            defaults.update(normalized)
            return defaults
    return default_caption_variants(
        caption=caption,
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
    transcript_excerpt: object = None,
) -> List[str]:
    focus = selected_trend or compact_phrase(str(transcript_excerpt or title or hook))
    platform_label = platform_display_name(target_platform)
    angle = packaging_angle.replace("-", " ")
    if packaging_angle == "controversy":
        return [
            f"Most people are still wrong about {focus}.",
            f"The {focus} disagreement starts here.",
            f"Post this when you want the comments to split.",
        ]
    if packaging_angle == "story":
        return [
            f"This is where {focus} turns.",
            f"Watch the payoff build in one cut.",
            f"The moment that makes the story worth posting.",
        ]
    if packaging_angle == "shock":
        return [
            f"Stop scrolling before this moment passes.",
            f"The payoff hits faster than the setup.",
            f"This is the interrupt cut for {platform_label}.",
        ]
    if packaging_angle == "curiosity":
        return [
            f"The skipped detail behind {focus}.",
            f"Most viewers miss this before the payoff.",
            f"Here is why this moment holds attention.",
        ]
    return [
        f"The useful part of {focus} starts here.",
        f"Save this cut before posting the full breakdown.",
        f"Use this {angle} cut first on {platform_label}.",
    ]


def default_caption_variants(
    *,
    caption: str,
    target_platform: str,
    packaging_angle: str,
) -> dict[str, str]:
    platform_label = platform_display_name(target_platform)
    return {
        "viral": caption,
        "story": f"{caption} Built to travel as a cleaner {packaging_angle} story for {platform_label}.",
        "educational": f"{caption} Keep the framing clear so the takeaway lands fast on {platform_label}.",
        "controversial": f"{caption} Frame the strongest disagreement early so the {platform_label} audience reacts.",
    }


def default_why_this_matters(
    *,
    title: str,
    target_platform: str,
    post_rank: int,
    packaging_angle: str | None = None,
    transcript_excerpt: object = None,
) -> str:
    packaging = (packaging_angle or "value").replace("_", " ")
    transcript_focus = compact_phrase(str(transcript_excerpt or title))
    platform = platform_display_name(target_platform)
    if post_rank == 1:
        return (
            f"Post this first because the {transcript_focus} payoff lands fast, sets the {packaging} frame, "
            f"and gives {platform} viewers the clearest reason to keep watching."
        )
    if post_rank == 2:
        return (
            f"Use this second because it extends the {packaging} angle after the opener earns attention, "
            f"then gives the {platform} stack a cleaner follow-up beat."
        )
    return (
        f"Hold this for later because the {transcript_focus} moment works best after viewers understand the angle "
        f"and are ready to comment, save, or follow through on {platform}."
    )


def default_reason(*, title: str, target_platform: str, packaging_angle: str) -> str:
    return f"{title} works for {target_platform} because the {packaging_angle} framing is easy to understand and fast to react to."


def default_thumbnail_text(
    *,
    title: str,
    hook: str,
    packaging_angle: str | None = None,
    target_platform: str | None = None,
    post_rank: int | None = None,
) -> str:
    source = hook if len(hook.strip()) >= len(title.strip()) else title
    words = signal_words(source, limit=3)
    if not words:
        if packaging_angle == "controversy":
            return "Wrong Take"
        if packaging_angle == "curiosity":
            return "Hidden Detail"
        if packaging_angle == "shock":
            return "Watch This"
        if post_rank == 1:
            return "Post First"
        return "Best Clip"

    text = " ".join(words).title()
    if post_rank == 1 and len(words) <= 2:
        return f"{text} First"
    return text


def default_cta_suggestion(*, target_platform: str, post_rank: int, packaging_angle: str | None = None) -> str:
    platform = normalize_platform(target_platform)
    packaging = (packaging_angle or "").lower()
    if post_rank == 1:
        if platform == "youtube":
            return "End by asking viewers to watch the full breakdown next."
        if platform == "instagram":
            return "End by asking viewers to save it before they forget the move."
        if platform == "tiktok":
            return "End by asking viewers if they want part two."
        if platform == "facebook":
            return "End by asking viewers which part they agree with most."
        return "End by asking viewers what they want broken down next."
    if packaging == "controversy":
        return "Close by asking viewers which side they agree with and why."
    if packaging == "story":
        return "Close by asking viewers if they want the next part or full sequence."
    if platform == "instagram":
        return "Close by asking people to save this and send it to a creator friend."
    if platform == "facebook":
        return "Close by inviting people to comment with the part they agreed with most."
    return "Close by asking viewers which angle they want you to break down next."


def default_caption_style(target_platform: str, packaging_angle: str | None = None) -> str:
    normalized = normalize_platform(target_platform)
    packaging = (packaging_angle or "").lower()
    if packaging == "controversy":
        return "Tension-led contrarian"
    if packaging == "story":
        return "Beat-driven narrative"
    if packaging == "curiosity":
        return "Question-led teaser"
    if packaging == "shock":
        return "Punchy interrupt"
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
    normalized = normalize_platform(target_platform)
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


def fallback_confidence_score(
    *,
    score: int,
    confidence: float,
    transcript_excerpt: object,
    source_context: Optional[SourceContext],
) -> int:
    transcript_bonus = min(score_excerpt(str(transcript_excerpt or "")) // 6, 10)
    selection_bonus = 4 if source_context and source_context.selection_strategy == "transcript" and transcript_excerpt else 0
    base = max(int(round(confidence * 100)), score - 4)
    return max(55, min(base + transcript_bonus + selection_bonus, 99))


def compact_phrase(value: str) -> str:
    words = signal_words(value, limit=3)
    if not words:
        return "this angle"
    return " ".join(words).lower()


STOP_WORDS = {
    "about",
    "after",
    "again",
    "also",
    "because",
    "before",
    "breakdown",
    "clip",
    "could",
    "from",
    "have",
    "into",
    "just",
    "like",
    "make",
    "most",
    "post",
    "really",
    "short",
    "that",
    "their",
    "there",
    "this",
    "video",
    "watch",
    "when",
    "with",
    "would",
    "your",
}


def signal_words(value: str, *, limit: int) -> list[str]:
    words: list[str] = []
    for word in re.findall(r"[A-Za-z0-9']+", value):
        normalized = word.strip("'").lower()
        if len(normalized) < 3 or normalized in STOP_WORDS:
            continue
        if normalized in words:
            continue
        words.append(normalized)
        if len(words) >= limit:
            break
    return words


def normalize_platform(value: str) -> str:
    normalized = (value or "").strip().lower()
    if "tiktok" in normalized:
        return "tiktok"
    if "instagram" in normalized or "reels" in normalized:
        return "instagram"
    if "youtube" in normalized or "shorts" in normalized:
        return "youtube"
    if "facebook" in normalized:
        return "facebook"
    if "linkedin" in normalized:
        return "linkedin"
    return "short-form"


def platform_display_name(value: str) -> str:
    normalized = normalize_platform(value)
    if normalized == "tiktok":
        return "TikTok"
    if normalized == "instagram":
        return "Instagram Reels"
    if normalized == "youtube":
        return "YouTube Shorts"
    if normalized == "facebook":
        return "Facebook"
    if normalized == "linkedin":
        return "LinkedIn"
    return "short-form"
