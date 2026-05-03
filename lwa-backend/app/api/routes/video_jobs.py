from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from app.core.auth import get_current_user_optional
from app.core.config import Settings, get_settings
from app.services.video_os import (
    VideoOSOrchestrator,
    VideoJobRequest,
    VideoJobType,
    VideoJobStatus,
)


router = APIRouter()


class VideoJobCreateRequest(BaseModel):
    job_type: str
    prompt: Optional[str] = None
    input_urls: List[str] = []
    source_asset_ids: List[str] = []
    aspect_ratio: str = "9:16"
    duration_seconds: int = 15
    resolution: str = "720p"
    style_preset: Optional[str] = None


class VideoJobResponse(BaseModel):
    job_id: str
    user_id: str
    job_type: str
    provider: str
    status: str
    prompt: Optional[str]
    input_urls: List[str]
    source_asset_ids: List[str]
    aspect_ratio: str
    duration_seconds: int
    resolution: str
    style_preset: Optional[str]
    cost_estimate_usd: float
    progress: int
    preview_url: Optional[str]
    output_url: Optional[str]
    thumbnail_url: Optional[str]
    error_message: Optional[str]
    timeline_plan: Optional[dict]
    created_at: str
    updated_at: str


class VideoJobListResponse(BaseModel):
    jobs: List[VideoJobResponse]


class CancelResponse(BaseModel):
    message: str
    job_id: str
    status: str


def get_video_orchestrator(settings: Settings) -> VideoOSOrchestrator:
    """Get Video OS orchestrator with current settings."""
    return VideoOSOrchestrator(
        enabled=settings.video_os_enabled,
        provider=settings.video_provider,
    )


