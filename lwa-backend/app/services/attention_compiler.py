from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Optional

from openai import OpenAI

from ..core.config import Settings
from ..models.schemas import ClipResult, ScoreBreakdown
from ..processor import SourceContext, score_excerpt
from .anthropic_service import (
    anthropic_available,
    generate_clip_packaging_with_opus,
    generate_clip_packaging_with_sonnet,
)
from .ai_service import resolve_attention_mode

logger = logging.getLogger("uvicorn.error")

ALLOWED_PACKAGING_ANGLES = {"shock", "story", "value", "controversy", "curiosity"}
SIGNAL_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "but",
    "by",
    "clip",
    "for",
    "from",
    "get",
    "gets",
    "got",
    "has",
    "have",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "just",
    "make",
    "most",
    "one",
    "of",
    "on",
    "or",
    "part",
    "post",
    "first",
    "reels",
    "shorts",
    "that",
    "the",
    "their",
    "them",
    "they",
    "this",
    "tiktok",
    "to",
    "use",
    "using",
    "want",
    "when",
    "why",
    "with",
    "you",
    "your",
    "youtube",
}


async def compile_attention(
    *,
    settings: Settings,
    clips: list[ClipResult],
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    source_context: Optional[SourceContext],
    premium_reasoning: bool = False,
) -> tuple[list[ClipResult], str]:
    mode = resolve_attention_mode(settings, premium_reasoning=premium_reasoning)
    logger.info("attention_compiler_start mode=%s clips=%s", mode, len(clips))

    if not clips:
        logger.info("attention_compiler_end mode=%s clips=0", mode)
        return clips, mode

    if mode == "anthropic" and anthropic_available(settings):
        try:
            compiled = await asyncio.to_thread(
                compile_with_anthropic,
                settings,
                clips,
                target_platform,
                selected_trend,
                content_angle,
                source_context,
                premium_reasoning,
            )
            logger.info("attention_compiler_end mode=anthropic clips=%s", len(compiled))
            return compiled, "anthropic-opus" if premium_reasoning else "anthropic-sonnet"
        except Exception as error:
            logger.warning("attention_compiler_fallback mode=anthropic reason=%s", error)

    if mode == "openai":
        try:
            compiled = await asyncio.to_thread(
                compile_with_openai,
                settings,
                clips,
                target_platform,
                selected_trend,
                content_angle,
                source_context,
            )
            logger.info("attention_compiler_end mode=openai clips=%s", len(compiled))
            return compiled, "openai"
        except Exception as error:
            logger.warning("attention_compiler_fallback mode=openai reason=%s", error)

    compiled = compile_with_fallback(
        clips=clips,
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        source_context=source_context,
    )
    logger.info("attention_compiler_end mode=fallback clips=%s", len(compiled))
    return compiled, "fallback"


def compile_with_anthropic(
    settings: Settings,
    clips: list[ClipResult],
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    source_context: Optional[SourceContext],
    premium_reasoning: bool,
) -> list[ClipResult]:
    prompt = build_attention_prompt(
        clips=clips,
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        source_context=source_context,
    )
    if premium_reasoning:
        raw = generate_clip_packaging_with_opus(settings=settings, prompt=prompt)
    else:
        raw = generate_clip_packaging_with_sonnet(settings=settings, prompt=prompt)

    try:
        payload = json.loads(raw)
    except Exception as error:
        raise RuntimeError(f"invalid compiler payload: {error}") from error

    entries = payload.get("clips", [])
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("empty compiler payload")

    compiled = merge_compiler_entries(
        clips=clips,
        entries=entries,
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        source_context=source_context,
    )
    return rank_compiled_clips(compiled)


def compile_with_openai(
    settings: Settings,
    clips: list[ClipResult],
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    source_context: Optional[SourceContext],
) -> list[ClipResult]:
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        input=build_attention_prompt(
            clips=clips,
            target_platform=target_platform,
            selected_trend=selected_trend,
            content_angle=content_angle,
            source_context=source_context,
        ),
    )
    raw = response.output_text

    try:
        payload = json.loads(raw)
    except Exception as error:
        raise RuntimeError(f"invalid compiler payload: {error}") from error

    entries = payload.get("clips", [])
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("empty compiler payload")

    compiled = merge_compiler_entries(
        clips=clips,
        entries=entries,
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        source_context=source_context,
    )
    return rank_compiled_clips(compiled)


def compile_with_fallback(
    *,
    clips: list[ClipResult],
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    source_context: Optional[SourceContext],
) -> list[ClipResult]:
    compiled: list[ClipResult] = []
    for index, clip in enumerate(clips, start=1):
        analysis = heuristic_analysis(
            clip=clip,
            target_platform=target_platform,
            selected_trend=selected_trend,
            content_angle=content_angle,
            source_context=source_context,
            index=index,
        )
        compiled.append(clip.model_copy(update=analysis))

    logger.info("attention_compiler_scored mode=fallback clips=%s", len(compiled))
    return rank_compiled_clips(compiled)


