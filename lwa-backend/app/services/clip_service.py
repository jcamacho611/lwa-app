from __future__ import annotations

import asyncio
import importlib.util
import json
import logging
import re
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import HTTPException, Request

from ..core.config import Settings
from ..job_store import JobStore
from ..models.schemas import (
    CampaignRequirementCheck,
    CaptionModes,
    ClipBatchResponse,
    ClipResult,
    EditPlan,
    ExportBundle,
    ProcessRequest,
    ProcessingSummary,
    ScoreBreakdown,
    TrendItem,
    TrendsResponse,
)
from ..models.user import UserRecord
from ..services.ai_service import generate_clip_copy
from ..services.asset_retention import cleanup_generated_assets_nonfatal_for_settings
from ..services.attention_compiler import compile_attention
from ..services.caption_artifacts import create_caption_artifacts
from ..services.clip_status_store import register_clip_batch
from ..services.confidence_engine import build_confidence_label, resolve_confidence_score
from ..services.director_brain import build_director_brain_plan
from ..services.entitlements import EntitlementContext, UsageStore
from ..services.event_log import emit_event
from ..services.intelligence_data_core import get_intelligence_core
from ..services.output_builder import OutputBuilder
from ..services.platform_store import PlatformStore
from ..services.render_quality import evaluate_render_quality
from ..services.render_jobs import queue_preview_render
from ..services.shot_planner import build_shot_plan_for_clip
from ..services.source_ingest import (
    build_strategy_source_context,
    infer_source_type,
    source_type_uses_media_pipeline,
    source_value_for_request,
)
from ..services.trend_intelligence import build_trend_intelligence
from ..services.video_service import build_source_context, export_social_ready_clips, ffmpeg_available
from ..services.visual_generation_service import visual_generation_available, visual_generation_status
from ..services.visual_render_provider import (
    RENDER_PROVIDER_PUBLIC_ID,
    RENDERED_BY_PUBLIC_LABEL,
    VisualRenderPayload,
    VisualRenderProviderResult,
    render_visual_clip,
    resolve_visual_render_provider_state,
)
from ..services.whop_service import build_whop_provider_health, describe_whop_verification_state
from ..style_engine import build_script_pack
from ..trends import fetch_public_trends, trends_timestamp

logger = logging.getLogger("uvicorn.error")
_last_generated_asset_prune_at = 0.0
DEFAULT_EXPORT_PROFILE = "tiktok_reels_9_16"
SHORTS_EXPORT_PROFILE = "shorts_9_16"
PODCAST_EXPORT_PROFILE = "podcast_clean_9_16"
STRATEGY_EXPORT_PROFILE = "strategy_only_package"


def enforce_api_key(request: Request, settings: Settings) -> None:
    # Skip API key enforcement in free launch mode for public testing
    if settings.free_launch_mode:
        return
        
    if not settings.api_key_secret:
        return

    provided_key = (request.headers.get(settings.api_key_header_name) or "").strip()
    allowed_keys = {
        settings.api_key_secret.strip(),
        *settings.pro_api_keys,
        *settings.scale_api_keys,
    }
    if provided_key not in allowed_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")


def dependency_health(settings: Settings) -> dict[str, object]:
    whop_state = describe_whop_verification_state(settings)
    return {
        "ffmpeg": ffmpeg_available(settings),
        "yt_dlp": importlib.util.find_spec("yt_dlp") is not None,
        "openai_key_present": bool(settings.openai_api_key),
        "anthropic_key_present": bool(settings.anthropic_api_key),
        "whop_key_present": bool(settings.whop_api_key),
        "whop_verification_enabled": whop_state.enabled,
        "whop_verification_configured": whop_state.configured,
        "google_key_present": bool(settings.google_api_key or settings.youtube_api_key),
        "tiktok_keys_present": bool(settings.tiktok_client_key and settings.tiktok_client_secret),
        "meta_keys_present": bool(
            (settings.meta_app_id and settings.meta_app_secret)
            or settings.facebook_page_access_token
            or settings.instagram_access_token
        ),
        "visual_generation_enabled": bool(settings.visual_generation_enabled),
        "visual_generation_configured": visual_generation_available(settings),
    }


