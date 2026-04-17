from __future__ import annotations

import asyncio
import importlib.util
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path
from urllib.parse import urlparse

from fastapi import HTTPException, Request

from ..core.config import Settings
from ..job_store import JobStore
from ..models.schemas import ClipBatchResponse, ProcessRequest, ProcessingSummary, TrendItem, TrendsResponse
from ..models.user import UserRecord
from ..services.ai_service import generate_clip_copy
from ..services.attention_compiler import compile_attention
from ..services.entitlements import EntitlementContext, UsageStore
from ..services.platform_store import PlatformStore
from ..services.video_service import build_source_context, export_social_ready_clips, ffmpeg_available
from ..trends import fetch_public_trends, trends_timestamp

logger = logging.getLogger("uvicorn.error")


def enforce_api_key(request: Request, settings: Settings) -> None:
    if not settings.api_key_secret:
        return

    provided_key = request.headers.get(settings.api_key_header_name)
    if provided_key != settings.api_key_secret:
        raise HTTPException(status_code=401, detail="Invalid API key")


def dependency_health(settings: Settings) -> dict[str, bool]:
    return {
        "ffmpeg": ffmpeg_available(settings),
        "yt_dlp": importlib.util.find_spec("yt_dlp") is not None,
        "openai_key_present": bool(settings.openai_api_key),
        "whop_key_present": bool(settings.whop_api_key),
        "google_key_present": bool(settings.google_api_key or settings.youtube_api_key),
        "tiktok_keys_present": bool(settings.tiktok_client_key and settings.tiktok_client_secret),
        "meta_keys_present": bool(
            (settings.meta_app_id and settings.meta_app_secret)
            or settings.facebook_page_access_token
            or settings.instagram_access_token
        ),
    }


def detect_platform(video_url: str) -> str:
    hostname = urlparse(video_url).netloc.lower()
    if not hostname:
        return "Upload"
    if "youtube" in hostname or "youtu.be" in hostname:
        return "YouTube"
    if "tiktok" in hostname:
        return "TikTok"
    if "instagram" in hostname:
        return "Instagram"
    if "twitch" in hostname:
        return "Twitch"
    return "Web"


async def get_live_trends() -> TrendsResponse:
    trends = await fetch_public_trends()
    return TrendsResponse(
        status="success",
        updated_at=trends_timestamp(),
        trends=trends,
    )