def merge_compiler_entries(
    *,
    clips: list[ClipResult],
    entries: list[object],
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    source_context: Optional[SourceContext],
) -> list[ClipResult]:
    entry_map = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        entry_id = str(entry.get("id") or "").strip()
        entry_map[entry_id or f"index:{index}"] = entry

    merged: list[ClipResult] = []
    for index, clip in enumerate(clips):
        entry = entry_map.get(clip.id) or entry_map.get(f"index:{index}") or {}
        merged.append(
            clip.model_copy(
                update=normalize_compiler_update(
                    clip=clip,
                    entry=entry,
                    target_platform=target_platform,
                    selected_trend=selected_trend,
                    content_angle=content_angle,
                    source_context=source_context,
                    index=index + 1,
                )
            )
        )

    logger.info("attention_compiler_scored mode=openai clips=%s", len(merged))
    return merged


def normalize_compiler_update(
    *,
    clip: ClipResult,
    entry: dict[object, object],
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    source_context: Optional[SourceContext],
    index: int,
) -> dict[str, object]:
    heuristic = heuristic_analysis(
        clip=clip,
        target_platform=target_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
        source_context=source_context,
        index=index,
    )
    score = clamp_score(entry.get("score"), fallback=int(heuristic["score"]))
    confidence = clamp_confidence(entry.get("confidence"), fallback=float(heuristic["confidence"]))
    reason = str_or_default(entry.get("reason"), str(heuristic["reason"]))
    packaging_angle = normalize_packaging_angle(entry.get("packaging_angle"), fallback=str(heuristic["packaging_angle"]))
    hook_variants = normalize_hook_variants(
        entry.get("hook_variants"),
        fallback=list(heuristic["hook_variants"]),
    )
    score_breakdown = normalize_score_breakdown(
        entry.get("score_breakdown"),
        fallback=heuristic["score_breakdown"],
    )

    return {
        "score": score,
        "virality_score": score,
        "hook_score": clamp_score(entry.get("hook_score"), fallback=int(heuristic["hook_score"])),
        "confidence": confidence,
        "reason": reason,
        "why_this_matters": str_or_default(entry.get("why_this_matters"), str(heuristic["why_this_matters"])),
        "confidence_score": clamp_score(entry.get("confidence_score"), fallback=int(heuristic["confidence_score"])),
        "score_breakdown": score_breakdown,
        "scoring_explanation": str_or_default(
            entry.get("scoring_explanation"),
            str(heuristic["scoring_explanation"]),
        ),
        "hook_variants": hook_variants,
        "caption_variants": normalize_caption_variants(
            entry.get("caption_variants"),
            fallback=caption_variants_for(
                clip=clip,
                target_platform=target_platform,
                packaging_angle=packaging_angle,
            ),
        ),
        "packaging_angle": packaging_angle,
        "platform_fit": str_or_default(entry.get("platform_fit"), str(heuristic["platform_fit"])),
        "thumbnail_text": str_or_default(entry.get("thumbnail_text"), str(heuristic["thumbnail_text"])),
        "cta_suggestion": str_or_default(entry.get("cta_suggestion"), str(heuristic["cta_suggestion"])),
        "caption_style": str_or_default(entry.get("caption_style"), str(heuristic["caption_style"])),
        "render_readiness_score": clamp_score(
            entry.get("render_readiness_score"),
            fallback=int(heuristic["render_readiness_score"]),
        ),
        "post_rank": clamp_score(entry.get("post_rank"), fallback=index),
    }


def rank_compiled_clips(clips: list[ClipResult]) -> list[ClipResult]:
    review_ranked = sorted(
        clips,
        key=lambda clip: (-(clip.score or 0), -(clip.confidence or 0.0), clip.start_time),
    )
    ranked: list[ClipResult] = []
    for rank, clip in enumerate(review_ranked, start=1):
        ranked.append(
            clip.model_copy(
                update={
                    "rank": rank,
                    "confidence_score": clip.confidence_score or max(0, min(int(round((clip.confidence or 0.0) * 100)), 100)),
                    "caption_style": clip.caption_style or caption_style_for(clip.platform_fit or "", clip.packaging_angle or "value"),
                }
            )
        )

    posting_sequence = sorted(
        ranked,
        key=lambda clip: (
            posting_stage_for(clip),
            clip.post_rank or 999,
            -(clip.score or 0),
            clip.rank or 999,
            clip.start_time,
        ),
    )
    post_order = {clip.id: index for index, clip in enumerate(posting_sequence, start=1)}

    finalized: list[ClipResult] = []
    for clip in ranked:
        post_rank = post_order.get(clip.id, clip.rank or 1)
        finalized.append(
            clip.model_copy(
                update={
                    "post_rank": post_rank,
                    "best_post_order": post_rank,
                    "why_this_matters": clip.why_this_matters
                    or why_this_matters_for(
                        clip=clip,
                        target_platform=clip.platform_fit or "short-form",
                        packaging_angle=clip.packaging_angle or "value",
                        post_rank=post_rank,
                        review_rank=clip.rank or post_rank,
                    ),
                }
            )
        )

    logger.info("attention_compiler_ranking_complete clips=%s", len(finalized))
    return finalized