def provider_health(settings: Settings) -> dict[str, dict[str, object]]:
    return {
        "openai": {
            "configured": bool(settings.openai_api_key),
            "selected_when_available": settings.ai_provider in {"auto", "openai"},
            "status": "configured" if settings.openai_api_key else "missing-key",
        },
        "anthropic": {
            "configured": bool(settings.enable_anthropic and settings.anthropic_api_key),
            "selected_when_available": settings.ai_provider in {"auto", "anthropic"}
            or settings.premium_reasoning_provider == "anthropic",
            "status": "configured"
            if settings.enable_anthropic and settings.anthropic_api_key
            else "disabled" if not settings.enable_anthropic else "missing-key",
        },
        "whop": build_whop_provider_health(settings),
        "visual_generation": visual_generation_status(settings),
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
    source_value = source_value_for_request(request)
    video_url = str(request.video_url or request.source_url or "")
    normalized_source_type = infer_source_type(request)
    requested_clip_limit, clip_limit_upgrade_reason = resolve_requested_clip_limit(
        requested_clip_count=request.clip_count,
        plan_clip_limit=entitlement.plan.feature_flags.clip_limit,
        hard_max_clip_limit=max(
            getattr(
                settings,
                "high_volume_max_clips" if getattr(settings, "enable_high_volume_clips", False) else "max_clip_limit",
                entitlement.plan.feature_flags.clip_limit,
            ),
            1,
        ),
        enable_high_volume_clips=bool(getattr(settings, "enable_high_volume_clips", False)),
        high_volume_max_clips=max(getattr(settings, "high_volume_max_clips", getattr(settings, "max_clip_limit", 12)), 1),
        max_clips_per_job=max(getattr(settings, "max_clips_per_job", getattr(settings, "max_clip_limit", 12)), 1),
    )
    clip_count_requested = max(int(request.clip_count), 1) if request.clip_count is not None else entitlement.plan.feature_flags.clip_limit
    clip_count_allowed = requested_clip_limit
    candidate_limit = min(max(requested_clip_limit, 20), 40)
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
    if request.clip_count and request.clip_count > 12:
        emit_event(
            settings=settings,
            event="high_volume_requested",
            request_id=request_id,
            plan_code=entitlement.plan.code,
            subject_source=entitlement.subject_source,
            metadata={
                "clip_count_requested": request.clip_count,
                "clip_count_allowed": clip_count_allowed,
                "high_volume_enabled": bool(getattr(settings, "enable_high_volume_clips", False)),
            },
        )
    if clip_limit_upgrade_reason:
        emit_event(
            settings=settings,
            event="clip_count_clamped",
            request_id=request_id,
            plan_code=entitlement.plan.code,
            subject_source=entitlement.subject_source,
            metadata={
                "clip_count_requested": clip_count_requested,
                "clip_count_allowed": clip_count_allowed,
                "reason": clip_limit_upgrade_reason,
            },
        )
    await asyncio.to_thread(maybe_prune_generated_assets, settings)

    await emit_progress(progress_callback, "Ingesting source media, transcript windows, and candidate moments.")

    can_process_source = (
        ffmpeg_is_available
        and source_type_uses_media_pipeline(
            normalized_source_type,
            has_source_path=bool(source_path),
            source_url=video_url,
        )
        and (bool(source_path) or (bool(video_url) and yt_dlp_is_available))
    )

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
                source_type=normalized_source_type,
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
            # Use enhanced fallback service for graceful degradation
            from .source_fallback import source_fallback_service
            fallback_service = source_fallback_service(settings)
            fallback_result = await fallback_service.handle_source_failure(
                request=request,
                error=error,
                source_url=video_url
            )
            
            # Convert fallback result to SourceContext
            from ..processor import SourceContext
            source_context = SourceContext(**fallback_result.source_context)
            fallback_reason = fallback_result.fallback_reason
            
            logger.info(
                "source_context_fallback_enhanced request_id=%s route=%s strategy=%s reason=%s",
                request_id,
                route_path,
                fallback_result.strategy.value,
                fallback_reason,
            )
            await emit_progress(progress_callback, f"Source ingest failed. Using {fallback_result.strategy.value} fallback.")
    else:
        # Use enhanced fallback service even for strategy-only sources
        from .source_fallback import source_fallback_service
        fallback_service = source_fallback_service(settings)
        
        # Create a mock error for strategy-only processing
        class StrategyOnlyError(Exception):
            pass
        
        fallback_result = await fallback_service.handle_source_failure(
            request=request,
            error=StrategyOnlyError("Strategy-only source type"),
            source_url=video_url
        )
        
        # Convert fallback result to SourceContext
        from ..processor import SourceContext
        source_context = SourceContext(**fallback_result.source_context)
        fallback_reason = fallback_result.fallback_reason
        
        logger.info(
            "source_context_strategy_only_enhanced request_id=%s route=%s strategy=%s reason=%s",
            request_id,
            route_path,
            fallback_result.strategy.value,
            fallback_reason,
        )
        await emit_progress(progress_callback, f"Building {fallback_result.strategy.value} package from provided context.")

    source_platform = source_context.source_platform if source_context else detect_platform(video_url)
    auto_target_platform, recommendation_reason, recommended_content_type, recommended_output_style = (
        recommend_platform_strategy(
            source_context=source_context,
            detected_source_platform=source_platform,
            selected_trend=request.selected_trend,
            content_angle=request.content_angle,
        )
    )
    manual_platform_override = bool(request.target_platform)
    target_platform = request.target_platform or auto_target_platform

    clips, provider_used = await generate_clip_copy(
        settings=settings,
        video_url=source_value,
        target_platform=target_platform,
        selected_trend=request.selected_trend,
        content_angle=request.content_angle,
        trend_context=trend_context,
        source_context=source_context,
        premium_reasoning=bool(entitlement.plan.feature_flags.priority_processing),
    )
    await emit_progress(progress_callback, "Compiling attention signals, ranking clips, and generating angles.")
    clips, compiler_mode = await compile_attention(
        settings=settings,
        clips=clips,
        target_platform=target_platform,
        selected_trend=request.selected_trend,
        content_angle=request.content_angle,
        source_context=source_context,
        premium_reasoning=bool(entitlement.plan.feature_flags.priority_processing),
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
        requested_clip_limit=requested_clip_limit,
    )
    clips, director_brain_summary = await apply_director_brain_foundation(
        settings=settings,
        clips=clips,
        target_platform=target_platform,
    )
    clips = [clip.model_copy(update={"request_id": request_id}) for clip in clips]
    clips = attach_platform_caption_artifacts(
        settings=settings,
        clips=clips,
        request_id=request_id,
        public_base_url=public_base_url,
        target_platform=target_platform,
    )
    clips = attach_trend_and_evergreen_metadata(
        clips=clips,
        selected_trend=request.selected_trend,
        trend_context=trend_context,
    )
    source_title = source_context.title if source_context else None
    source_type = source_context.source_type if source_context else (normalized_source_type or ("video_upload" if source_path else "url"))
    clips = apply_operational_metadata(
        clips=clips,
        request_id=request_id,
        source_label=source_title or source_type or "Source 1",
        request=request,
        entitlement=entitlement,
        target_platform=target_platform,
    )
    local_asset_paths = resolve_local_asset_paths(settings=settings, request_id=request_id, clips=clips)
    register_clip_batch(request_id=request_id, clips=clips, local_asset_paths=local_asset_paths)
    for clip in clips:
        if clip.preview_url:
            continue
        local_asset_path = local_asset_paths.get(clip.id)
        if not local_asset_path:
            continue
        queue_preview_render(
            settings=settings,
            request_id=request_id,
            clip_id=clip.id,
            public_base_url=public_base_url,
            local_asset_path=local_asset_path,
            title_text=clip.hook or clip.title,
            subtitle_text=clip.transcript_excerpt or clip.caption,
        )

    await emit_progress(progress_callback, "Finalizing ranked clip pack and delivery bundle.")
    processing_mode = source_context.processing_mode if source_context else "mock"
    source_duration_seconds = source_context.duration_seconds if source_context else None
    assets_created = len([clip for clip in clips if clip.clip_url])
    selection_strategy = source_context.selection_strategy if source_context else "timeline"
    preview_asset_url = resolve_preview_asset_url(clips=clips, source_context=source_context)
    download_asset_url = resolve_download_asset_url(clips=clips, source_context=source_context, entitlement=entitlement)
    thumbnail_url = resolve_thumbnail_url(clips=clips, source_context=source_context)
    preview_ready_count = len([clip for clip in clips if clip.preview_url or clip.edited_clip_url or clip.clip_url or clip.raw_clip_url])
    raw_assets_created = len([clip for clip in clips if clip.raw_clip_url or clip.clip_url])
    rendered_clip_count = int(director_brain_summary["rendered_clip_count"])
    strategy_only_clip_count = int(director_brain_summary["strategy_only_clip_count"])
    export_ready_count = len([clip for clip in clips if clip.download_url])
    thumbnail_count = len([clip for clip in clips if clip.thumbnail_preview_url or clip.preview_image_url or clip.thumbnail_url])
    export_manifest = (
        OutputBuilder(settings).create_export_manifest(
            request_id=request_id,
            clips=[clip.model_dump() for clip in clips],
        )
        if clips
        else None
    )
    script_pack = build_script_pack(
        source_title=source_title,
        transcript=source_context.transcript if source_context else None,
        target_platform=target_platform,
        clip_phrases=[
            phrase
            for clip in clips[:6]
            for phrase in [clip.transcript_excerpt or clip.hook or clip.title]
            if phrase
        ],
    )

    response = ClipBatchResponse(
        request_id=request_id,
        video_url=source_value,
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
            plan_code=entitlement.plan.code,
            plan_name=entitlement.plan.name,
            credits_remaining=entitlement.credits_remaining,
            estimated_turnaround="preview ready now" if preview_ready_count else settings.default_turnaround,
            recommended_next_step=build_recommended_next_step(
                preview_ready_count=preview_ready_count,
                rendered_clip_count=rendered_clip_count,
                export_ready_count=export_ready_count,
                entitlement=entitlement,
            ),
            ai_provider=compiler_mode or provider_used,
            target_platform=target_platform,
            platform_decision="manual" if manual_platform_override else "auto",
            recommended_platform=auto_target_platform,
            platform_recommendation_reason=recommendation_reason,
            recommended_content_type=recommended_content_type,
            recommended_output_style=recommended_output_style,
            manual_platform_override=manual_platform_override,
            trend_used=request.selected_trend,
            sources_considered=sorted({item.source for item in trend_context}),
            processing_mode=processing_mode,
            selection_strategy=selection_strategy,
            fallback_reason=fallback_reason,
            source_title=source_title,
            source_type=source_type,
            source_duration_seconds=source_duration_seconds,
            source_count=1,
            clip_count_requested=clip_count_requested,
            clip_count_allowed=clip_count_allowed,
            clip_count_returned=len(clips),
            batch_mode=False,
            batch_id=None,
            generation_mode="campaign_pack" if request.campaign_brief else "single_source",
            workflow_stage=determine_workflow_stage(
                rendered_clip_count=rendered_clip_count,
                strategy_only_clip_count=strategy_only_clip_count,
                export_ready_count=export_ready_count,
            ),
            upgrade_reason=resolve_upgrade_reason(
                clip_limit_upgrade_reason=clip_limit_upgrade_reason,
                campaign_requested=bool(request.campaign_brief),
                campaign_feature_enabled=bool(entitlement.plan.feature_flags.campaign_mode),
            ),
            campaign_mode=bool(request.campaign_brief) and bool(entitlement.plan.feature_flags.campaign_mode),
            campaign_goal=request.campaign_goal,
            allowed_platforms=list(request.allowed_platforms or []),
            campaign_readiness=build_campaign_readiness_summary(
                campaign_requested=bool(request.campaign_brief),
                campaign_enabled=bool(entitlement.plan.feature_flags.campaign_mode),
                rendered_clip_count=rendered_clip_count,
                strategy_only_clip_count=strategy_only_clip_count,
            ),
            campaign_notes=build_campaign_notes(
                request=request,
                campaign_enabled=bool(entitlement.plan.feature_flags.campaign_mode),
            ),
            assets_created=assets_created,
            raw_assets_created=raw_assets_created,
            edited_assets_created=edited_assets_created,
            visual_engine_enabled=bool(director_brain_summary["visual_engine_enabled"]),
            visual_engine_attempted_count=int(director_brain_summary["visual_engine_attempted_count"]),
            visual_engine_ready_count=int(director_brain_summary["visual_engine_ready_count"]),
            visual_engine_failed_count=int(director_brain_summary["visual_engine_failed_count"]),
            rendered_clip_count=rendered_clip_count,
            strategy_only_clip_count=strategy_only_clip_count,
            thumbnail_count=thumbnail_count,
            thumbnail_generation_enabled=bool(thumbnail_count or ffmpeg_is_available),
            available_caption_styles=available_caption_styles(),
            default_caption_style=default_caption_style(clips),
            export_bundle_available=bool(export_manifest),
            export_bundle_format="json" if export_manifest else None,
            export_bundle_manifest_url=export_manifest["download_url"] if export_manifest else None,
            export_bundle_notes=build_export_bundle_notes(
                export_manifest=export_manifest,
                rendered_clip_count=rendered_clip_count,
                strategy_only_clip_count=strategy_only_clip_count,
            ),
            available_export_profiles=available_export_profiles(clips=clips, target_platform=target_platform),
            default_export_profile=default_export_profile(clips=clips, target_platform=target_platform),
            render_quality_summary=build_render_quality_summary(clips),
            bulk_export_ready=bool(export_manifest),
            manifest_url=export_manifest["download_url"] if export_manifest else None,
            free_preview_unlocked=entitlement.plan.code == "free",
            persistence_requires_signup=current_user is None,
            upgrade_prompt=build_upgrade_prompt(entitlement=entitlement, current_user=current_user),
            feature_flags=entitlement.plan.feature_flags,
        ),
        trend_context=trend_context[:6],
        clips=clips,
        scripts=script_pack,
    )
    if platform_store is not None:
        response = platform_store.persist_clip_batch(
            request_id=request_id,
            user_id=current_user.id if current_user else entitlement.subject,
            campaign_id=campaign_id,
            response=response,
            local_asset_paths=local_asset_paths,
        )
    emit_event(
        settings=settings,
        event="generation_completed",
        request_id=request_id,
        plan_code=entitlement.plan.code,
        subject_source=entitlement.subject_source,
        metadata={
            "target_platform": target_platform,
            "source_type": source_type,
            "clip_count": len(clips),
            "assets_created": assets_created,
            "edited_assets_created": edited_assets_created,
            "ai_provider": compiler_mode or provider_used,
            "processing_mode": processing_mode,
        },
    )
    if assets_created > 0:
        emit_event(
            settings=settings,
            event="rendered_asset_created",
            request_id=request_id,
            plan_code=entitlement.plan.code,
            subject_source=entitlement.subject_source,
            metadata={
                "target_platform": target_platform,
                "assets_created": assets_created,
                "rendered_clip_count": rendered_clip_count,
            },
        )
    elif clips:
        emit_event(
            settings=settings,
            event="strategy_package_created",
            request_id=request_id,
            plan_code=entitlement.plan.code,
            subject_source=entitlement.subject_source,
            metadata={
                "target_platform": target_platform,
                "clip_count": len(clips),
                "strategy_only_clip_count": strategy_only_clip_count,
                "fallback_reason": fallback_reason or "render_unavailable",
            },
        )
    return response