@router.post("/video-jobs", response_model=VideoJobResponse)
async def create_video_job(
    request: VideoJobCreateRequest,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Create a new video job."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Validate job type
    try:
        job_type = VideoJobType(request.job_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid job type: {request.job_type}. Valid types: {[jt.value for jt in VideoJobType]}"
        )
    
    # Create video job request
    video_request = VideoJobRequest(
        job_type=job_type,
        prompt=request.prompt,
        input_urls=request.input_urls,
        source_asset_ids=request.source_asset_ids,
        aspect_ratio=request.aspect_ratio,
        duration_seconds=request.duration_seconds,
        resolution=request.resolution,
        style_preset=request.style_preset,
    )
    
    # Create job
    orchestrator = get_video_orchestrator(settings)
    job = orchestrator.create_video_job(video_request, user_id)
    
    return VideoJobResponse(
        job_id=job.job_id,
        user_id=job.user_id,
        job_type=job.job_type.value,
        provider=job.provider,
        status=job.status.value,
        prompt=job.prompt,
        input_urls=job.input_urls,
        source_asset_ids=job.source_asset_ids,
        aspect_ratio=job.aspect_ratio,
        duration_seconds=job.duration_seconds,
        resolution=job.resolution,
        style_preset=job.style_preset,
        cost_estimate_usd=job.cost_estimate_usd,
        progress=job.progress,
        preview_url=job.preview_url,
        output_url=job.output_url,
        thumbnail_url=job.thumbnail_url,
        error_message=job.error_message,
        timeline_plan={
            "id": job.timeline_plan.id,
            "title": job.timeline_plan.title,
            "aspect_ratio": job.timeline_plan.aspect_ratio,
            "duration_seconds": job.timeline_plan.duration_seconds,
            "track_count": len(job.timeline_plan.tracks),
        } if job.timeline_plan else None,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/video-jobs/{job_id}", response_model=VideoJobResponse)
async def get_video_job(
    job_id: str,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get status of a specific video job."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    orchestrator = get_video_orchestrator(settings)
    job = orchestrator.get_video_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify user owns this job (in production, add proper user filtering)
    # For v0 with in-memory storage, we'll skip strict user checking
    
    return VideoJobResponse(
        job_id=job.job_id,
        user_id=job.user_id,
        job_type=job.job_type.value,
        provider=job.provider,
        status=job.status.value,
        prompt=job.prompt,
        input_urls=job.input_urls,
        source_asset_ids=job.source_asset_ids,
        aspect_ratio=job.aspect_ratio,
        duration_seconds=job.duration_seconds,
        resolution=job.resolution,
        style_preset=job.style_preset,
        cost_estimate_usd=job.cost_estimate_usd,
        progress=job.progress,
        preview_url=job.preview_url,
        output_url=job.output_url,
        thumbnail_url=job.thumbnail_url,
        error_message=job.error_message,
        timeline_plan={
            "id": job.timeline_plan.id,
            "title": job.timeline_plan.title,
            "aspect_ratio": job.timeline_plan.aspect_ratio,
            "duration_seconds": job.timeline_plan.duration_seconds,
            "track_count": len(job.timeline_plan.tracks),
        } if job.timeline_plan else None,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/video-jobs", response_model=VideoJobListResponse)
async def list_video_jobs(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """List recent video jobs."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    orchestrator = get_video_orchestrator(settings)
    jobs = orchestrator.list_video_jobs()
    
    # In production, filter by user_id. For v0, return all jobs from memory
    job_responses = []
    for job in jobs:
        job_responses.append(VideoJobResponse(
            job_id=job.job_id,
            user_id=job.user_id,
            job_type=job.job_type.value,
            provider=job.provider,
            status=job.status.value,
            prompt=job.prompt,
            input_urls=job.input_urls,
            source_asset_ids=job.source_asset_ids,
            aspect_ratio=job.aspect_ratio,
            duration_seconds=job.duration_seconds,
            resolution=job.resolution,
            style_preset=job.style_preset,
            cost_estimate_usd=job.cost_estimate_usd,
            progress=job.progress,
            preview_url=job.preview_url,
            output_url=job.output_url,
            thumbnail_url=job.thumbnail_url,
            error_message=job.error_message,
            timeline_plan={
                "id": job.timeline_plan.id,
                "title": job.timeline_plan.title,
                "aspect_ratio": job.timeline_plan.aspect_ratio,
                "duration_seconds": job.timeline_plan.duration_seconds,
                "track_count": len(job.timeline_plan.tracks),
            } if job.timeline_plan else None,
            created_at=job.created_at,
            updated_at=job.updated_at,
        ))
    
    return VideoJobListResponse(jobs=job_responses)


@router.post("/video-jobs/{job_id}/cancel", response_model=CancelResponse)
async def cancel_video_job(
    job_id: str,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Cancel a video job."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    orchestrator = get_video_orchestrator(settings)
    job = orchestrator.get_video_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify user owns this job (in production, add proper user checking)
    
    canceled_job = orchestrator.cancel_video_job(job_id)
    
    if not canceled_job:
        raise HTTPException(status_code=400, detail="Cannot cancel job")
    
    return CancelResponse(
        message="Job canceled successfully",
        job_id=job_id,
        status=canceled_job.status.value,
    )


@router.get("/video-jobs/capabilities")
async def get_video_job_capabilities(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get video job capabilities and configuration."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "enabled": settings.video_os_enabled,
        "provider": settings.video_provider,
        "job_types": [jt.value for jt in VideoJobType],
        "statuses": [js.value for js in VideoJobStatus],
        "allowed_aspect_ratios": ["9:16", "16:9", "1:1", "4:5"],
        "allowed_resolutions": ["480p", "720p", "1080p"],
        "max_duration_seconds": settings.video_max_duration_seconds,
        "max_inputs": settings.video_max_inputs,
        "max_resolution": settings.video_max_resolution,
        "allow_live_providers": settings.video_allow_live_providers,
        "storage_provider": settings.video_storage_provider,
        "mock_mode": not settings.video_os_enabled or settings.video_provider == "mock",
    }


@router.post("/video-jobs/estimate-cost")
async def estimate_video_job_cost(
    request: VideoJobCreateRequest,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Estimate cost for a video job without creating it."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Validate job type
    try:
        job_type = VideoJobType(request.job_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid job type: {request.job_type}"
        )
    
    # Create request for cost estimation
    video_request = VideoJobRequest(
        job_type=job_type,
        prompt=request.prompt,
        input_urls=request.input_urls,
        source_asset_ids=request.source_asset_ids,
        aspect_ratio=request.aspect_ratio,
        duration_seconds=request.duration_seconds,
        resolution=request.resolution,
        style_preset=request.style_preset,
    )
    
    # Import cost estimation function
    from app.services.video_os import estimate_video_job_cost
    
    cost = estimate_video_job_cost(video_request)
    
    return {
        "estimated_cost_usd": cost,
        "currency": "USD",
        "job_type": request.job_type,
        "duration_seconds": request.duration_seconds,
        "resolution": request.resolution,
        "input_count": len(request.input_urls),
    }