async def build_clip_response(
    *,
    settings: Settings,
    request_id: str,
    request: ProcessRequest,
    public_base_url: str,
    route_path: str,
    entitlement: EntitlementContext,
    current_user: UserRecord | None = None,
    platform_store: PlatformStore | None = None,
    campaign_id: str | None = None,
    source_path: str | None = None,
    progress_callback: Callable[[str], Awaitable[None]] | None = None,
) -> ClipBatchResponse:
    video_url = str(request.video_url)
    target_platform = request.target_platform or "TikTok"
    candidate_limit = min(max(entitlement.plan.feature_flags.clip_limit, 20), 40)
    trend_context_response = await get_live_trends()
    trend_context: list[TrendItem] = trend_context_response.trends
    source_context = None
    fallback_reason: str | None = None
    yt_dlp_is_available = importlib.util.find_spec("yt_dlp") is not None
    ffmpeg_is_available = ffmpeg_available(settings)

    logger.info(
        "clip_response_start request_id=%s route=%s ffmpeg=%s yt_dlp=%s base_url=%s",
        request_id,
        route_path,
        ffmpeg_is_available,
        yt_dlp_is_available,
        public_base_url,
    )

    await emit_progress(progress_callback, "Ingesting source media, transcript windows, and candidate moments.")

    can_process_source = ffmpeg_is_available and (bool(source_path) or yt_dlp_is_available)

    if can_process_source:
        try:
            source_context = await asyncio.to_thread(
                build_source_context,
                settings=settings,
                request_id=request_id,
                video_url=video_url,
                public_base_url=public_base_url,
                source_path=source_path,
                max_candidates=candidate_limit,
                source_type=request.source_type,
                upload_content_type=request.upload_content_type,
            )
            logger.info(
                "source_context_ready request_id=%s route=%s built=%s clip_seeds=%s strategy=%s title=%s",
                request_id,
                route_path,
                True,
                len(source_context.clip_seeds),
                source_context.selection_strategy,
                source_context.title,
            )
            await emit_progress(progress_callback, "Scoring breakout moments and building ranked packaging angles.")
        except Exception as error:
            fallback_reason = str(error)
            logger.warning(
                "source_context_fallback request_id=%s route=%s built=%s reason=%s",
                request_id,
                route_path,
                False,
                fallback_reason,
            )
            await emit_progress(progress_callback, "Source ingest failed. Falling back to lightweight packaging.")
            source_context = None
    else:
        fallback_reason = "missing runtime dependencies"
        logger.warning(
            "source_context_skipped request_id=%s route=%s built=%s ffmpeg=%s yt_dlp=%s reason=%s",
            request_id,
            route_path,
            False,
            ffmpeg_is_available,
            yt_dlp_is_available,
            fallback_reason,
        )
        await emit_progress(progress_callback, "Runtime dependencies are limited. Building a lightweight clip pack.")

    clips, provider_used = await generate_clip_copy(
        settings=settings,
        video_url=video_url,
        target_platform=target_platform,
        selected_trend=request.selected_trend,
        content_angle=request.content_angle,
        trend_context=trend_context,
        source_context=source_context,
    )
    await emit_progress(progress_callback, "Compiling attention signals, ranking clips, and generating angles.")
    clips, compiler_mode = await compile_attention(
        settings=settings,
        clips=clips,
        target_platform=target_platform,
        selected_trend=request.selected_trend,
        content_angle=request.content_angle,
        source_context=source_context,
    )
    edited_assets_created = 0
    if source_context:
        await emit_progress(progress_callback, "Rendering vertical exports, overlays, and preview assets.")
        clips, edited_assets_created = await asyncio.to_thread(
            export_social_ready_clips,
            settings=settings,
            clip_results=clips,
            clip_seeds=source_context.clip_seeds,
            request_id=request_id,
            public_base_url=public_base_url,
        )
        logger.info(
            "clip_exports_complete request_id=%s route=%s clip_seeds=%s exports=%s",
            request_id,
            route_path,
            len(source_context.clip_seeds),
            edited_assets_created,
        )
    else:
        logger.info(
            "clip_mock_fallback request_id=%s route=%s reason=%s",
            request_id,
            route_path,
            fallback_reason or "real pipeline unavailable",
        )

    clips = apply_plan_feature_flags(
        clips=clips,
        entitlement=entitlement,
    )

    await emit_progress(progress_callback, "Finalizing ranked clip pack and delivery bundle.")
    processing_mode = source_context.processing_mode if source_context else "mock"
    source_title = source_context.title if source_context else None
    source_duration_seconds = source_context.duration_seconds if source_context else None
    assets_created = len([clip for clip in clips if clip.clip_url])
    selection_strategy = source_context.selection_strategy if source_context else "timeline"
    source_type = source_context.source_type if source_context else (request.source_type or ("video_upload" if source_path else "url"))
    source_platform = source_context.source_platform if source_context else detect_platform(video_url)
    preview_asset_url = resolve_preview_asset_url(clips=clips, source_context=source_context)
    download_asset_url = resolve_download_asset_url(clips=clips, source_context=source_context, entitlement=entitlement)
    thumbnail_url = resolve_thumbnail_url(clips=clips, source_context=source_context)

    response = ClipBatchResponse(
        request_id=request_id,
        video_url=request.video_url,
        status="success",
        source_type=source_type,
        source_title=source_title,
        source_platform=source_platform,
        transcript=source_context.transcript if source_context else None,
        visual_summary=source_context.visual_summary if source_context else None,
        preview_asset_url=preview_asset_url,
        download_asset_url=download_asset_url,
        thumbnail_url=thumbnail_url,
        processing_summary=ProcessingSummary(
            plan_name=entitlement.plan.name,
            credits_remaining=entitlement.credits_remaining,
            estimated_turnaround="ready now" if assets_created else settings.default_turnaround,
            recommended_next_step=(
                "Open the edited clip, test it with real creators, then use those results to justify paid tiers."
                if assets_created
                else "No valid clips were produced. Try a different source video or a longer recording."
            ),
            ai_provider=compiler_mode or provider_used,
            target_platform=target_platform,
            trend_used=request.selected_trend,
            sources_considered=sorted({item.source for item in trend_context}),
            processing_mode=processing_mode,
            selection_strategy=selection_strategy,
            source_title=source_title,
            source_type=source_type,
            source_duration_seconds=source_duration_seconds,
            assets_created=assets_created,
            edited_assets_created=edited_assets_created,
            feature_flags=entitlement.plan.feature_flags,
        ),
        trend_context=trend_context[:6],
        clips=clips,
    )
    if platform_store is not None:
        response = platform_store.persist_clip_batch(
            request_id=request_id,
            user_id=current_user.id if current_user else entitlement.user_id,
            campaign_id=campaign_id,
            response=response,
            local_asset_paths=resolve_local_asset_paths(settings=settings, request_id=request_id, clips=clips),
        )
    return response