async def apply_director_brain_foundation(
    *,
    settings: Settings,
    clips: list[ClipResult],
    target_platform: str,
) -> tuple[list[ClipResult], dict[str, int | bool]]:
    provider_state = resolve_visual_render_provider_state(settings)
    max_render_attempts = max(int(getattr(settings, "visual_engine_max_renders_per_request", 1)), 0)
    visual_engine_attempted_count = 0
    visual_engine_ready_count = 0
    visual_engine_failed_count = 0
    enriched: list[ClipResult] = []

    for clip in clips:
        try:
            director_plan = build_director_brain_plan(clip, target_platform=target_platform)
            shot_plan = build_shot_plan_for_clip(clip, target_platform=target_platform)
            render_result: VisualRenderProviderResult | None = None
            if not clip_has_rendered_media(clip):
                if provider_state == "disabled":
                    render_result = VisualRenderProviderResult(
                        provider_state="disabled",
                        message="Visual rendering is turned off. Keep the clip strategy-only and preserve the shot plan.",
                    )
                elif provider_state == "missing-key":
                    render_result = VisualRenderProviderResult(
                        provider_state="missing-key",
                        message="Visual rendering key is missing. Keep the strategy-only clip and surface a recover render action.",
                    )
                elif visual_engine_attempted_count < max_render_attempts:
                    render_result = await render_visual_clip(
                        settings=settings,
                        payload=VisualRenderPayload(
                            clip_id=clip.id,
                            title=clip.title,
                            hook=clip.hook,
                            caption=clip.caption,
                            shot_plan=[step.model_dump() for step in shot_plan.shot_plan],
                            visual_engine_prompt=shot_plan.visual_engine_prompt,
                            motion_prompt=shot_plan.motion_prompt,
                            duration_seconds=clip.duration,
                            target_platform=target_platform,
                            source_clip_url=clip.clip_url or clip.raw_clip_url or clip.preview_url,
                        ),
                    )
                    if render_result.attempted:
                        visual_engine_attempted_count += 1

            evaluation = evaluate_render_quality(clip=clip, render_result=render_result)
            update: dict[str, object] = {
                **director_plan.as_clip_update(clip),
                **shot_plan.as_clip_update(),
                **evaluation.as_clip_update(),
                "render_provider": clip.render_provider or RENDER_PROVIDER_PUBLIC_ID,
                "rendered_by": clip.rendered_by or RENDERED_BY_PUBLIC_LABEL,
                "render_status": clip.render_status or ("ready" if clip_has_rendered_media(clip) else "pending"),
            }
            if render_result:
                if render_result.preview_url:
                    update["preview_url"] = render_result.preview_url
                if render_result.asset_url:
                    update["clip_url"] = render_result.asset_url
                if render_result.download_url:
                    update["download_url"] = render_result.download_url
                if render_result.error:
                    update["render_error"] = render_result.error
                if render_result.attempted:
                    update["render_status"] = "ready" if render_result.success else "failed"

            updated_clip = clip.model_copy(update=update)
            if updated_clip.visual_engine_status == "ready_now":
                visual_engine_ready_count += 1
            if updated_clip.visual_engine_status in {"recoverable", "render_failed"}:
                visual_engine_failed_count += 1
            enriched.append(updated_clip)
        except Exception as error:
            logger.warning(
                "director_brain_enrichment_failed clip_id=%s reason=%s",
                clip.id,
                error,
            )
            enriched.append(
                clip.model_copy(
                    update={
                        "render_provider": clip.render_provider or RENDER_PROVIDER_PUBLIC_ID,
                        "rendered_by": clip.rendered_by or (RENDERED_BY_PUBLIC_LABEL if clip_has_rendered_media(clip) else None),
                    }
                )
            )

    rendered_clip_count = len([clip for clip in enriched if clip_has_rendered_media(clip)])
    strategy_only_clip_count = max(len(enriched) - rendered_clip_count, 0)
    return enriched, {
        "visual_engine_enabled": bool(getattr(settings, "visual_engine_enabled", False)),
        "visual_engine_attempted_count": visual_engine_attempted_count,
        "visual_engine_ready_count": visual_engine_ready_count,
        "visual_engine_failed_count": visual_engine_failed_count,
        "rendered_clip_count": rendered_clip_count,
        "strategy_only_clip_count": strategy_only_clip_count,
    }


def apply_plan_feature_flags(
    *,
    clips: list,
    entitlement: EntitlementContext,
    requested_clip_limit: int | None = None,
) -> list:
    plan_clip_limit = max(entitlement.plan.feature_flags.clip_limit, 1)
    clip_limit = min(max(requested_clip_limit or plan_clip_limit, 1), plan_clip_limit)
    alt_hooks_unlocked = bool(entitlement.plan.feature_flags.alt_hooks)
    packaging_profiles_unlocked = bool(entitlement.plan.feature_flags.packaging_profiles)
    exports_unlocked = bool(entitlement.plan.feature_flags.premium_exports)
    ranked = sorted(
        clips,
        key=lambda clip: (
            clip.post_rank or clip.best_post_order or clip.rank or 999,
            -(clip.score or 0),
            clip.rank or 999,
        ),
    )
    visible = ranked[:clip_limit]
    gated = []
    for clip in visible:
        preview_url = clip.preview_url or clip.edited_clip_url or clip.clip_url or clip.raw_clip_url
        download_url = preview_url if exports_unlocked else None
        caption_variants = clip.caption_variants or {}
        if not alt_hooks_unlocked:
            caption_variants = {"viral": caption_variants.get("viral") or clip.caption}
        elif not packaging_profiles_unlocked:
            caption_variants = {"viral": caption_variants.get("viral") or clip.caption}

        confidence_score = resolve_confidence_score(clip)
        confidence_label = build_confidence_label(
            {
                "confidence_score": confidence_score,
                "score": clip.score,
                "confidence": clip.confidence,
            }
        )
        packaging_angle = clip.packaging_angle or "value"
        caption_style = clip.caption_style or "Short-form native"
        post_order = clip.post_rank or clip.best_post_order or clip.rank or 1
        # Ensure all intelligence fields are always populated with meaningful fallbacks.
        why_this_matters = (
            clip.why_this_matters
            or clip.reason
            or build_plan_fallback_why_this_matters(
                clip=clip,
                post_order=post_order,
                packaging_angle=packaging_angle,
            )
        )
        cta_suggestion = clip.cta_suggestion or build_plan_fallback_cta(
            clip=clip,
            post_order=post_order,
            packaging_angle=packaging_angle,
        )
        thumbnail_text = clip.thumbnail_text or build_plan_fallback_thumbnail(clip)
        platform_fit = clip.platform_fit or build_plan_fallback_platform_fit(
            clip=clip,
            packaging_angle=packaging_angle,
        )
        hook_variants = clip.hook_variants if clip.hook_variants else build_plan_fallback_hook_variants(
            clip=clip,
            post_order=post_order,
            packaging_angle=packaging_angle,
        )
        if not alt_hooks_unlocked:
            hook_variants = hook_variants[:1]
        if not caption_variants:
            caption_variants = {"viral": clip.caption}
        if not packaging_profiles_unlocked:
            caption_style = "Standard short-form"
        caption_modes = build_caption_modes(
            clip=clip,
            caption_variants=caption_variants,
            caption_style=caption_style,
            packaging_angle=packaging_angle,
        )
        edit_plan = build_edit_plan(
            clip=clip,
            caption_style=caption_style,
            thumbnail_text=thumbnail_text,
            packaging_angle=packaging_angle,
            post_order=post_order,
        )
        export_bundle = build_export_bundle(
            clip=clip,
            preview_url=preview_url,
            download_url=download_url,
            post_order=post_order,
            packaging_angle=packaging_angle,
            thumbnail_text=thumbnail_text,
            cta_suggestion=cta_suggestion,
        )
        is_rendered = bool(preview_url)
        render_status = clip.render_status or ("ready" if is_rendered else "pending")
        rendered_status = clip.rendered_status or build_clip_rendered_status(
            preview_url=clip.preview_url,
            edited_clip_url=clip.edited_clip_url,
            clip_url=clip.clip_url,
            raw_clip_url=clip.raw_clip_url,
            render_status=render_status,
        )
        hook_score = clip.hook_score or max(min((clip.score or 70) + 4, 100), 40)
        render_readiness_score = clip.render_readiness_score or clip.render_quality_score or (78 if is_rendered else 42)
        score_breakdown = clip.score_breakdown or ScoreBreakdown(
            hook_score=hook_score,
            retention_score=clip.score or 70,
            emotional_spike_score=max((clip.score or 70) - 8, 0),
            clarity_score=clip.score or 70,
            platform_fit_score=max((clip.score or 70) - 4, 0),
            visual_energy_score=max((clip.score or 70) - 12, 0),
            audio_energy_score=max((clip.score or 70) - 10, 0),
            controversy_score=max((clip.score or 70) - 18, 0),
            educational_value_score=max((clip.score or 70) - 14, 0),
            share_comment_score=max((clip.score or 70) - 16, 0),
            render_readiness_score=render_readiness_score,
            commercial_value_score=max((clip.score or 70) - 20, 0),
        )
        scoring_explanation = (
            clip.scoring_explanation
            or "Score led by hook strength, clarity, and platform fit. Confirm render readiness before posting."
        )
        first_three_seconds_assessment = clip.first_three_seconds_assessment or build_plan_first_three_seconds_assessment(clip.hook)
        hook_strength = clip.hook_strength or build_plan_hook_strength_label(hook_score)
        retention_reason = clip.retention_reason or build_plan_retention_reason(
            clip=clip,
            rendered_status=rendered_status,
            hook_score=hook_score,
            render_readiness_score=render_readiness_score,
        )
        campaign_requirement_checks = build_campaign_requirement_checks(
            clip=clip,
            export_bundle=export_bundle,
            is_rendered=is_rendered,
            hook_score=hook_score,
            confidence_score=confidence_score,
            render_readiness_score=render_readiness_score,
            score_breakdown=score_breakdown,
            thumbnail_text=thumbnail_text,
            cta_suggestion=cta_suggestion,
        )
        approval_state = build_approval_state(
            campaign_requirement_checks=campaign_requirement_checks,
            is_rendered=is_rendered,
            render_readiness_score=render_readiness_score,
        )

        gated.append(
            clip.model_copy(
                update={
                    "confidence_score": confidence_score,
                    "confidence_label": confidence_label,
                    "hook_variants": hook_variants,
                    "caption_variants": caption_variants,
                    "caption_style": caption_style,
                    "caption_modes": caption_modes,
                    "edit_plan": edit_plan,
                    "export_bundle": export_bundle,
                    "post_rank": post_order,
                    "best_post_order": clip.best_post_order or post_order,
                    "timestamp_start": clip.start_time,
                    "timestamp_end": clip.end_time,
                    "duration": derive_clip_duration_seconds(clip.start_time, clip.end_time),
                    "transcript": clip.transcript_excerpt,
                    "cta": cta_suggestion,
                    "cta_suggestion": cta_suggestion,
                    "hook_score": hook_score,
                    "hook_strength": hook_strength,
                    "first_three_seconds_assessment": first_three_seconds_assessment,
                    "retention_reason": retention_reason,
                    "preview_url": preview_url,
                    "download_url": download_url,
                    "thumbnail_url": clip.thumbnail_url or clip.preview_image_url,
                    "is_rendered": is_rendered,
                    "is_strategy_only": not is_rendered,
                    "render_status": render_status,
                    "rendered_status": rendered_status,
                    "export_ready": bool(preview_url or download_url),
                    "asset_manifest": build_clip_asset_manifest(
                        clip.model_copy(
                            update={
                                "preview_url": preview_url,
                                "download_url": download_url,
                                "rendered_status": rendered_status,
                            }
                        )
                    ),
                    "package_text": build_clip_package_text(
                        clip.model_copy(
                            update={
                                "post_rank": post_order,
                                "thumbnail_text": thumbnail_text,
                                "cta_suggestion": cta_suggestion,
                                "platform_fit": platform_fit,
                                "rendered_status": rendered_status,
                            }
                        )
                    ),
                    "render_readiness_score": render_readiness_score,
                    "score_breakdown": score_breakdown,
                    "scoring_explanation": scoring_explanation,
                    "campaign_requirement_checks": campaign_requirement_checks,
                    "approval_state": approval_state,
                    "approved": approval_state == "approved",
                    "why_this_matters": why_this_matters,
                    "thumbnail_text": thumbnail_text,
                    "platform_fit": platform_fit,
                    "packaging_angle": packaging_angle,
                }
            )
        )
    return gated


