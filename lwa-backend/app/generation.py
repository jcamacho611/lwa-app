from __future__ import annotations

import json
from typing import List, Optional

import httpx
from openai import OpenAI

from .config import Settings
from .mock_data import build_mock_clips
from .processor import ClipSeed, SourceContext
from .schemas import ClipResult, TrendItem


def determine_provider(settings: Settings) -> str:
    provider = settings.ai_provider.lower()

    if provider == "auto":
        if settings.ollama_base_url:
            return "ollama"
        if settings.openai_api_key:
            return "openai"
        return "heuristic"

    return provider


async def generate_clips(
    *,
    settings: Settings,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> tuple[List[ClipResult], str]:
    provider = determine_provider(settings)

    if provider == "openai" and settings.openai_api_key:
        try:
            return await generate_with_openai(
                settings=settings,
                video_url=video_url,
                target_platform=target_platform,
                selected_trend=selected_trend,
                trend_context=trend_context,
                source_context=source_context,
            )
        except Exception:
            pass

    if provider == "ollama":
        try:
            return await generate_with_ollama(
                settings=settings,
                video_url=video_url,
                target_platform=target_platform,
                selected_trend=selected_trend,
                trend_context=trend_context,
                source_context=source_context,
            )
        except Exception:
            pass

    return (
        build_mock_clips(
            video_url=video_url,
            target_platform=target_platform,
            selected_trend=selected_trend,
            trend_context=trend_context,
            clip_urls=[seed.clip_url for seed in source_context.clip_seeds] if source_context else None,
            start_end_pairs=[(seed.start_time, seed.end_time) for seed in source_context.clip_seeds] if source_context else None,
            source_title=source_context.title if source_context else None,
            transcript_excerpts=[seed.transcript_excerpt for seed in source_context.clip_seeds] if source_context else None,
        ),
        "heuristic",
    )


async def generate_with_ollama(
    *,
    settings: Settings,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> tuple[List[ClipResult], str]:
    prompt = build_generation_prompt(video_url, target_platform, selected_trend, trend_context, source_context)

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
        trend_context,
        source_context,
    ), "ollama"


async def generate_with_openai(
    *,
    settings: Settings,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> tuple[List[ClipResult], str]:
    prompt = build_generation_prompt(video_url, target_platform, selected_trend, trend_context, source_context)
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
        trend_context,
        source_context,
    ), "openai"


def parse_generated_clips(
    raw: str,
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
    trend_context: List[TrendItem],
    source_context: Optional[SourceContext] = None,
) -> List[ClipResult]:
    try:
        payload = json.loads(raw)
        clips = payload.get("clips", [])
    except Exception:
        clips = []

    if not clips:
        return build_mock_clips(
            video_url=video_url,
            target_platform=target_platform,
            selected_trend=selected_trend,
            trend_context=trend_context,
            clip_urls=[seed.clip_url for seed in source_context.clip_seeds] if source_context else None,
            start_end_pairs=[(seed.start_time, seed.end_time) for seed in source_context.clip_seeds] if source_context else None,
            source_title=source_context.title if source_context else None,
            transcript_excerpts=[seed.transcript_excerpt for seed in source_context.clip_seeds] if source_context else None,
        )

    normalized: list[ClipResult] = []
    for index, clip in enumerate(clips[:3], start=1):
        seed = source_context.clip_seeds[index - 1] if source_context and len(source_context.clip_seeds) >= index else None
        normalized.append(
            ClipResult(
                id=seed.id if seed else f"clip_{index:03d}",
                title=str(clip.get("title", f"{target_platform} Clip {index}")),
                hook=str(clip.get("hook", "Lead with a strong hook.")),
                caption=str(clip.get("caption", "Use a short value-focused caption.")),
                start_time=seed.start_time if seed else str(clip.get("start_time", "00:00")),
                end_time=seed.end_time if seed else str(clip.get("end_time", "00:15")),
                score=int(clip.get("score", max(70, 95 - (index * 4)))),
                format=str(clip.get("format", seed.format if seed else "Trend First")),
                clip_url=seed.clip_url if seed else clip.get("clip_url"),
                raw_clip_url=seed.raw_clip_url if seed else clip.get("raw_clip_url"),
                transcript_excerpt=seed.transcript_excerpt if seed else clip.get("transcript_excerpt"),
                edit_profile=clip.get("edit_profile"),
                aspect_ratio=clip.get("aspect_ratio"),
            )
        )

    return normalized


def build_generation_prompt(
    video_url: str,
    target_platform: str,
    selected_trend: Optional[str],
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
      "caption": "...",
      "score": 90,
      "format": "Hook First"
    }}
  ]
}}
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
