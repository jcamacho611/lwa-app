from __future__ import annotations

import asyncio
import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ...core.config import get_settings
from ...dependencies.auth import get_optional_user, get_platform_store
from ...services.clip_analysis_service import (
    queue_analysis_clip_render,
    run_video_analysis,
    video_analysis_summary,
    video_candidate_clips,
)
from ...services.clip_analysis_store import create_video_record
from ...services.output_builder import OutputBuilder

router = APIRouter(prefix="/v1/video-analysis", tags=["video-analysis"])
platform_store = get_platform_store()
settings = get_settings()
logger = logging.getLogger("uvicorn.error")


class VideoAnalysisRequest(BaseModel):
    video_url: str | None = None
    upload_file_id: str | None = None
    target_platform: str | None = None
    mode: str | None = None


class VideoAnalysisResponse(BaseModel):
    request_id: str
    status: str
    message: str
    clip_count: int | None = None
    render_jobs: dict[str, int] | None = None
    bundle_info: dict[str, object] | None = None


def allow_first_use_without_auth(request: Request) -> bool:
    return True


def analysis_actor_id(request: Request) -> str:
    user = get_optional_user(request)
    if user:
        return user.id
    client_id = (request.headers.get(settings.client_id_header_name) or "").strip()
    safe_id = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in client_id)
    return f"guest_{safe_id[:64] or 'first_use'}"


def export_lookup_subjects(request: Request) -> list[str]:
    user = get_optional_user(request)
    if user:
        return [user.id]

    client_id = (request.headers.get(settings.client_id_header_name) or "").strip()
    if not client_id:
        return []

    safe_id = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in client_id)
    subjects = [f"client:{client_id}"]
    if safe_id:
        subjects.append(f"guest_{safe_id[:64]}")
    return subjects


def resolve_analysis_source(payload: VideoAnalysisRequest, request: Request) -> str:
    if payload.video_url:
        return payload.video_url
    if not payload.upload_file_id:
        raise HTTPException(status_code=400, detail="Either video_url or upload_file_id must be provided")

    user = get_optional_user(request)
    upload = platform_store.get_upload(payload.upload_file_id, user_id=user.id if user else None)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    public_url = str(upload.get("public_url") or "").strip()
    if not public_url:
        raise HTTPException(status_code=409, detail="Upload is missing a public URL")
    return public_url


def run_analysis_and_queue_renders(
    *,
    video_id: str,
    source_url: str,
    target_platform: str | None,
    mode: str | None,
    public_base_url: str,
) -> None:
    run_video_analysis(
        settings=settings,
        video_id=video_id,
        video_url=source_url,
        target_platform=target_platform,
        mode=mode,
    )
    for clip in video_candidate_clips(settings=settings, video_id=video_id):
        if str(clip.get("render_status") or "pending") in {"ready", "rendering"}:
            continue
        queue_analysis_clip_render(
            settings=settings,
            clip_id=str(clip["id"]),
            public_base_url=public_base_url,
        )


@router.post("/analyze")
async def start_video_analysis(payload: VideoAnalysisRequest, request: Request) -> VideoAnalysisResponse:
    """Start a first-use video analysis without requiring signup."""
    if not allow_first_use_without_auth(request):
        raise HTTPException(status_code=401, detail="Signup required")

    source_url = resolve_analysis_source(payload, request)
    actor_id = analysis_actor_id(request)
    video_id = f"analysis_{actor_id}_{uuid4().hex[:12]}"
    public_base_url = (settings.api_base_url or str(request.base_url)).rstrip("/")

    create_video_record(
        settings=settings,
        video_id=video_id,
        source_url=source_url,
        target_platform=payload.target_platform,
        mode=payload.mode,
    )
    asyncio.create_task(
        asyncio.to_thread(
            run_analysis_and_queue_renders,
            video_id=video_id,
            source_url=source_url,
            target_platform=payload.target_platform,
            mode=payload.mode,
            public_base_url=public_base_url,
        )
    )

    logger.info("video_analysis_queued request_id=%s actor_id=%s", video_id, actor_id)
    return VideoAnalysisResponse(
        request_id=video_id,
        status="processing",
        message="Video analysis started.",
        clip_count=None,
        render_jobs={"queued": 0},
    )


@router.get("/status/{request_id}")
async def get_analysis_status(request_id: str, request: Request) -> VideoAnalysisResponse:
    """Get status of a first-use video analysis request."""
    summary = video_analysis_summary(settings=settings, video_id=request_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Analysis request not found")

    return VideoAnalysisResponse(
        request_id=request_id,
        status=str(summary.get("status") or "processing"),
        message=str(summary.get("error") or "Analysis status loaded."),
        clip_count=int(summary.get("candidate_clip_count") or 0),
        render_jobs={
            "ready": int(summary.get("ready_clip_count") or 0),
            "failed": int(summary.get("failed_clip_count") or 0),
        },
    )


@router.post("/retry/{request_id}")
async def retry_failed_renders(request_id: str, request: Request) -> VideoAnalysisResponse:
    """Retry failed preview renders for an analysis request."""
    public_base_url = (settings.api_base_url or str(request.base_url)).rstrip("/")
    clips = video_candidate_clips(settings=settings, video_id=request_id)
    if not clips:
        raise HTTPException(status_code=404, detail="Analysis request not found")

    retry_count = 0
    for clip in clips:
        if str(clip.get("render_status") or "") == "failed":
            queue_analysis_clip_render(settings=settings, clip_id=str(clip["id"]), public_base_url=public_base_url)
            retry_count += 1

    return VideoAnalysisResponse(
        request_id=request_id,
        status="processing" if retry_count else "ready",
        message=f"Queued {retry_count} failed preview renders for retry.",
        clip_count=len(clips),
        render_jobs={"queued": retry_count},
    )


@router.get("/queue-status")
async def get_queue_status(request: Request) -> dict[str, object]:
    """Compatibility queue status endpoint for first-use analysis flow."""
    return {
        "queue_length": 0,
        "pending_jobs": 0,
        "processing_jobs": 0,
        "active_workers": 0,
        "total_capacity": 0,
    }


@router.post("/export/{request_id}")
async def export_bundle(request_id: str, request: Request) -> dict[str, object]:
    """Export a bundle for a completed first-use request."""
    clips = video_candidate_clips(settings=settings, video_id=request_id)

    if not clips:
        for subject in export_lookup_subjects(request):
            clip_pack = platform_store.get_clip_pack(user_id=subject, request_id=request_id)
            pack_clips = clip_pack.get("clips") or []
            if pack_clips:
                clips = pack_clips
                break

    if not clips:
        raise HTTPException(status_code=404, detail="Analysis request not found")

    output_builder = OutputBuilder(settings)
    bundle = await output_builder.create_clip_bundle(
        request_id=request_id,
        clips=clips,
        bundle_format="zip",
        include_metadata=True,
    )

    logger.info("video_analysis_export_created request_id=%s", request_id)
    return {
        "bundle_id": bundle["bundle_id"],
        "file_name": bundle["file_name"],
        "download_url": bundle["download_url"],
        "manifest_url": bundle.get("manifest_url"),
        "clip_count": bundle["clip_count"],
        "created_at": bundle["created_at"],
        "bundle_format": bundle.get("bundle_format"),
        "artifact_types": bundle.get("artifact_types"),
        "artifact_counts": bundle.get("artifact_counts"),
        "size_bytes": bundle["size_bytes"],
    }