def build_caption_modes(
    *,
    clip,
    caption_variants: dict[str, str],
    caption_style: str,
    packaging_angle: str,
) -> CaptionModes:
    base_caption = clip.caption or caption_variants.get("viral") or ""
    return CaptionModes(
        primary=base_caption,
        short=shorten_caption(base_caption),
        story=caption_variants.get("story") or base_caption,
        educational=caption_variants.get("educational") or base_caption,
        controversial=caption_variants.get("controversial") or base_caption,
        style=caption_style,
        angle=packaging_angle,
    )


def build_edit_plan(
    *,
    clip,
    caption_style: str,
    thumbnail_text: str,
    packaging_angle: str,
    post_order: int,
) -> EditPlan:
    opening = "Start on the strongest payoff line in the first beat."
    if packaging_angle == "story":
        opening = "Open on the setup beat, then cut quickly to the turning point."
    elif packaging_angle == "controversy":
        opening = "Start on the disagreement line and keep the tension visible immediately."
    elif packaging_angle == "curiosity":
        opening = "Open on the question or tease before revealing the explanation."
    elif packaging_angle == "shock":
        opening = "Open on the interruption moment and keep the pacing tight."

    return EditPlan(
        opening_beat=opening,
        pacing=caption_style or "Short-form native",
        visual_focus=thumbnail_text or clip.title or "Lead moment",
        overlay_plan=clip.hook,
        posting_role=posting_role_label(post_order),
    )


def build_export_bundle(
    *,
    clip,
    preview_url: str | None,
    download_url: str | None,
    post_order: int,
    packaging_angle: str,
    thumbnail_text: str,
    cta_suggestion: str,
) -> ExportBundle:
    return ExportBundle(
        post_order=post_order,
        post_sequence_label=posting_role_label(post_order),
        packaging_angle=packaging_angle,
        thumbnail_text=thumbnail_text or clip.title or "Best Clip",
        cta=cta_suggestion or "Prompt viewers to comment or follow.",
        preview_ready=bool(preview_url),
        download_ready=bool(download_url),
        bundle_format="zip",
        manifest_ready=True,
        artifact_types=["package_json", "caption_txt", "subtitle_srt", "subtitle_vtt"],
    )


def attach_platform_caption_artifacts(
    *,
    settings: Settings,
    clips: list[ClipResult],
    request_id: str,
    public_base_url: str,
    target_platform: str | None,
) -> list[ClipResult]:
    enriched: list[ClipResult] = []
    for clip in clips:
        artifacts = create_caption_artifacts(
            settings=settings,
            public_base_url=public_base_url,
            request_id=request_id,
            clip=clip,
            target_platform=target_platform,
        )
        enriched.append(clip.model_copy(update=artifacts))
    return enriched


def attach_trend_and_evergreen_metadata(
    *,
    clips: list[ClipResult],
    selected_trend: str | None,
    trend_context: list[TrendItem],
) -> list[ClipResult]:
    enriched: list[ClipResult] = []
    for clip in clips:
        trend_fields = build_trend_intelligence(
            clip=clip,
            selected_trend=selected_trend,
            trend_context=trend_context,
        )
        enriched.append(clip.model_copy(update=trend_fields))
    return enriched


