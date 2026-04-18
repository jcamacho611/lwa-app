from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Optional

from openai import OpenAI

from ..core.config import Settings
from ..models.schemas import ClipResult
from ..processor import SourceContext, score_excerpt
from .anthropic_service import (
    anthropic_available,
    generate_clip_packaging_with_opus,
    generate_clip_packaging_with_sonnet,
)
from .ai_service import resolve_attention_mode

logger = logging.getLogger("uvicorn.error")

ALLOWED_PACKAGING_ANGLES = {"shock", "story", "value", "controversy", "curiosity"}


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

    return {
        "score": score,
        "virality_score": score,
        "confidence": confidence,
        "reason": reason,
        "why_this_matters": str_or_default(entry.get("why_this_matters"), str(heuristic["why_this_matters"])),
        "confidence_score": clamp_score(entry.get("confidence_score"), fallback=int(heuristic["confidence_score"])),
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
    emotional = keyword_score(combined_text, {"love", "hate", "pain", "fear", "crazy", "wild", "shocking", "secret"}) + punctuation_score(combined_text)
    story = keyword_score(combined_text, {"story", "when", "then", "realized", "started", "moment", "because"})
    curiosity = keyword_score(combined_text, {"why", "how", "stop", "before", "nobody", "most", "exact", "mistake"})
    replay = keyword_score(combined_text, {"exact", "step", "mistake", "never", "always", "pattern", "shortcut", "convert"})
    clarity = clarity_score(combined_text)
    retention = duration_score(clip.start_time, clip.end_time)
    transcript_signal = transcript_signal_score(clip.transcript_excerpt, source_context=source_context)

    packaging_angle = heuristic_packaging_angle(
        combined_text=combined_text,
        preferred_angle=content_angle,
        emotional=emotional,
        story=story,
        curiosity=curiosity,
        replay=replay,
    )
    score = max(
        55,
        min(
            int(
                round(
                    38
                    + (retention * 0.24)
                    + (clarity * 0.22)
                    + (emotional * 0.18)
                    + (curiosity * 0.18)
                    + (replay * 0.18)
                    + transcript_signal
                )
            ),
            99,
        ),
    )
    confidence = clamp_confidence(
        None,
        fallback=min(
            0.97,
            max(
                0.45,
                (score / 100.0)
                + (0.04 if clip.transcript_excerpt else 0.0)
                + (0.02 if index == 1 else 0.0)
                + min(transcript_signal / 200.0, 0.05),
            ),
        ),
    )
    focus = selected_trend or compact_phrase(clip.title or clip.hook)

    return {
        "score": score,
        "virality_score": score,
        "confidence": confidence,
        "confidence_score": max(int(round(confidence * 100)), 55),
        "reason": (
            f"This clip is strong because the {packaging_angle} framing creates a fast hook and a clear payoff for {target_platform} viewers."
        ),
        "why_this_matters": why_this_matters_for(
            clip=clip,
            target_platform=target_platform,
            packaging_angle=packaging_angle,
            post_rank=index,
            review_rank=index,
        ),
        "hook_variants": [
            f"Why {focus} is the {packaging_angle} angle most creators are missing.",
            f"The {focus} moment worth posting first on {target_platform}.",
            f"If you test one {packaging_angle} hook from this source, make it this one.",
        ],
        "caption_variants": caption_variants_for(
            clip=clip,
            target_platform=target_platform,
            packaging_angle=packaging_angle,
        ),
        "packaging_angle": packaging_angle,
        "platform_fit": platform_fit_for(target_platform, packaging_angle),
        "thumbnail_text": thumbnail_text_for(clip.title, clip.hook),
        "cta_suggestion": cta_for(target_platform, index),
        "caption_style": caption_style_for(target_platform, packaging_angle),
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
    if isinstance(value, list):
        variants = [str(item).strip() for item in value if str(item).strip()]
        if variants:
            return variants[:5]
    return fallback


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


def thumbnail_text_for(title: str, hook: str) -> str:
    source = hook if len(hook.strip()) >= len(title.strip()) else title
    words = [
        word
        for word in re.findall(r"[A-Za-z0-9']+", source)
        if word.lower() not in {"the", "and", "that", "with", "this", "your", "from", "into"}
    ]
    return " ".join(words[:4]).title() or "Best Clip"


def cta_for(target_platform: str, rank: int) -> str:
    platform = target_platform.lower()
    if rank == 1:
        return "Ask viewers if they want the full breakdown next."
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
    if angle in {"shock", "curiosity"}:
        return 0
    if angle == "controversy":
        return 1
    if angle == "value":
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
    focus = compact_phrase(clip.transcript_excerpt or clip.title or clip.hook)
    platform_name = target_platform or "short-form"
    if post_rank == 1:
        return (
            f"Open with this because the {focus} payoff lands quickly and gives {platform_name} viewers "
            f"the strongest first impression with a {packaging_angle} frame."
        )
    if post_rank == 2:
        return (
            f"Use this second because it deepens the {packaging_angle} angle after the opener and keeps the stack "
            f"feeling intentional for {platform_name} viewers."
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