def heuristic_analysis(
    *,
    clip: ClipResult,
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    source_context: Optional[SourceContext],
    index: int,
) -> dict[str, object]:
    opening_line = primary_opening_line(clip.hook or clip.transcript_excerpt or clip.title)
    combined_text = " ".join(
        part
        for part in [
            clip.title,
            clip.hook,
            clip.caption,
            clip.transcript_excerpt or "",
            source_context.title if source_context else "",
            selected_trend or "",
        ]
        if part
    )
    punctuation = punctuation_score(combined_text)
    emotional = keyword_score(combined_text, {"love", "hate", "pain", "fear", "crazy", "wild", "shocking", "secret"}) + punctuation
    story = keyword_score(combined_text, {"story", "when", "then", "realized", "started", "moment", "because"})
    curiosity = keyword_score(combined_text, {"why", "how", "stop", "before", "nobody", "most", "exact", "mistake"})
    replay = keyword_score(combined_text, {"exact", "step", "mistake", "never", "always", "pattern", "shortcut", "convert"})
    clarity = clarity_score(combined_text)
    retention = duration_score(clip.start_time, clip.end_time)
    transcript_signal = transcript_signal_score(clip.transcript_excerpt, source_context=source_context)
    hook_strength = hook_strength_score(opening_line)
    standalone = standalone_coherence_score(opening_line, combined_text)
    authority = authority_signal_score(combined_text)
    contrarian = keyword_score(combined_text, {"wrong", "myth", "nobody", "most", "never", "mistake", "everyone"})

    packaging_angle = heuristic_packaging_angle(
        combined_text=combined_text,
        preferred_angle=content_angle,
        emotional=emotional,
        story=story,
        curiosity=curiosity,
        replay=replay,
    )
    breakdown_data = score_breakdown_for(
        clip=clip,
        target_platform=target_platform,
        combined_text=combined_text,
        packaging_angle=packaging_angle,
        punctuation=punctuation,
        emotional=emotional,
        story=story,
        curiosity=curiosity,
        replay=replay,
        clarity=clarity,
        retention=retention,
        transcript_signal=transcript_signal,
        hook_strength=hook_strength,
        standalone=standalone,
        authority=authority,
        contrarian=contrarian,
    )
    score_breakdown = ScoreBreakdown(**breakdown_data)
    score = weighted_virality_score(breakdown_data)
    score = max(score, 38 if clip.transcript_excerpt else 32)
    signal_completeness = sum(1 for value in breakdown_data.values() if value >= 55)
    confidence = clamp_confidence(
        None,
        fallback=min(
            0.97,
            max(
                0.45,
                (score / 100.0)
                + (0.04 if clip.transcript_excerpt else 0.0)
                + (0.02 if index == 1 else 0.0)
                + min(signal_completeness / 140.0, 0.08),
            ),
        ),
    )
    focus = selected_trend or focus_phrase_for(
        clip.transcript_excerpt,
        clip.hook,
        clip.title,
        source_context.title if source_context else "",
    )
    hook_variants = build_hook_variants(
        clip=clip,
        target_platform=target_platform,
        packaging_angle=packaging_angle,
        focus=focus,
        selected_trend=selected_trend,
    )
    thumbnail_text = thumbnail_text_for(
        clip.title,
        clip.hook,
        transcript_excerpt=clip.transcript_excerpt,
        packaging_angle=packaging_angle,
    )

    return {
        "score": score,
        "virality_score": score,
        "hook_score": score_breakdown.hook_score,
        "confidence": confidence,
        "confidence_score": max(int(round(confidence * 100)), 55 if score >= 60 else 46),
        "reason": heuristic_reason_for(
            target_platform=target_platform,
            packaging_angle=packaging_angle,
            hook_strength=hook_strength,
            standalone=standalone,
            emotional=emotional,
            curiosity=curiosity,
            authority=authority,
        ),
        "score_breakdown": score_breakdown,
        "scoring_explanation": scoring_explanation_for(score_breakdown),
        "why_this_matters": why_this_matters_for(
            clip=clip,
            target_platform=target_platform,
            packaging_angle=packaging_angle,
            post_rank=index,
            review_rank=index,
        ),
        "hook_variants": hook_variants,
        "caption_variants": caption_variants_for(
            clip=clip,
            target_platform=target_platform,
            packaging_angle=packaging_angle,
        ),
        "packaging_angle": packaging_angle,
        "platform_fit": platform_fit_for(target_platform, packaging_angle),
        "thumbnail_text": thumbnail_text,
        "cta_suggestion": cta_for(target_platform, index, packaging_angle=packaging_angle),
        "caption_style": caption_style_for(target_platform, packaging_angle),
        "render_readiness_score": score_breakdown.render_readiness_score,
    }