def build_campaign_requirement_checks(
    *,
    clip,
    export_bundle: ExportBundle,
    is_rendered: bool,
    hook_score: int,
    confidence_score: int,
    render_readiness_score: int,
    score_breakdown: ScoreBreakdown,
    thumbnail_text: str,
    cta_suggestion: str,
) -> list[CampaignRequirementCheck]:
    checks: list[CampaignRequirementCheck] = []

    if is_rendered and render_readiness_score >= 72:
        checks.append(
            CampaignRequirementCheck(
                status="pass",
                requirement="Playable asset",
                message="Rendered media is ready to publish now.",
            )
        )
    elif is_rendered:
        checks.append(
            CampaignRequirementCheck(
                status="warning",
                requirement="Playable asset",
                message="Rendered media exists, but first-frame pacing or readability should be reviewed before publishing.",
            )
        )
    else:
        checks.append(
            CampaignRequirementCheck(
                status="fail",
                requirement="Playable asset",
                message=clip.strategy_only_reason or "This clip is still strategy-only and needs recovery before it can ship as media.",
            )
        )

    if hook_score >= 70:
        checks.append(
            CampaignRequirementCheck(
                status="pass",
                requirement="Hook strength",
                message="The opener is strong enough to lead a post without extra setup.",
            )
        )
    elif hook_score >= 55:
        checks.append(
            CampaignRequirementCheck(
                status="warning",
                requirement="Hook strength",
                message="The opener is usable, but it could be sharper before this becomes a campaign lead.",
            )
        )
    else:
        checks.append(
            CampaignRequirementCheck(
                status="fail",
                requirement="Hook strength",
                message="The opener is too soft for a lead post and needs a stronger first line.",
            )
        )

    platform_fit_score = score_breakdown.platform_fit_score
    if platform_fit_score >= 80:
        checks.append(
            CampaignRequirementCheck(
                status="pass",
                requirement="Platform fit",
                message="Trim and packaging align well with the target platform.",
            )
        )
    elif platform_fit_score >= 65:
        checks.append(
            CampaignRequirementCheck(
                status="warning",
                requirement="Platform fit",
                message="The clip is close to platform-native, but pacing or packaging should be refined before campaign use.",
            )
        )
    else:
        checks.append(
            CampaignRequirementCheck(
                status="fail",
                requirement="Platform fit",
                message="This cut does not fit the target platform tightly enough yet.",
            )
        )

    package_parts = [bool((clip.caption or "").strip()), bool(thumbnail_text.strip()), bool(cta_suggestion.strip())]
    package_completeness = sum(1 for part in package_parts if part)
    if package_completeness == 3:
        checks.append(
            CampaignRequirementCheck(
                status="pass",
                requirement="Packaging completeness",
                message="Caption, thumbnail line, and CTA are all ready.",
            )
        )
    elif package_completeness == 2:
        checks.append(
            CampaignRequirementCheck(
                status="warning",
                requirement="Packaging completeness",
                message="Core packaging is mostly ready, but one delivery element still needs review.",
            )
        )
    else:
        checks.append(
            CampaignRequirementCheck(
                status="fail",
                requirement="Packaging completeness",
                message="This clip needs more packaging support before it is campaign-ready.",
            )
        )

    artifact_types = set((export_bundle.artifact_types if export_bundle else []) or [])
    has_caption_text = "caption_txt" in artifact_types or bool((clip.caption or "").strip())
    has_subtitle_files = "subtitle_srt" in artifact_types and "subtitle_vtt" in artifact_types
    has_burned_caption_delivery = bool(clip.preview_url or clip.edited_clip_url or clip.clip_url or clip.raw_clip_url) if is_rendered else True

    if has_caption_text and has_subtitle_files and has_burned_caption_delivery:
        checks.append(
            CampaignRequirementCheck(
                status="pass",
                requirement="Caption delivery",
                message="Caption text, subtitle files, and publishable media delivery are all in place.",
            )
        )
    elif has_caption_text and has_subtitle_files:
        checks.append(
            CampaignRequirementCheck(
                status="warning",
                requirement="Caption delivery",
                message="Caption files are ready, but the rendered delivery asset still needs review before campaign use.",
            )
        )
    else:
        checks.append(
            CampaignRequirementCheck(
                status="fail",
                requirement="Caption delivery",
                message="Caption artifacts are incomplete. Generate text and subtitle assets before this enters a campaign pack.",
            )
        )

    if confidence_score >= 80:
        checks.append(
            CampaignRequirementCheck(
                status="pass",
                requirement="Decision confidence",
                message="Signal confidence is strong enough to treat this ranking as campaign-safe.",
            )
        )
    elif confidence_score >= 65:
        checks.append(
            CampaignRequirementCheck(
                status="warning",
                requirement="Decision confidence",
                message="The ranking is usable, but this clip should be reviewed by an operator before campaign deployment.",
            )
        )
    else:
        checks.append(
            CampaignRequirementCheck(
                status="fail",
                requirement="Decision confidence",
                message="Signal confidence is too soft for campaign use without manual review and recutting.",
            )
        )

    return checks


def build_approval_state(
    *,
    campaign_requirement_checks: list[CampaignRequirementCheck],
    is_rendered: bool,
    render_readiness_score: int,
) -> str:
    fail_count = sum(1 for check in campaign_requirement_checks if check.status == "fail")
    warning_count = sum(1 for check in campaign_requirement_checks if check.status == "warning")

    if fail_count > 0:
        return "needs_edit"
    if warning_count > 0:
        return "needs_review"
    if is_rendered and render_readiness_score >= 72:
        return "approved"
    return "new"


def build_plan_fallback_why_this_matters(*, clip, post_order: int, packaging_angle: str) -> str:
    focus = compact_clip_focus(clip.transcript_excerpt or clip.hook or clip.title)
    if post_order == 1:
        return f"Post this first because the {focus} payoff is the clearest opener and gives the pack a strong {packaging_angle} frame."
    if post_order == 2:
        return f"Use this second because it extends the {focus} angle after the lead clip earns attention."
    return f"Use this later because the {focus} moment works best once viewers understand the angle and are ready to act."


def build_plan_fallback_cta(*, clip, post_order: int, packaging_angle: str) -> str:
    platform = infer_clip_platform(clip)
    if post_order == 1 and platform == "youtube":
        return "End by pointing viewers to the full breakdown."
    if post_order == 1 and platform == "instagram":
        return "End by asking viewers to save it before they forget the move."
    if post_order == 1 and platform == "tiktok":
        return "End by asking viewers if they want part two."
    if packaging_angle == "controversy":
        return "Close by asking viewers which side they agree with."
    if packaging_angle == "story":
        return "Close by asking viewers if they want the next part."
    return "Close by asking viewers what they want broken down next."


def build_plan_fallback_thumbnail(clip) -> str:
    words = clip_signal_words(clip.hook or clip.title or "", limit=3)
    if not words:
        return "Post First" if (clip.post_rank or clip.rank or 1) == 1 else "Best Clip"
    return " ".join(words).title()


def build_plan_fallback_platform_fit(*, clip, packaging_angle: str) -> str:
    platform = infer_clip_platform(clip)
    if platform == "youtube":
        return f"Shorts-ready structure with a clear {packaging_angle} setup and fast context."
    if platform == "instagram":
        return f"Reels-ready packaging with a polished {packaging_angle} frame and saveable payoff."
    if platform == "tiktok":
        return f"TikTok-friendly pacing with a {packaging_angle} opener and immediate payoff."
    return f"Short-form native packaging built around a {packaging_angle} angle."


def build_plan_fallback_hook_variants(*, clip, post_order: int, packaging_angle: str) -> list[str]:
    focus = compact_clip_focus(clip.transcript_excerpt or clip.hook or clip.title)
    if packaging_angle == "controversy":
        return [
            clip.hook,
            f"Most viewers are still wrong about {focus}.",
            f"The {focus} disagreement starts here.",
        ]
    if packaging_angle == "curiosity":
        return [
            clip.hook,
            f"The skipped detail behind {focus}.",
            "Most viewers miss this before the payoff.",
        ]
    if packaging_angle == "story":
        return [
            clip.hook,
            f"This is where {focus} turns.",
            "The payoff makes the whole story worth posting.",
        ]
    return [
        clip.hook,
        f"The useful part of {focus} starts here.",
        "Save this before posting the full breakdown.",
    ]


def infer_clip_platform(clip) -> str:
    text = " ".join(
        str(value or "").lower()
        for value in [clip.platform_fit, clip.caption_style, clip.title, clip.caption]
    )
    if "tiktok" in text:
        return "tiktok"
    if "instagram" in text or "reels" in text:
        return "instagram"
    if "youtube" in text or "shorts" in text:
        return "youtube"
    if "facebook" in text:
        return "facebook"
    return "short-form"


CLIP_STOP_WORDS = {
    "about",
    "after",
    "again",
    "because",
    "before",
    "breakdown",
    "clip",
    "from",
    "have",
    "into",
    "just",
    "post",
    "that",
    "this",
    "video",
    "watch",
    "when",
    "with",
    "your",
}


def compact_clip_focus(value: str) -> str:
    words = clip_signal_words(value, limit=3)
    return " ".join(words).lower() if words else "this angle"


def clip_signal_words(value: str, *, limit: int) -> list[str]:
    words: list[str] = []
    for word in re.findall(r"[A-Za-z0-9']+", value):
        normalized = word.strip("'").lower()
        if len(normalized) < 3 or normalized in CLIP_STOP_WORDS:
            continue
        if normalized in words:
            continue
        words.append(normalized)
        if len(words) >= limit:
            break
    return words


def shorten_caption(value: str, limit: int = 90) -> str:
    normalized = " ".join((value or "").split())
    if len(normalized) <= limit:
        return normalized
    trimmed = normalized[:limit].rsplit(" ", 1)[0].strip()
    return f"{trimmed}..." if trimmed else normalized[:limit]


def posting_role_label(post_order: int) -> str:
    if post_order == 1:
        return "post first"
    if post_order == 2:
        return "post second"
    if post_order == 3:
        return "post third"
    return "post later"


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


def clip_has_rendered_media(clip) -> bool:
    return bool(
        clip.preview_url
        or clip.edited_clip_url
        or clip.clip_url
        or clip.raw_clip_url
    )


def build_clip_rendered_status(
    *,
    preview_url: str | None,
    edited_clip_url: str | None,
    clip_url: str | None,
    raw_clip_url: str | None,
    render_status: str | None,
) -> str:
    normalized = str(render_status or "").strip().lower()
    if normalized == "failed":
        return "render_failed"
    if preview_url or edited_clip_url:
        return "rendered"
    if clip_url or raw_clip_url:
        return "raw_only"
    return "strategy_only"


def available_caption_styles() -> list[str]:
    try:
        presets = get_intelligence_core().caption_presets()
    except Exception:
        presets = []
    styles = [
        str(row.get("preset_name") or row.get("id") or "").strip()
        for row in presets
        if str(row.get("preset_name") or row.get("id") or "").strip()
    ]
    if styles:
        return styles
    return [
        "clean_editorial",
        "karaoke_bold",
        "block_punch",
        "beauty_minimal",
        "clinical_safe",
    ]


def default_caption_style(clips: list) -> str:
    for clip in clips:
        style = str(getattr(clip, "caption_preset", None) or getattr(clip, "caption_style", None) or "").strip()
        if style:
            return style
    styles = available_caption_styles()
    return styles[0] if styles else "clean_editorial"


def default_export_profile(*, clips: list, target_platform: str) -> str:
    if any((clip.rendered_status or clip.render_status) == "strategy_only" for clip in clips) and not any(
        clip_has_rendered_media(clip) for clip in clips
    ):
        return STRATEGY_EXPORT_PROFILE

    lowered = str(target_platform or "").strip().lower()
    if "youtube" in lowered:
        return SHORTS_EXPORT_PROFILE
    if "podcast" in lowered:
        return PODCAST_EXPORT_PROFILE
    return DEFAULT_EXPORT_PROFILE