def apply_plan_feature_flags(
    *,
    clips: list,
    entitlement: EntitlementContext,
) -> list:
    clip_limit = max(entitlement.plan.feature_flags.clip_limit, 1)
    alt_hooks_unlocked = bool(entitlement.plan.feature_flags.alt_hooks)
    exports_unlocked = bool(entitlement.plan.feature_flags.premium_exports)
    ranked = sorted(
        clips,
        key=lambda clip: (clip.rank or 999, -(clip.score or 0)),
    )
    visible = ranked[:clip_limit]
    gated = []
    for clip in visible:
        preview_url = clip.edited_clip_url or clip.clip_url or clip.raw_clip_url
        download_url = preview_url if exports_unlocked else None
        caption_variants = clip.caption_variants or {}
        if not alt_hooks_unlocked:
            caption_variants = {"viral": caption_variants.get("viral") or clip.caption}

        # Ensure all intelligence fields are always populated with meaningful fallbacks
        why_this_matters = (
            clip.why_this_matters
            or clip.reason
            or "Strong pacing, clear payoff, and creator-ready packaging."
        )
        cta_suggestion = clip.cta_suggestion or "Prompt viewers to comment or follow."
        thumbnail_text = clip.thumbnail_text or clip.title or (clip.hook[:40] if clip.hook else "Best Clip")
        platform_fit = clip.platform_fit or "Optimized for fast short-form viewing."
        packaging_angle = clip.packaging_angle or "value"
        hook_variants = clip.hook_variants if clip.hook_variants else [clip.hook]
        if not alt_hooks_unlocked:
            hook_variants = hook_variants[:1]
        if not caption_variants:
            caption_variants = {"viral": clip.caption}

        gated.append(
            clip.model_copy(
                update={
                    "hook_variants": hook_variants,
                    "caption_variants": caption_variants,
                    "timestamp_start": clip.start_time,
                    "timestamp_end": clip.end_time,
                    "duration": derive_clip_duration_seconds(clip.start_time, clip.end_time),
                    "transcript": clip.transcript_excerpt,
                    "cta": cta_suggestion,
                    "cta_suggestion": cta_suggestion,
                    "preview_url": preview_url,
                    "download_url": download_url,
                    "thumbnail_url": clip.preview_image_url,
                    "why_this_matters": why_this_matters,
                    "thumbnail_text": thumbnail_text,
                    "platform_fit": platform_fit,
                    "packaging_angle": packaging_angle,
                }
            )
        )
    return gated