def build_attention_prompt(
    *,
    clips: list[ClipResult],
    target_platform: str,
    selected_trend: Optional[str],
    content_angle: Optional[str],
    source_context: Optional[SourceContext],
) -> str:
    source_title = source_context.title if source_context else "Unknown source"
    source_duration = source_context.duration_seconds if source_context and source_context.duration_seconds else "unknown"
    clip_lines = "\n".join(
        f"- id={clip.id} | title={clip.title} | start={clip.start_time} | end={clip.end_time} | format={clip.format} | hook={clip.hook} | caption={clip.caption} | transcript={clip.transcript_excerpt or 'none'}"
        for clip in clips
    )
    return f"""
You are the Attention Compiler for a short-form video system.

Score and enrich the candidate clips for {target_platform}.
Selected trend: {selected_trend or "none"}
Preferred packaging angle: {content_angle or "none"}
Source title: {source_title}
Source duration seconds: {source_duration}

Candidates:
{clip_lines}

Return valid JSON with this shape:
{{
  "clips": [
    {{
      "id": "clip_001",
      "score": 91,
      "confidence": 0.87,
      "reason": "Short sentence on why the clip will work.",
      "why_this_matters": "Short sentence on where this belongs in the post stack.",
      "hook_variants": ["...", "...", "..."],
      "caption_variants": {{
        "viral": "...",
        "story": "...",
        "educational": "...",
        "controversial": "..."
      }},
      "caption_style": "...",
      "post_rank": 1,
      "packaging_angle": "value",
      "platform_fit": "Short sentence tailored to the platform.",
      "cta_suggestion": "Short CTA suggestion.",
      "thumbnail_text": "2 to 5 words"
    }}
  ]
}}

Rules:
- Use only these packaging angles: shock, story, value, controversy, curiosity.
- hook_variants must contain 3 to 5 options.
- caption_variants must contain these keys exactly: viral, story, educational, controversial.
- why_this_matters must explain whether the clip should open, deepen, or close the posting stack.
- post_rank must recommend the posting sequence separately from the overall score.
- confidence must be a float between 0.0 and 1.0.
- Keep reason, platform_fit, and cta_suggestion concise.
""".strip()


def normalize_hook_variants(value: object, *, fallback: list[str]) -> list[str]:
    variants: list[str] = []
    if isinstance(value, list):
        variants.extend(str(item).strip() for item in value if str(item).strip())
    variants.extend(fallback)
    return unique_variants(variants)[:5]


def normalize_packaging_angle(value: object, *, fallback: str) -> str:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ALLOWED_PACKAGING_ANGLES:
            return normalized
    return fallback


def normalize_caption_variants(value: object, *, fallback: dict[str, str]) -> dict[str, str]:
    if isinstance(value, dict):
        normalized: dict[str, str] = {}
        for key in ("viral", "story", "educational", "controversial"):
            raw = value.get(key)
            if isinstance(raw, str) and raw.strip():
                normalized[key] = raw.strip()
        if normalized:
            return {**fallback, **normalized}
    return fallback


def normalize_score_breakdown(value: object, *, fallback: object) -> ScoreBreakdown:
    if isinstance(fallback, ScoreBreakdown):
        normalized = fallback.model_dump()
    elif isinstance(fallback, dict):
        normalized = {
            key: clamp_score(raw, fallback=0)
            for key, raw in fallback.items()
        }
    else:
        normalized = ScoreBreakdown().model_dump()

    if isinstance(value, ScoreBreakdown):
        normalized.update(value.model_dump())
    elif isinstance(value, dict):
        for key in ScoreBreakdown.model_fields:
            if key in value:
                normalized[key] = clamp_score(value.get(key), fallback=normalized.get(key, 0))

    return ScoreBreakdown(**normalized)


def scaled_component(raw: float, maximum: float) -> int:
    if maximum <= 0:
        return 0
    return max(0, min(int(round((raw / maximum) * 100)), 100))


def platform_fit_score_for(
    *,
    target_platform: str,
    duration_seconds: int,
    packaging_angle: str,
    has_transcript: bool,
    opening_line: str,
) -> int:
    normalized = target_platform.lower()
    if "tiktok" in normalized:
        if 7 <= duration_seconds <= 30:
            base = 88
        elif 5 <= duration_seconds <= 45:
            base = 76
        elif duration_seconds <= 60:
            base = 64
        else:
            base = 46
        if packaging_angle in {"shock", "curiosity", "controversy"}:
            base += 6
    elif "instagram" in normalized or "reels" in normalized:
        if 7 <= duration_seconds <= 30:
            base = 86
        elif 30 <= duration_seconds <= 60:
            base = 80
        elif duration_seconds <= 90:
            base = 68
        else:
            base = 48
        if packaging_angle in {"story", "curiosity", "value"}:
            base += 4
    elif "youtube" in normalized or "shorts" in normalized:
        if 15 <= duration_seconds <= 60:
            base = 88
        elif 10 <= duration_seconds <= 75:
            base = 76
        else:
            base = 52
        if packaging_angle in {"value", "story", "curiosity"}:
            base += 5
    elif "linkedin" in normalized:
        if 30 <= duration_seconds <= 90:
            base = 88
        elif 20 <= duration_seconds <= 180:
            base = 72
        else:
            base = 46
        if packaging_angle in {"value", "story"}:
            base += 6
    elif "facebook" in normalized:
        if 15 <= duration_seconds <= 60:
            base = 84
        elif 10 <= duration_seconds <= 75:
            base = 72
        else:
            base = 48
        if packaging_angle in {"story", "value"}:
            base += 4
    else:
        base = 74 if 10 <= duration_seconds <= 60 else 58

    opening_words = re.findall(r"[A-Za-z0-9']+", opening_line)
    if has_transcript:
        base += 4
    if 5 <= len(opening_words) <= 14:
        base += 2
    return max(0, min(base, 100))