def available_export_profiles(*, clips: list, target_platform: str) -> list[str]:
    profiles = [default_export_profile(clips=clips, target_platform=target_platform)]
    if PODCAST_EXPORT_PROFILE not in profiles and any(
        "podcast" in str(getattr(clip, "caption_style", "")).lower()
        or "podcast" in str(getattr(clip, "detected_category", "")).lower()
        for clip in clips
    ):
        profiles.append(PODCAST_EXPORT_PROFILE)
    if STRATEGY_EXPORT_PROFILE not in profiles:
        profiles.append(STRATEGY_EXPORT_PROFILE)
    return profiles


def build_render_quality_summary(clips: list) -> str:
    counts = {
        "rendered": 0,
        "raw_only": 0,
        "strategy_only": 0,
        "render_failed": 0,
    }
    for clip in clips:
        status = str(getattr(clip, "rendered_status", None) or getattr(clip, "render_status", None) or "strategy_only")
        if status not in counts:
            status = "strategy_only"
        counts[status] += 1
    return (
        f"rendered={counts['rendered']}, "
        f"raw_only={counts['raw_only']}, "
        f"strategy_only={counts['strategy_only']}, "
        f"render_failed={counts['render_failed']}"
    )


def build_clip_subtitle_url(clip) -> str | None:
    return clip.caption_vtt_url or clip.caption_srt_url or clip.caption_txt_url


def build_clip_thumbnail_preview_url(clip) -> str | None:
    return clip.preview_image_url or clip.thumbnail_url


def build_clip_captions_burned_in(clip) -> bool:
    existing = getattr(clip, "captions_burned_in", None)
    if existing is not None:
        return bool(existing)
    return False


def build_clip_resolution(*, clip, rendered_status: str) -> str | None:
    if getattr(clip, "resolution", None):
        return clip.resolution
    if getattr(clip, "aspect_ratio", None) == "9:16" or rendered_status == "rendered":
        return "720x1280"
    return None


def resolve_clip_export_profile(*, clip, target_platform: str, rendered_status: str) -> str:
    if rendered_status == "strategy_only":
        return STRATEGY_EXPORT_PROFILE
    lowered = str(target_platform or "").strip().lower()
    if "youtube" in lowered:
        return SHORTS_EXPORT_PROFILE
    if "podcast" in lowered or "podcast" in str(getattr(clip, "caption_style", "")).lower():
        return PODCAST_EXPORT_PROFILE
    return DEFAULT_EXPORT_PROFILE


def build_clip_render_notes(*, clip, rendered_status: str, subtitle_url: str | None) -> list[str]:
    notes: list[str] = []
    if subtitle_url:
        notes.append("Subtitle sidecar files are available for manual upload or review.")
    if rendered_status == "rendered":
        notes.append("Current rendered exports use overlay text support, not full phrase-by-phrase burned-in captions.")
    elif rendered_status == "raw_only":
        notes.append("A raw or lightly edited cut exists, but final polish is still optional.")
    elif rendered_status == "render_failed":
        notes.append("Rendering failed before a stable export was created.")
    else:
        notes.append("No playable media asset is available yet; treat this as strategy-only.")
    if getattr(clip, "recovery_recommendation", None):
        notes.append(str(clip.recovery_recommendation))
    return notes[:3]


def build_plan_first_three_seconds_assessment(hook: str | None) -> str:
    opener = " ".join((hook or "").strip().split())
    if not opener:
        return "The first three seconds need a stronger opening sentence."
    lowered = opener.lower()
    if lowered.startswith(("stop", "why", "how", "most", "this", "here")) or "?" in opener or "!" in opener:
        return f"The first three seconds open with a clear interrupt: {opener}"
    return f"The first three seconds are usable, but the opener would benefit from a sharper interrupt: {opener}"


def build_plan_hook_strength_label(hook_score: int) -> str:
    if hook_score >= 80:
        return "strong"
    if hook_score >= 60:
        return "workable"
    return "soft"


def build_plan_retention_reason(
    *,
    clip,
    rendered_status: str,
    hook_score: int,
    render_readiness_score: int,
) -> str:
    reasons: list[str] = []
    if hook_score >= 80:
        reasons.append("the opener lands quickly")
    elif hook_score >= 60:
        reasons.append("the opener is strong enough to test")
    if clip.transcript_excerpt:
        reasons.append("the clip has enough context to stand on its own")
    if clip.score and clip.score >= 80:
        reasons.append("the payoff is likely clear enough for short-form pacing")
    if rendered_status == "rendered":
        reasons.append("a playable export already exists")
    elif rendered_status == "raw_only":
        reasons.append("raw media exists but still needs final polish")
    elif rendered_status == "render_failed":
        reasons.append("render recovery is needed before this can act as proof")
    else:
        reasons.append("this is still a strategy-first recommendation")
    if render_readiness_score < 55:
        reasons.append("render readiness is still low")
    return "Retention case: " + ", ".join(reasons[:3]) + "."


def clip_record_needs_recovery(clip_record: dict[str, object]) -> bool:
    return not bool(
        clip_record.get("preview_url")
        or clip_record.get("edited_clip_url")
        or clip_record.get("clip_url")
        or clip_record.get("raw_clip_url")
    )


def resolve_requested_clip_limit(
    *,
    requested_clip_count: int | None,
    plan_clip_limit: int,
    hard_max_clip_limit: int,
    enable_high_volume_clips: bool = False,
    high_volume_max_clips: int | None = None,
    max_clips_per_job: int | None = None,
) -> tuple[int, str | None]:
    allowed_limit = min(max(plan_clip_limit, 1), max(hard_max_clip_limit, 1))
    if enable_high_volume_clips and high_volume_max_clips is not None:
        allowed_limit = min(allowed_limit, max(high_volume_max_clips, 1))
    if max_clips_per_job is not None:
        allowed_limit = min(allowed_limit, max(max_clips_per_job, 1))
    if requested_clip_count is None:
        return allowed_limit, None
    requested = max(int(requested_clip_count), 1)
    if requested > allowed_limit:
        return allowed_limit, f"Requested {requested} clips, but the current plan returns up to {allowed_limit}."
    return requested, None


def build_campaign_notes(*, request: ProcessRequest, campaign_enabled: bool) -> list[str]:
    if not request.campaign_brief:
        return []
    notes = [
        "Review campaign rules manually before posting.",
        "This package does not submit to any campaign automatically.",
        "Use rendered clips only where media assets are available.",
    ]
    if not campaign_enabled:
        notes.insert(0, "Campaign-ready packaging beyond the basic clip pack is gated to higher plans.")
    if request.forbidden_terms:
        notes.append("Check forbidden terms manually before publishing campaign copy.")
    return notes


def build_campaign_readiness_summary(
    *,
    campaign_requested: bool,
    campaign_enabled: bool,
    rendered_clip_count: int,
    strategy_only_clip_count: int,
) -> str | None:
    if not campaign_requested:
        return None
    if not campaign_enabled:
        return "ready_for_manual_review"
    if rendered_clip_count and not strategy_only_clip_count:
        return "ready_for_manual_review"
    if rendered_clip_count:
        return "needs_render_review"
    return "strategy_only"


def build_export_bundle_notes(
    *,
    export_manifest: dict[str, object] | None,
    rendered_clip_count: int,
    strategy_only_clip_count: int,
) -> list[str]:
    if not export_manifest:
        return []
    notes = ["Manifest generation succeeded for this clip pack."]
    if rendered_clip_count:
        notes.append("Playable clip URLs are included where render assets exist.")
    if strategy_only_clip_count:
        notes.append("Strategy-only clips stay in the manifest, but they require manual review before posting.")
    return notes


def resolve_upgrade_reason(
    *,
    clip_limit_upgrade_reason: str | None,
    campaign_requested: bool,
    campaign_feature_enabled: bool,
) -> str | None:
    if clip_limit_upgrade_reason:
        return clip_limit_upgrade_reason
    if campaign_requested and not campaign_feature_enabled:
        return "Campaign-ready packaging beyond the standard clip pack is available on higher plans."
    return None


def determine_workflow_stage(
    *,
    rendered_clip_count: int,
    strategy_only_clip_count: int,
    export_ready_count: int,
) -> str:
    if export_ready_count:
        return "delivered"
    if rendered_clip_count:
        return "rendered"
    if strategy_only_clip_count:
        return "packaged"
    return "ranked"


def build_clip_package_text(clip) -> str:
    status_label = {
        "rendered": "Rendered",
        "raw_only": "Raw cut",
        "render_failed": "Render failed",
        "strategy_only": "Strategy only",
    }.get(clip.rendered_status or clip.render_status or "strategy_only", "Strategy only")
    lines = [
        f"Title: {clip.title}",
        f"Status: {status_label}",
        f"Score: {clip.score}",
        f"Hook: {clip.hook}",
        f"Caption: {clip.caption}",
    ]
    if clip.thumbnail_text:
        lines.append(f"Thumbnail Text: {clip.thumbnail_text}")
    if clip.cta_suggestion:
        lines.append(f"CTA: {clip.cta_suggestion}")
    if clip.caption_style:
        lines.append(f"Caption Style: {clip.caption_style}")
    if getattr(clip, "export_profile", None):
        lines.append(f"Export Profile: {clip.export_profile}")
    lines.append(f"Post Order: {clip.post_rank or clip.rank or 1}")
    if clip.platform_fit:
        lines.append(f"Platform: {clip.platform_fit}")
    clip_url = clip.preview_url or clip.edited_clip_url or clip.clip_url or clip.raw_clip_url or clip.download_url
    if clip_url:
        lines.append(f"Clip URL: {clip_url}")
    return "\n".join(line for line in lines if line.split(":", 1)[1].strip())


