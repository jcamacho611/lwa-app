from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models.schemas import ClipBatchResponse, ClipResult, ProcessingSummary, ProcessRequest
from .entitlements import EntitlementContext


@dataclass(frozen=True)
class FallbackClipResult:
    status: str
    reason: str
    transcript_segments: list[dict[str, Any]]
    moments: list[dict[str, Any]]
    clips: list[ClipResult]


def transcript_fallback(*, source_label: str, total_seconds: int = 90) -> list[dict[str, Any]]:
    window_seconds = 30
    segment_count = max(total_seconds // window_seconds, 1)
    return [
        {
            "index": index,
            "start_seconds": (index - 1) * window_seconds,
            "end_seconds": index * window_seconds,
            "text": f"Segment {index}: {source_label}",
        }
        for index in range(1, segment_count + 1)
    ]


def moment_fallback(*, total_seconds: int = 90, count: int = 3) -> list[dict[str, Any]]:
    window_seconds = 30
    safe_count = max(min(count, 3), 1)
    if safe_count == 1:
        starts = [0]
    else:
        max_start = max(total_seconds - window_seconds, 0)
        step = max_start / max(safe_count - 1, 1)
        starts = [int(round(step * index)) for index in range(safe_count)]

    return [
        {
            "index": index,
            "start_seconds": start,
            "end_seconds": min(start + window_seconds, total_seconds),
            "label": f"Fallback moment {index}",
        }
        for index, start in enumerate(starts, start=1)
    ]


def caption_fallback(text: str) -> str:
    return " ".join(text.split()) or "Fallback clip package generated from the available source context."


def hook_fallback(text: str) -> str:
    words = caption_fallback(text).split()
    return " ".join(words[:7]) or "Start with the strongest available moment"


def build_fallback_clip_result(*, source_label: str, reason: str, clip_count: int = 3) -> FallbackClipResult:
    transcript_segments = transcript_fallback(source_label=source_label)
    moments = moment_fallback(count=clip_count)
    clips: list[ClipResult] = []

    for index, moment in enumerate(moments, start=1):
        transcript_text = transcript_segments[min(index - 1, len(transcript_segments) - 1)]["text"]
        hook = hook_fallback(transcript_text)
        caption = caption_fallback(transcript_text)
        score = max(64 - ((index - 1) * 4), 52)
        clips.append(
            ClipResult(
                id=f"fallback_{index}",
                title=f"Fallback strategy clip {index}",
                hook=hook,
                caption=caption,
                score=score,
                reason=reason,
                why_this_matters="LWA preserved a usable strategy package when the full render pipeline was unavailable.",
                first_three_seconds_assessment="Open directly on the strongest available claim or visual beat.",
                category="fallback",
                format="strategy",
                is_strategy_only=True,
                strategy_only=True,
                is_rendered=False,
                rendered=False,
                fallback_reason=reason,
                post_rank=index,
                best_post_order=index,
                virality_score=score,
                rank=index,
                target_platform="TikTok",
                transcript_excerpt=caption,
                thumbnail_text=hook,
                cta_suggestion="Use this as a strategy-only draft, then retry rendering with a direct upload.",
                hook_variants=[
                    hook,
                    f"Why this moment still matters: {hook}",
                    f"Start here before the full render is ready: {hook}",
                ],
                caption_variants={
                    "primary": caption,
                    "short": hook,
                    "story": caption,
                },
                packaging_angle="degraded_strategy_fallback",
                duration=30,
                duration_seconds=30,
                timestamp_start=str(moment["start_seconds"]),
                timestamp_end=str(moment["end_seconds"]),
                transcript=caption,
                cta="Retry with a direct upload when ready.",
                package_text=caption,
                export_ready=False,
                request_id=None,
            )
        )

    return FallbackClipResult(
        status="degraded",
        reason=reason,
        transcript_segments=transcript_segments,
        moments=moments,
        clips=clips,
    )


def build_degraded_clip_response(
    *,
    request_id: str,
    request: ProcessRequest,
    entitlement: EntitlementContext,
    reason: str,
    error_class: str,
    trend_context: list[Any],
) -> ClipBatchResponse:
    source_value = (
        (request.video_url or "").strip()
        or (request.source_url or "").strip()
        or (request.prompt or "").strip()
        or (request.text_prompt or "").strip()
        or (request.campaign_goal or "").strip()
        or "source"
    )
    source_type = (request.source_type or "unknown").strip() or "unknown"
    target_platform = request.target_platform or "TikTok"
    clip_count = min(max(int(request.clip_count or entitlement.plan.feature_flags.clip_limit or 3), 1), 3)
    fallback = build_fallback_clip_result(source_label=source_value, reason=reason, clip_count=clip_count)
    clips = [
        clip.model_copy(update={"request_id": request_id, "target_platform": target_platform})
        for clip in fallback.clips
    ]

    return ClipBatchResponse(
        request_id=request_id,
        video_url=source_value,
        status=fallback.status,
        status_reason=reason,
        source_type=source_type,
        source_title=None,
        source_platform=None,
        transcript="\n".join(segment["text"] for segment in fallback.transcript_segments),
        visual_summary="Strategy-only degraded fallback. No rendered media was produced.",
        preview_asset_url=None,
        download_asset_url=None,
        thumbnail_url=None,
        processing_summary=ProcessingSummary(
            plan_code=entitlement.plan.code,
            plan_name=entitlement.plan.name,
            credits_remaining=entitlement.credits_remaining,
            estimated_turnaround="strategy fallback ready now",
            recommended_next_step="Retry with a direct upload or shorter source if rendered output is required.",
            ai_provider="deterministic_fallback",
            target_platform=target_platform,
            platform_decision="manual" if request.target_platform else "auto",
            recommended_platform=target_platform,
            platform_recommendation_reason="Fallback keeps the package usable without claiming render success.",
            trend_used=request.selected_trend,
            sources_considered=[],
            processing_mode="degraded",
            selection_strategy="deterministic_fallback",
            fallback_reason=reason,
            source_type=source_type,
            source_count=1,
            clip_count_requested=request.clip_count,
            clip_count_allowed=clip_count,
            clip_count_returned=len(clips),
            generation_mode="degraded_fallback",
            workflow_stage="strategy_only",
            assets_created=0,
            raw_assets_created=0,
            edited_assets_created=0,
            rendered_clip_count=0,
            strategy_only_clip_count=len(clips),
            thumbnail_count=0,
            free_preview_unlocked=True,
            persistence_requires_signup=False,
            upgrade_prompt=None,
            feature_flags=entitlement.plan.feature_flags,
        ),
        trend_context=trend_context,
        clips=clips,
        scripts=None,
    )