def commercial_signal_score(text: str) -> int:
    lowered = text.lower()
    score = 0
    if re.search(r"[$€£]\s?\d", text) or re.search(r"\b\d+(k|m|x|%)\b", lowered):
        score += 8
    if any(keyword in lowered for keyword in {"revenue", "sales", "clients", "followers", "grew", "made", "results", "booked"}):
        score += 6
    if any(keyword in lowered for keyword in {"offer", "buy", "dm", "consult", "join", "book"}):
        score += 4
    return min(score, 18)


def score_breakdown_for(
    *,
    clip: ClipResult,
    target_platform: str,
    combined_text: str,
    packaging_angle: str,
    punctuation: int,
    emotional: int,
    story: int,
    curiosity: int,
    replay: int,
    clarity: int,
    retention: int,
    transcript_signal: int,
    hook_strength: int,
    standalone: int,
    authority: int,
    contrarian: int,
) -> dict[str, int]:
    duration_seconds = max(parse_timestamp(clip.end_time or "0") - parse_timestamp(clip.start_time or "0"), 1)
    hook_score = scaled_component(
        hook_strength + (curiosity * 0.45) + (contrarian * 0.35) + (authority * 0.20),
        34,
    )
    retention_score = scaled_component((retention * 0.6) + (standalone * 0.4), 22)
    emotional_spike_score = scaled_component(emotional, 34)
    clarity_component = scaled_component((clarity * 0.65) + (transcript_signal * 0.35), 19)
    platform_fit_score = platform_fit_score_for(
        target_platform=target_platform,
        duration_seconds=duration_seconds,
        packaging_angle=packaging_angle,
        has_transcript=bool(clip.transcript_excerpt),
        opening_line=clip.hook or clip.title,
    )
    visual_energy_score = scaled_component(
        (emotional * 0.40) + (contrarian * 0.25) + (hook_strength * 0.20) + (8 if packaging_angle in {"shock", "controversy"} else 0),
        30,
    )
    audio_energy_score = scaled_component((emotional * 0.50) + (hook_strength * 0.35) + (curiosity * 0.15), 30)
    controversy_score = scaled_component(min(contrarian + (8 if packaging_angle == "controversy" else 0), 24), 24)
    educational_value_score = scaled_component((authority * 0.55) + (replay * 0.45), 18)
    share_comment_score = scaled_component(
        (curiosity * 0.35)
        + (contrarian * 0.40)
        + (emotional * 0.15)
        + (8 if packaging_angle in {"controversy", "curiosity"} else 0),
        24,
    )
    commercial_value_score = scaled_component(
        (authority * 0.40) + (transcript_signal * 0.20) + (commercial_signal_score(combined_text) * 0.40),
        14,
    )

    render_readiness_score = clip.render_readiness_score
    if render_readiness_score is None:
        render_readiness_base = 28 + min(transcript_signal * 2, 18)
        if clip.transcript_excerpt:
            render_readiness_base += 12
        if 7 <= duration_seconds <= 45:
            render_readiness_base += 8
        elif 5 <= duration_seconds <= 60:
            render_readiness_base += 4
        if hook_score >= 70:
            render_readiness_base += 8
        elif hook_score >= 55:
            render_readiness_base += 4
        if clarity_component >= 70:
            render_readiness_base += 8
        elif clarity_component >= 55:
            render_readiness_base += 4
        if audio_energy_score >= 60:
            render_readiness_base += 6
        elif audio_energy_score >= 45:
            render_readiness_base += 3
        if any([clip.preview_url, clip.clip_url, clip.edited_clip_url, clip.raw_clip_url]):
            render_readiness_base += 18
        if clip.render_status == "failed":
            render_readiness_base -= 18
        render_readiness_score = max(22, min(render_readiness_base, 92))

    return {
        "hook_score": hook_score,
        "retention_score": retention_score,
        "emotional_spike_score": emotional_spike_score,
        "clarity_score": clarity_component,
        "platform_fit_score": platform_fit_score,
        "visual_energy_score": visual_energy_score,
        "audio_energy_score": audio_energy_score,
        "controversy_score": controversy_score,
        "educational_value_score": educational_value_score,
        "share_comment_score": share_comment_score,
        "render_readiness_score": clamp_score(render_readiness_score, fallback=render_readiness_score),
        "commercial_value_score": commercial_value_score,
    }


def weighted_virality_score(breakdown: dict[str, int]) -> int:
    score = (
        (breakdown["hook_score"] * 0.25)
        + (breakdown["retention_score"] * 0.20)
        + (breakdown["emotional_spike_score"] * 0.15)
        + (breakdown["clarity_score"] * 0.10)
        + (breakdown["platform_fit_score"] * 0.10)
        + (breakdown["visual_energy_score"] * 0.05)
        + (breakdown["audio_energy_score"] * 0.05)
        + (breakdown["controversy_score"] * 0.03)
        + (breakdown["educational_value_score"] * 0.03)
        + (breakdown["share_comment_score"] * 0.02)
        + (breakdown["render_readiness_score"] * 0.01)
        + (breakdown["commercial_value_score"] * 0.01)
    )
    return clamp_score(None, fallback=int(round(score)))