def build_clip_asset_manifest(clip) -> dict[str, object]:
    manifest = {
        "clip_url": clip.clip_url,
        "raw_clip_url": clip.raw_clip_url,
        "edited_clip_url": clip.edited_clip_url,
        "preview_url": clip.preview_url,
        "preview_image_url": clip.preview_image_url,
        "thumbnail_preview_url": getattr(clip, "thumbnail_preview_url", None),
        "thumbnail_url": clip.thumbnail_url,
        "download_url": clip.download_url,
        "subtitle_url": getattr(clip, "subtitle_url", None),
        "caption_txt_url": clip.caption_txt_url,
        "caption_srt_url": clip.caption_srt_url,
        "caption_vtt_url": clip.caption_vtt_url,
        "captions_burned_in": getattr(clip, "captions_burned_in", False),
        "rendered_status": clip.rendered_status or clip.render_status,
        "render_quality": getattr(clip, "render_quality", None),
        "export_profile": getattr(clip, "export_profile", None),
    }
    return {key: value for key, value in manifest.items() if value is not None and value != ""}


def apply_operational_metadata(
    *,
    clips: list,
    request_id: str,
    source_label: str,
    request: ProcessRequest,
    entitlement: EntitlementContext,
    target_platform: str,
) -> list:
    diversity_counts: dict[str, int] = {}
    for clip in clips:
        bucket = clip.packaging_angle or clip.detected_category or "general"
        diversity_counts[bucket] = diversity_counts.get(bucket, 0) + 1

    campaign_requested = bool(request.campaign_brief)
    campaign_enabled = bool(entitlement.plan.feature_flags.campaign_mode)
    allowed_platforms = [value for value in (request.allowed_platforms or []) if value]
    updated = []
    for index, clip in enumerate(clips, start=1):
        diversity_bucket = clip.packaging_angle or clip.detected_category or "general"
        rendered_status = clip.rendered_status or build_clip_rendered_status(
            preview_url=clip.preview_url,
            edited_clip_url=clip.edited_clip_url,
            clip_url=clip.clip_url,
            raw_clip_url=clip.raw_clip_url,
            render_status=clip.render_status,
        )
        campaign_fit_score = None
        campaign_fit_reason = None
        platform_notes: list[str] = []
        compliance_notes: list[str] = []
        required_hashtags = [tag for tag in (request.required_hashtags or []) if isinstance(tag, str) and tag.strip()]
        subtitle_url = build_clip_subtitle_url(clip)
        thumbnail_preview_url = build_clip_thumbnail_preview_url(clip)
        duration_seconds = clip.duration or derive_clip_duration_seconds(clip.start_time, clip.end_time)
        export_profile = resolve_clip_export_profile(
            clip=clip,
            target_platform=target_platform,
            rendered_status=rendered_status,
        )
        render_notes = build_clip_render_notes(
            clip=clip,
            rendered_status=rendered_status,
            subtitle_url=subtitle_url,
        )
        render_quality = rendered_status
        prepared_clip = clip.model_copy(
            update={
                "duration_seconds": duration_seconds,
                "duration": duration_seconds,
                "subtitle_url": subtitle_url,
                "captions_burned_in": build_clip_captions_burned_in(clip),
                "thumbnail_preview_url": thumbnail_preview_url,
                "thumbnail_url": clip.thumbnail_url or thumbnail_preview_url,
                "export_profile": export_profile,
                "render_quality": render_quality,
                "render_notes": render_notes,
                "resolution": build_clip_resolution(clip=clip, rendered_status=rendered_status),
                "rendered_status": rendered_status,
            }
        )

        if campaign_requested:
            if allowed_platforms and target_platform not in allowed_platforms:
                platform_notes.append(f"Requested campaign platforms prefer {', '.join(allowed_platforms)} over {target_platform}.")
            else:
                platform_notes.append(f"Current packaging is aimed at {target_platform}.")
            if request.forbidden_terms:
                compliance_notes.append("Review forbidden terms manually before publishing campaign copy.")
            if clip.risk_flags:
                compliance_notes.append("Review risk flags before using this clip in a paid or campaign context.")
            if campaign_enabled:
                fit = min(max((clip.score or 0) + (8 if rendered_status == "rendered" else 0), 0), 100)
                campaign_fit_score = fit
                campaign_fit_reason = (
                    "Rendered asset plus strong packaging makes this the safest manual-review candidate."
                    if rendered_status == "rendered"
                    else "Packaging is useful, but this still needs render review before campaign use."
                )

        updated.append(
            prepared_clip.model_copy(
                update={
                    "source_index": 1,
                    "source_label": source_label,
                    "batch_group": request_id,
                    "selection_reason": prepared_clip.selection_reason or prepared_clip.why_this_matters or prepared_clip.reason,
                    "duplicate_risk": "medium" if diversity_counts.get(diversity_bucket, 0) > 1 else "low",
                    "diversity_bucket": diversity_bucket,
                    "rendered_status": rendered_status,
                    "export_ready": bool(prepared_clip.preview_url or prepared_clip.edited_clip_url or prepared_clip.clip_url or prepared_clip.raw_clip_url or prepared_clip.download_url),
                    "asset_manifest": build_clip_asset_manifest(prepared_clip),
                    "package_text": build_clip_package_text(prepared_clip),
                    "campaign_fit_score": campaign_fit_score,
                    "campaign_fit_reason": campaign_fit_reason,
                    "platform_notes": platform_notes,
                    "required_hashtag_suggestions": required_hashtags if campaign_enabled else [],
                    "compliance_notes": compliance_notes,
                }
            )
        )
    return updated


def build_recommended_next_step(
    *,
    preview_ready_count: int,
    rendered_clip_count: int,
    export_ready_count: int,
    entitlement: EntitlementContext,
) -> str:
    if export_ready_count:
        return "Open the lead preview, review the ranked cuts, then export the winners."
    if preview_ready_count and not entitlement.plan.feature_flags.premium_exports:
        return "Open the lead preview now. Upgrade when you want clean clip exports."
    if preview_ready_count:
        return "Open the lead preview now. Export will appear once rendering finishes."
    if rendered_clip_count:
        return "Review the rendered clips first. The rest of the pack is still useful as strategy, but it needs another run for playable proof."
    return "The intelligence pack is ready, but no playable preview was produced. Try a longer or cleaner source."


def build_upgrade_prompt(
    *,
    entitlement: EntitlementContext,
    current_user: UserRecord | None,
) -> str | None:
    if entitlement.plan.code == "free":
        if current_user is None:
            return (
                "Keep the first runs free. Create an account when you want synced uploads and saved workflow history, "
                "then move to Pro for more clips, alternate hooks, and clean exports."
            )
        return (
            "Upgrade to Pro for more clips per run, alternate hooks, richer caption packaging, and export-ready assets."
        )
    if entitlement.plan.code == "pro":
        return "Upgrade to Scale when you need campaign mode, posting queue access, and higher daily volume."
    return None


def recovery_request_for_clip(clip_record: dict[str, object]) -> ProcessRequest:
    source_video_url = str(clip_record.get("source_video_url") or "").strip()
    if source_video_url.lower() in {"none", "null"}:
        source_video_url = ""
    if not source_video_url:
        raise HTTPException(
            status_code=409,
            detail="Recovery is unavailable because this clip was saved without a reusable source reference.",
        )
    return ProcessRequest(
        video_url=source_video_url,
        source_type=clip_record.get("source_type"),
        upload_content_type=clip_record.get("source_upload_content_type"),
        content_angle=clip_record.get("packaging_angle"),
    )


def select_recovery_candidate(*, original_clip: dict[str, object], recovered_clips: list) -> object | None:
    media_ready = [clip for clip in recovered_clips if clip_has_rendered_media(clip)]
    if not media_ready:
        return None

    original_clip_key = str(original_clip.get("clip_id") or original_clip.get("id") or "").strip()
    for clip in media_ready:
        if clip.id == original_clip_key:
            return clip

    original_start = original_clip.get("start_time")
    original_end = original_clip.get("end_time")
    for clip in media_ready:
        if clip.start_time == original_start and clip.end_time == original_end:
            return clip

    original_post_rank = original_clip.get("post_rank") or original_clip.get("best_post_order")
    for clip in media_ready:
        if (clip.post_rank or clip.best_post_order or clip.rank) == original_post_rank:
            return clip

    original_rank = original_clip.get("rank")
    for clip in media_ready:
        if clip.rank == original_rank:
            return clip

    return media_ready[0]