def derive_clip_duration_seconds(start_time: str | None, end_time: str | None) -> int | None:
    start = parse_timestamp(start_time)
    end = parse_timestamp(end_time)
    if start is None or end is None or end <= start:
        return None
    return max(int(end - start), 1)


def parse_timestamp(value: str | None) -> int | None:
    if not value:
        return None
    try:
        parts = [int(float(part)) for part in value.split(":")]
    except Exception:
        return None
    if len(parts) == 2:
        minutes, seconds = parts
        return (minutes * 60) + seconds
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return (hours * 3600) + (minutes * 60) + seconds
    return None


def resolve_preview_asset_url(*, clips: list, source_context) -> str | None:
    if clips:
        first = clips[0]
        return first.preview_url or first.preview_image_url or first.clip_url or first.raw_clip_url
    if source_context:
        return source_context.preview_asset_url or source_context.thumbnail_url
    return None


def resolve_download_asset_url(*, clips: list, source_context, entitlement: EntitlementContext) -> str | None:
    if not entitlement.plan.feature_flags.premium_exports:
        return None
    if clips:
        first = clips[0]
        return first.download_url or first.edited_clip_url or first.clip_url or first.raw_clip_url
    if source_context:
        return source_context.download_asset_url
    return None


def resolve_thumbnail_url(*, clips: list, source_context) -> str | None:
    if clips:
        first = clips[0]
        return first.thumbnail_url or first.preview_image_url
    if source_context:
        return source_context.thumbnail_url
    return None


async def emit_progress(
    progress_callback: Callable[[str], Awaitable[None]] | None,
    message: str,
) -> None:
    if progress_callback is None:
        return
    await progress_callback(message)


async def run_job(
    *,
    settings: Settings,
    job_store: JobStore,
    usage_store: UsageStore,
    job_id: str,
    request: ProcessRequest,
    public_base_url: str,
    route_path: str,
    entitlement: EntitlementContext,
    current_user: UserRecord | None = None,
    platform_store: PlatformStore | None = None,
    campaign_id: str | None = None,
    source_path: str | None = None,
) -> None:
    await job_store.update(
        job_id,
        status="processing",
        message="Queue accepted. Starting source ingest.",
    )

    try:
        response = await build_clip_response(
            settings=settings,
            request_id=job_id,
            request=request,
            public_base_url=public_base_url,
            route_path=route_path,
            entitlement=entitlement,
            current_user=current_user,
            platform_store=platform_store,
            campaign_id=campaign_id,
            source_path=source_path,
            progress_callback=lambda message: job_store.update(
                job_id,
                status="processing",
                message=message,
            ),
        )
        await job_store.complete(job_id, response)
        if platform_store is not None:
            platform_store.update_job(
                job_id=job_id,
                status="completed",
                message="Clips ready.",
                response_json=response.model_dump_json(),
            )
    except Exception as error:  # pragma: no cover
        usage_store.release(subject=entitlement.subject, usage_day=entitlement.usage_day)
        await job_store.fail(job_id, str(error))
        if platform_store is not None:
            platform_store.update_job(
                job_id=job_id,
                status="failed",
                message=str(error),
            )


def resolve_local_asset_paths(*, settings: Settings, request_id: str, clips: list) -> dict[str, str]:
    request_dir = Path(settings.generated_assets_dir) / request_id
    mapping: dict[str, str] = {}
    for clip in clips:
        candidate_names = [
            f"{clip.id}.mp4",
            f"{clip.id}_raw.mp4",
            f"{clip.id}.mov",
            f"{clip.id}_raw.mov",
        ]
        for candidate_name in candidate_names:
            candidate_path = request_dir / candidate_name
            if candidate_path.exists():
                mapping[clip.id] = str(candidate_path)
                break
    return mapping