def scoring_explanation_for(score_breakdown: ScoreBreakdown) -> str:
    explanation_map = {
        "hook_score": "the opener lands quickly",
        "retention_score": "the pacing should hold attention long enough to pay off",
        "emotional_spike_score": "the emotion carries extra replay pressure",
        "clarity_score": "the point is easy to understand fast",
        "platform_fit_score": "the trim fits the target platform cleanly",
        "visual_energy_score": "the moment should feel active on screen",
        "audio_energy_score": "the delivery has enough lift to carry the cut",
        "controversy_score": "the take is sharp enough to trigger responses",
        "educational_value_score": "the value is specific enough to save or share",
        "share_comment_score": "the framing gives viewers a reason to comment",
        "render_readiness_score": "the clip is technically ready to turn into a usable asset",
        "commercial_value_score": "the language carries clear proof or offer value",
    }
    breakdown = score_breakdown.model_dump()
    strongest = sorted(
        ((key, value) for key, value in breakdown.items() if key != "render_readiness_score"),
        key=lambda item: item[1],
        reverse=True,
    )
    strengths = [explanation_map[key] for key, value in strongest if value >= 65][:2]
    if not strengths:
        strengths = [explanation_map[strongest[0][0]]] if strongest else ["the clip has enough signal to test"]
    readiness = (
        "ready now"
        if score_breakdown.render_readiness_score >= 72
        else "worth testing but still needs review"
        if score_breakdown.render_readiness_score >= 55
        else "mostly strategic until render quality improves"
    )
    if len(strengths) == 1:
        return f"Score driven by {strengths[0]}. Render readiness is {readiness}."
    return f"Score driven by {strengths[0]} and {strengths[1]}. Render readiness is {readiness}."


def keyword_score(text: str, keywords: set[str]) -> int:
    lowered = text.lower()
    return min(sum(4 for keyword in keywords if keyword in lowered), 24)


def punctuation_score(text: str) -> int:
    return min((text.count("!") * 3) + (text.count("?") * 2), 10)


def clarity_score(text: str) -> int:
    words = re.findall(r"[A-Za-z0-9']+", text)
    if not words:
        return 8
    word_count = len(words)
    if 10 <= word_count <= 36:
        return 22
    if 6 <= word_count <= 50:
        return 18
    return 12