async def run_clip_recovery(
    *,
    settings: Settings,
    platform_store: PlatformStore,
    clip_record: dict[str, object],
    current_user: UserRecord,
    entitlement: EntitlementContext,
    public_base_url: str,
    route_path: str,
    recovery_job_id: str,
) -> dict[str, object]:
    request = recovery_request_for_clip(clip_record)
    response = await build_clip_response(
        settings=settings,
        request_id=f"recover_{uuid4().hex[:10]}",
        request=request,
        public_base_url=public_base_url,
        route_path=route_path,
        entitlement=entitlement,
        current_user=current_user,
        platform_store=None,
        source_path=None,
    )
    recovered_clip = select_recovery_candidate(original_clip=clip_record, recovered_clips=response.clips)
    if recovered_clip is None:
        raise HTTPException(
            status_code=409,
            detail="Recovery completed, but no playable or previewable media was produced for this clip.",
        )

    local_asset_paths = resolve_local_asset_paths(
        settings=settings,
        request_id=response.request_id,
        clips=response.clips,
    )
    updated_clip = platform_store.update_clip_recovery(
        clip_id=str(clip_record["record_id"]),
        user_id=current_user.id,
        clip_url=recovered_clip.clip_url,
        raw_clip_url=recovered_clip.raw_clip_url,
        edited_clip_url=recovered_clip.edited_clip_url or recovered_clip.preview_url,
        preview_image_url=recovered_clip.preview_image_url or recovered_clip.thumbnail_url,
        download_url=recovered_clip.download_url,
        local_asset_path=local_asset_paths.get(recovered_clip.id),
    )
    if not updated_clip:
        raise HTTPException(status_code=404, detail="Recovered media was produced, but the stored clip could not be updated.")
    return updated_clip


async def run_clip_recovery_job(
    *,
    settings: Settings,
    platform_store: PlatformStore,
    clip_record: dict[str, object],
    current_user: UserRecord,
    entitlement: EntitlementContext,
    public_base_url: str,
    route_path: str,
    job_id: str,
) -> None:
    platform_store.update_job(
        job_id=job_id,
        status="processing",
        message="Retrying media generation for the strategy-only clip.",
    )
    try:
        recovered_clip = await run_clip_recovery(
            settings=settings,
            platform_store=platform_store,
            clip_record=clip_record,
            current_user=current_user,
            entitlement=entitlement,
            public_base_url=public_base_url,
            route_path=route_path,
            recovery_job_id=job_id,
        )
    except HTTPException as error:
        platform_store.update_job(
            job_id=job_id,
            status="failed",
            message=error.detail if isinstance(error.detail, str) else "Recovery failed.",
            response_json=json.dumps({"error": error.detail}),
        )
        return
    except Exception as error:
        platform_store.update_job(
            job_id=job_id,
            status="failed",
            message="Recovery failed.",
            response_json=json.dumps({"error": str(error)}),
        )
        return

    platform_store.update_job(
        job_id=job_id,
        status="recovered",
        message="Recovered media is ready.",
        response_json=json.dumps({"recovered_clip": recovered_clip}),
    )


CONTENT_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Anime / fandom edit": ("anime", "manga", "amv", "fandom", "arc", "character", "episode", "edit"),
    "Reaction / commentary": ("reaction", "react", "commentary", "podcast", "interview", "stream", "review", "breakdown"),
    "Shock / reveal": ("shocking", "shock", "reveal", "twist", "secret", "plot twist", "crazy", "wait for it"),
    "Meme / quote-core": ("meme", "quote", "funny", "joke", "one-liner", "insane line", "caption this"),
    "Story payoff": ("story", "happened", "moment", "ending", "then", "finally", "payoff", "turned out"),
    "Animal / absurdity": ("dog", "cat", "animal", "pet", "absurd", "weird", "chaos", "wild animal"),
    "Polished lifestyle": ("beauty", "fashion", "outfit", "routine", "travel", "aesthetic", "morning routine", "fit check"),
}


def recommend_platform_strategy(
    *,
    source_context,
    detected_source_platform: str,
    selected_trend: str | None,
    content_angle: str | None,
) -> tuple[str, str, str, str]:
    recommended_content_type = infer_content_type(
        source_context=source_context,
        detected_source_platform=detected_source_platform,
        selected_trend=selected_trend,
        content_angle=content_angle,
    )

    if recommended_content_type == "Polished lifestyle" or detected_source_platform.lower() == "instagram":
        recommended_platform = "Instagram Reels"
    elif recommended_content_type in {"Reaction / commentary", "Story payoff"}:
        recommended_platform = "YouTube Shorts"
    elif recommended_content_type == "Anime / fandom edit":
        recommended_platform = "TikTok"
    elif recommended_content_type == "Animal / absurdity":
        recommended_platform = "TikTok"
    elif recommended_content_type == "Meme / quote-core":
        recommended_platform = "TikTok"
    elif recommended_content_type == "Shock / reveal":
        recommended_platform = "TikTok"
    elif detected_source_platform.lower() in {"youtube", "twitch"}:
        recommended_platform = "YouTube Shorts"
    else:
        recommended_platform = "TikTok"

    return (
        recommended_platform,
        platform_recommendation_reason(
            recommended_platform=recommended_platform,
            recommended_content_type=recommended_content_type,
            detected_source_platform=detected_source_platform,
        ),
        recommended_content_type,
        recommended_output_style(
            recommended_platform=recommended_platform,
            recommended_content_type=recommended_content_type,
        ),
    )


def infer_content_type(
    *,
    source_context,
    detected_source_platform: str,
    selected_trend: str | None,
    content_angle: str | None,
) -> str:
    combined = " ".join(
        part
        for part in [
            source_context.title if source_context else "",
            source_context.description if source_context else "",
            source_context.transcript if source_context else "",
            source_context.visual_summary if source_context else "",
            detected_source_platform,
            selected_trend or "",
            content_angle or "",
        ]
        if part
    ).lower()
    normalized = re.sub(r"\s+", " ", combined)

    scored = [
        (label, sum(1 for keyword in keywords if keyword in normalized))
        for label, keywords in CONTENT_TYPE_KEYWORDS.items()
    ]
    best_label, best_score = max(scored, key=lambda item: item[1], default=("Educational / value", 0))
    if best_score > 0:
        return best_label
    if detected_source_platform.lower() in {"youtube", "twitch"}:
        return "Reaction / commentary"
    return "Educational / value"


def platform_recommendation_reason(
    *,
    recommended_platform: str,
    recommended_content_type: str,
    detected_source_platform: str,
) -> str:
    if recommended_platform == "TikTok":
        return (
            f"This source reads like {recommended_content_type.lower()}, so the fastest cold-open, caption-led "
            "cut is the strongest first destination."
        )
    if recommended_platform == "Instagram Reels":
        return (
            f"This source reads like {recommended_content_type.lower()}, so a more polished visual package fits best "
            "before you branch into other feeds."
        )
    if detected_source_platform.lower() in {"youtube", "twitch"}:
        return (
            f"This source reads like {recommended_content_type.lower()} from a longer-form platform, so Shorts is the "
            "cleanest first destination for payoff-first clipping."
        )
    return (
        f"This source reads like {recommended_content_type.lower()}, so Shorts-style structure is the clearest first "
        "destination for replayable retention."
    )


def recommended_output_style(*, recommended_platform: str, recommended_content_type: str) -> str:
    if recommended_platform == "TikTok":
        if recommended_content_type == "Anime / fandom edit":
            return "High-contrast cold open with short caption bursts and fast loop payoff."
        if recommended_content_type == "Animal / absurdity":
            return "Instant action up front with minimal setup and comment bait at the end."
        return "Fast interruption, bold captions, and payoff in the first beat."
    if recommended_platform == "Instagram Reels":
        return "Cleaner framing, polished captions, and a more aesthetic payoff beat."
    return "Context-light opener, readable captions, and a clean payoff before the follow-up CTA."


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
        emit_event(
            settings=settings,
            event="quota_released",
            request_id=job_id,
            plan_code=entitlement.plan.code,
            subject_source=entitlement.subject_source,
            status="released",
            metadata={"reason": "async_job_failure"},
        )
        emit_event(
            settings=settings,
            event="generation_failed",
            request_id=job_id,
            plan_code=entitlement.plan.code,
            subject_source=entitlement.subject_source,
            status="failed",
            metadata={
                "target_platform": request.target_platform or "auto",
                "source_type": request.source_type or ("video_upload" if source_path else "url"),
                "error_code": type(error).__name__,
            },
        )
        await job_store.fail(job_id, str(error), error_type=type(error).__name__)
        if platform_store is not None:
            platform_store.update_job(
                job_id=job_id,
                status="failed",
                message=str(error),
            )
    finally:
        await asyncio.to_thread(maybe_prune_generated_assets, settings)


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


def maybe_prune_generated_assets(settings: Settings, *, force: bool = False) -> dict[str, int]:
    global _last_generated_asset_prune_at

    now = time.time()
    if not force and (now - _last_generated_asset_prune_at) < max(settings.generated_asset_prune_interval_seconds, 60):
        return {"scanned": 0, "removed": 0, "store_removed": 0}

    _last_generated_asset_prune_at = now
    emit_event(
        settings=settings,
        event="asset_cleanup_started",
        status="started",
        metadata={
            "retention_hours": settings.generated_asset_retention_hours,
            "max_files": settings.generated_assets_max_files,
        },
    )
    try:
        stats = cleanup_generated_assets_nonfatal_for_settings(settings)
        emit_event(
            settings=settings,
            event="asset_cleanup_completed",
            status="ok",
            metadata={
                "scanned_count": stats.get("scanned_count", 0),
                "deleted_count": stats.get("deleted_count", 0),
                "store_removed": stats.get("store_removed", 0),
            },
        )
        return {
            "scanned": int(stats.get("scanned_count", stats.get("scanned", 0))),
            "removed": int(stats.get("deleted_count", stats.get("removed", 0))),
            "store_removed": int(stats.get("store_removed", 0)),
        }
    except Exception as error:
        emit_event(
            settings=settings,
            event="asset_cleanup_failed",
            status="failed",
            metadata={"error_code": type(error).__name__},
        )
        logger.warning("generated_asset_cleanup_failed error=%s", error)
        return {"scanned": 0, "removed": 0, "store_removed": 0}
