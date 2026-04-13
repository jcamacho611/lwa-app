from __future__ import annotations

import asyncio
import importlib.util
import logging
from collections.abc import Awaitable, Callable
from urllib.parse import urlparse

from fastapi import HTTPException, Request

from ..core.config import Settings
from ..job_store import JobStore
from ..models.schemas import ClipBatchResponse, ProcessRequest, ProcessingSummary, TrendItem, TrendsResponse
from ..services.ai_service import generate_clip_copy
from ..services.attention_compiler import compile_attention
from ..services.entitlements import EntitlementContext, UsageStore
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
    progress_callback: Callable[[str], Awaitable[None]] | None = None,
) -> ClipBatchResponse:
    video_url = str(request.video_url)
    target_platform = request.target_platform or "TikTok"
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

    if ffmpeg_is_available and yt_dlp_is_available:
        try:
            source_context = await asyncio.to_thread(
                build_source_context,
                settings=settings,
                request_id=request_id,
                video_url=video_url,
                public_base_url=public_base_url,
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
        trend_context=trend_context,
        source_context=source_context,
    )
    await emit_progress(progress_callback, "Compiling attention signals, ranking clips, and generating angles.")
    clips, compiler_mode = await compile_attention(
        settings=settings,
        clips=clips,
        target_platform=target_platform,
        selected_trend=request.selected_trend,
        source_context=source_context,
    )
    clips = apply_plan_feature_flags(
        clips=clips,
        entitlement=entitlement,
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

    await emit_progress(progress_callback, "Finalizing ranked clip pack and delivery bundle.")
    processing_mode = source_context.processing_mode if source_context else "mock"
    source_title = source_context.title if source_context else None
    source_duration_seconds = source_context.duration_seconds if source_context else None
    assets_created = len([clip for clip in clips if clip.clip_url])
    selection_strategy = source_context.selection_strategy if source_context else "timeline"

    return ClipBatchResponse(
        request_id=request_id,
        video_url=request.video_url,
        status="success",
        source_platform=detect_platform(video_url),
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
            source_duration_seconds=source_duration_seconds,
            assets_created=assets_created,
            edited_assets_created=edited_assets_created,
            feature_flags=entitlement.plan.feature_flags,
        ),
        trend_context=trend_context[:6],
        clips=clips,
    )


def apply_plan_feature_flags(
    *,
    clips: list,
    entitlement: EntitlementContext,
) -> list:
    return clips


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
            progress_callback=lambda message: job_store.update(
                job_id,
                status="processing",
                message=message,
            ),
        )
        await job_store.complete(job_id, response)
    except Exception as error:  # pragma: no cover
        usage_store.release(subject=entitlement.subject, usage_day=entitlement.usage_day)
        await job_store.fail(job_id, str(error))