def primary_opening_line(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", cleaned, maxsplit=1)
    return parts[0].strip() if parts else cleaned


def hook_strength_score(text: str) -> int:
    lowered = text.lower()
    words = re.findall(r"[A-Za-z0-9']+", text)
    score = 0
    if 5 <= len(words) <= 12:
        score += 6
    elif 4 <= len(words) <= 18:
        score += 4
    elif words:
        score += 2
    if lowered.startswith(("stop", "why", "how", "if", "most", "this", "here")):
        score += 8
    if any(keyword in lowered for keyword in {"exact", "secret", "mistake", "wrong", "before", "nobody", "proof", "finally", "again", "suddenly"}):
        score += 6
    if any(phrase in lowered for phrase in {"most creators", "why this", "how this", "the exact", "stop doing"}):
        score += 4
    if any(token.isdigit() for token in words):
        score += 3
    if "?" in text or "!" in text:
        score += 3
    return min(score, 30)


def standalone_coherence_score(primary_line: str, combined_text: str) -> int:
    lowered = primary_line.lower()
    line_words = re.findall(r"[A-Za-z0-9']+", primary_line)
    signal_words = significant_words(primary_line or combined_text)
    score = 0
    if 6 <= len(line_words) <= 24:
        score += 6
    elif 4 <= len(line_words) <= 30:
        score += 4
    if len(signal_words) >= 3:
        score += 4
    elif len(signal_words) >= 2:
        score += 2
    if re.search(r"\b(because|so|when|why|how|if|here's|this is)\b", lowered):
        score += 4
    if primary_line.endswith((".", "?", "!")):
        score += 2
    if len(set(signal_words[:6])) >= 3:
        score += 2
    return min(score, 18)


def authority_signal_score(text: str) -> int:
    lowered = text.lower()
    score = 0
    if any(char.isdigit() for char in text):
        score += 4
    if any(keyword in lowered for keyword in {"exact", "step", "framework", "proof", "tested", "results", "system", "breakdown", "playbook"}):
        score += 6
    if any(keyword in lowered for keyword in {"today", "right now", "again", "first"}):
        score += 2
    return min(score, 12)


def heuristic_reason_for(
    *,
    target_platform: str,
    packaging_angle: str,
    hook_strength: int,
    standalone: int,
    emotional: int,
    curiosity: int,
    authority: int,
) -> str:
    strengths: list[str] = []
    if hook_strength >= 12:
        strengths.append("the opener makes a clear claim fast")
    if standalone >= 10:
        strengths.append("the clip stands on its own without extra context")
    if curiosity >= 12:
        strengths.append("the setup creates a real reason to stay for the payoff")
    if emotional >= 12:
        strengths.append("the emotional spike gives the cut stronger replay pressure")
    if authority >= 8:
        strengths.append("the language feels specific enough to earn trust quickly")
    if not strengths:
        strengths.append(f"the {packaging_angle} framing keeps the payoff easy to understand")
    return f"This clip should travel on {target_platform} because {', '.join(strengths[:2])}."


def duration_score(start_time: str, end_time: str) -> int:
    start_seconds = parse_timestamp(start_time)
    end_seconds = parse_timestamp(end_time)
    duration = max(end_seconds - start_seconds, 1)
    if 10 <= duration <= 24:
        return 24
    if 7 <= duration <= 32:
        return 18
    return 12


def heuristic_packaging_angle(
    *,
    combined_text: str,
    preferred_angle: Optional[str],
    emotional: int,
    story: int,
    curiosity: int,
    replay: int,
) -> str:
    if isinstance(preferred_angle, str):
        normalized_preference = preferred_angle.strip().lower()
        if normalized_preference in ALLOWED_PACKAGING_ANGLES:
            return normalized_preference
    lowered = combined_text.lower()
    if any(keyword in lowered for keyword in {"wrong", "never", "nobody", "myth", "mistake"}):
        return "controversy"
    if story >= emotional and story >= curiosity and story >= replay:
        return "story"
    if any(keyword in lowered for keyword in {"secret", "crazy", "wild", "shocking"}):
        return "shock"
    if curiosity >= emotional and curiosity >= replay:
        return "curiosity"
    return "value"


def platform_fit_for(target_platform: str, packaging_angle: str) -> str:
    normalized = target_platform.lower()
    if normalized == "tiktok":
        return f"TikTok-ready pacing with a {packaging_angle} opening and fast payoff."
    if normalized == "instagram":
        return f"Reels-friendly framing with cleaner visual packaging and a {packaging_angle} angle."
    if normalized == "youtube":
        return f"Shorts-native structure with context-light setup and a {packaging_angle} hook."
    return f"{target_platform} packaging built around a {packaging_angle} angle."


def unique_variants(values: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned:
            continue
        fingerprint = cleaned.lower()
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        normalized.append(cleaned)
    return normalized


def significant_words(value: str) -> list[str]:
    return [
        word
        for word in re.findall(r"[A-Za-z0-9']+", value)
        if word.lower() not in SIGNAL_STOPWORDS and len(word) > 2
    ]


def focus_phrase_for(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        words = significant_words(text)
        if len(words) >= 2:
            return " ".join(words[:3]).lower()
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        words = re.findall(r"[A-Za-z0-9']+", text)
        if words:
            return " ".join(words[:3]).lower()
    return "this clip"


def build_hook_variants(
    *,
    clip: ClipResult,
    target_platform: str,
    packaging_angle: str,
    focus: str,
    selected_trend: Optional[str],
) -> list[str]:
    trend_or_focus = (selected_trend or focus).strip()
    title_focus = focus_phrase_for(clip.title, clip.hook)
    base_focus = title_focus or "this clip"
    bold_claim = f"The clearest {trend_or_focus} proof starts with {base_focus}."
    contrarian = f"Most creators still frame {base_focus} the wrong way."
    curiosity_gap = f"Why {base_focus} is the part viewers wait to hear explained."

    if packaging_angle == "shock":
        bold_claim = f"Stop scrolling: {base_focus} changes the whole clip."
        contrarian = f"Most creators bury {base_focus} instead of opening with it."
        curiosity_gap = f"Why this {trend_or_focus} interruption holds attention longer than the rest."
    elif packaging_angle == "story":
        bold_claim = f"The story actually turns when {base_focus} lands."
        contrarian = f"Most creators start too early and miss the {base_focus} payoff."
        curiosity_gap = f"Why {base_focus} is the beat viewers stay for."
    elif packaging_angle == "controversy":
        bold_claim = f"The strongest proof in this clip is that {base_focus} flips the take."
        contrarian = f"Most creators still get {base_focus} wrong."
        curiosity_gap = f"Why the {trend_or_focus} argument starts the moment {base_focus} shows up."
    elif packaging_angle == "curiosity":
        bold_claim = f"The answer viewers want is buried inside {base_focus}."
        contrarian = f"Most people skip {base_focus} and lose the payoff."
        curiosity_gap = f"Why {base_focus} is suddenly working again."

    variants = [bold_claim, contrarian, curiosity_gap]

    return unique_variants(variants)[:5]


def thumbnail_text_for(
    title: str,
    hook: str,
    *,
    transcript_excerpt: str | None = None,
    packaging_angle: str | None = None,
) -> str:
    words: list[str] = []
    seen: set[str] = set()
    for word in significant_words(" ".join(part for part in [hook, transcript_excerpt or "", title] if part)):
        lowered = word.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        words.append(word)
    if len(words) < 2:
        words = re.findall(r"[A-Za-z0-9']+", hook or title)

    selected = [word.title() for word in words[:4] if word]
    if len(selected) == 1:
        suffix = {
            "shock": "Moment",
            "story": "Payoff",
            "controversy": "Take",
            "curiosity": "Question",
            "value": "Framework",
        }.get((packaging_angle or "value").lower(), "Clip")
        selected.append(suffix)

    if not selected:
        selected = ["Best", "Clip"]

    return " ".join(selected[:5])


def cta_for(target_platform: str, rank: int, *, packaging_angle: str | None = None) -> str:
    platform = target_platform.lower()
    if packaging_angle == "controversy":
        return "Ask viewers which side they agree with and why."
    if packaging_angle == "story":
        return "Ask viewers if they want the next beat or the full sequence."
    if packaging_angle == "value":
        return "Ask viewers which step they want broken down next."
    if rank == 1:
        return "Ask viewers if they want the full breakdown or next part."
    if platform == "instagram":
        return "Ask viewers to save this and send it to a creator friend."
    if platform == "youtube":
        return "Ask viewers which angle they want broken down next."
    return "Ask viewers to comment with the point they agreed with most."


def caption_style_for(target_platform: str, packaging_angle: str) -> str:
    normalized_platform = target_platform.lower()
    normalized_angle = packaging_angle.lower()
    if normalized_angle == "controversy":
        return "Tension-led contrarian"
    if normalized_angle == "story":
        return "Beat-driven narrative"
    if normalized_angle == "curiosity":
        return "Question-led teaser"
    if normalized_angle == "shock":
        return "Punchy interrupt"
    if "tiktok" in normalized_platform:
        return "Punchy proof-first"
    if "instagram" in normalized_platform or "reels" in normalized_platform:
        return "Polished emotional"
    if "youtube" in normalized_platform or "shorts" in normalized_platform:
        return "Clarity-led payoff"
    if "facebook" in normalized_platform:
        return "Story-first social"
    return "Short-form native"


def posting_stage_for(clip: ClipResult) -> int:
    angle = (clip.packaging_angle or "value").lower()
    combined_text = " ".join(
        part.lower()
        for part in [clip.hook, clip.title, clip.caption, clip.transcript_excerpt or ""]
        if part
    )
    if angle in {"shock", "curiosity"} or any(
        keyword in combined_text for keyword in {"stop", "secret", "before", "why", "mistake", "nobody"}
    ):
        return 0
    if angle == "controversy" or any(
        keyword in combined_text for keyword in {"wrong", "argue", "debate", "myth", "disagree"}
    ):
        return 1
    if angle == "value" or any(
        keyword in combined_text for keyword in {"step", "framework", "exact", "how", "lesson", "breakdown"}
    ):
        return 2
    return 3


def why_this_matters_for(
    *,
    clip: ClipResult,
    target_platform: str,
    packaging_angle: str,
    post_rank: int,
    review_rank: int,
) -> str:
    focus = focus_phrase_for(clip.transcript_excerpt, clip.title, clip.hook)
    platform_name = target_platform or "short-form"
    if post_rank == 1:
        return (
            f"Open with this because the {focus} payoff lands quickly and gives {platform_name} viewers "
            f"the strongest first impression with a {packaging_angle} frame."
        )
    if post_rank == 2:
        return (
            f"Use this second because it deepens the {packaging_angle} angle after the opener and gives the posting stack "
            f"a stronger middle beat for {platform_name} viewers."
        )
    if post_rank == 3:
        return (
            f"Use this later in the stack as the payoff clip because the {focus} beat turns attention into a clearer next "
            f"step once the first two posts have already built context."
        )
    if review_rank == 1:
        return (
            f"This scores like a lead clip, but it works better later because the {focus} beat pays off harder once "
            f"the audience already has context."
        )
    return (
        f"Hold this for later in the stack because the {focus} moment works best as a {packaging_angle} follow-through "
        f"after the stronger openers have already earned attention."
    )


def transcript_signal_score(transcript_excerpt: str | None, *, source_context: Optional[SourceContext]) -> int:
    excerpt = (transcript_excerpt or "").strip()
    if not excerpt:
        return 0
    score = min(score_excerpt(excerpt) // 5, 10)
    if source_context and source_context.selection_strategy == "transcript":
        score += 4
    return min(score, 14)


def caption_variants_for(*, clip: ClipResult, target_platform: str, packaging_angle: str) -> dict[str, str]:
    base = clip.caption.strip() or clip.hook.strip() or clip.title.strip()
    hook = clip.hook.strip() or clip.title.strip() or "this clip"
    platform = target_platform.lower()
    platform_tag = "tiktok" if "tik" in platform else "reels" if "insta" in platform else "shorts"

    return {
        "viral": f"{hook} {clip.cta_suggestion or 'Comment if you want part 2.'}".strip(),
        "story": f"{base} Start with the setup, then land the payoff in one clean beat.".strip(),
        "educational": f"{base} Save this {platform_tag} breakdown and test the {packaging_angle} angle yourself.".strip(),
        "controversial": f"{hook} Most people will disagree with this take, which is exactly why it spreads.".strip(),
    }


def parse_timestamp(value: str) -> int:
    parts = [int(part) for part in value.split(":") if part.isdigit()]
    if len(parts) == 2:
        return (parts[0] * 60) + parts[1]
    if len(parts) == 3:
        return (parts[0] * 3600) + (parts[1] * 60) + parts[2]
    return 0


def compact_phrase(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9']+", value)
    return " ".join(words[:3]).lower() if words else "this clip"


def str_or_default(value: object, fallback: str) -> str:
    if isinstance(value, str):
        normalized = value.strip()
        if normalized:
            return normalized
    return fallback


def clamp_score(value: object, fallback: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        parsed = fallback
    return max(0, min(parsed, 100))


def clamp_confidence(value: object, fallback: float) -> float:
    try:
        parsed = float(value)
    except Exception:
        parsed = fallback
    return max(0.0, min(parsed, 1.0))
