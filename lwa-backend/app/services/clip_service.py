from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
from urllib.parse import urlparse

from fastapi import HTTPException, Request

from ..core.config import Settings
from ..job_store import JobStore
from ..models.schemas import ClipBatchResponse, ProcessRequest, ProcessingSummary, TrendItem, TrendsResponse
from ..services.ai_service import generate_clip_copy
from ..services.video_service import build_source_context, export_social_ready_clips, ffmpeg_available
from ..trends import fetch_public_trends, trends_timestamp


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
) -> ClipBatchResponse:
    video_url = str(request.video_url)
    target_platform = request.target_platform or "TikTok"
    trend_context_response = await get_live_trends()
    trend_context: list[TrendItem] = trend_context_response.trends
    source_context = None

    try:
        source_context = await asyncio.to_thread(
            build_source_context,
            settings=settings,
            request_id=request_id,
            video_url=video_url,
            public_base_url=public_base_url,
        )
    except Exception:
        source_context = None

    clips, provider_used = await generate_clip_copy(
        settings=settings,
        video_url=video_url,
        target_platform=target_platform,
        selected_trend=request.selected_trend,
        trend_context=trend_context,
        source_context=source_context,
    )

    edited_assets_created = 0
    if source_context:
        clips, edited_assets_created = await asyncio.to_thread(
            export_social_ready_clips,
            settings=settings,
            clip_results=clips,
            clip_seeds=source_context.clip_seeds,
            request_id=request_id,
            public_base_url=public_base_url,
        )

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
            plan_name=settings.default_plan_name,
            credits_remaining=settings.default_credits_remaining,
            estimated_turnaround="ready now" if assets_created else settings.default_turnaround,
            recommended_next_step=(
                "Open the edited clip, test it with real creators, then use those results to justify paid tiers."
                if assets_created
                else "No valid clips were produced. Try a different source video or a longer recording."
            ),
            ai_provider=provider_used,
            target_platform=target_platform,
            trend_used=request.selected_trend,
            sources_considered=sorted({item.source for item in trend_context}),
            processing_mode=processing_mode,
            selection_strategy=selection_strategy,
            source_title=source_title,
            source_duration_seconds=source_duration_seconds,
            assets_created=assets_created,
            edited_assets_created=edited_assets_created,
        ),
        trend_context=trend_context[:6],
        clips=clips,
    )


async def run_job(
    *,
    settings: Settings,
    job_store: JobStore,
    job_id: str,
    request: ProcessRequest,
    public_base_url: str,
) -> None:
    await job_store.update(
        job_id,
        status="processing",
        message="Downloading source, cutting clips, and generating copy.",
    )

    try:
        response = await build_clip_response(
            settings=settings,
            request_id=job_id,
            request=request,
            public_base_url=public_base_url,
        )
        await job_store.complete(job_id, response)
    except Exception as error:  # pragma: no cover
        await job_store.fail(job_id, str(error))

