from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.auth import get_current_user_optional
from app.core.config import Settings, get_settings
from app.services.render_engine import (
    RenderEngine, 
    RenderJob, 
    RenderStatus, 
    OutputFormat, 
    AspectRatio,
    TimelineClip,
    TimelineAsset,
    AssetType
)

router = APIRouter()


class AssetRequest(BaseModel):
    asset_type: str
    source_url: str
    start_time: float = 0.0
    duration: float = 5.0
    track: int = 0
    metadata: Dict[str, Any] = {}


class ClipRequest(BaseModel):
    clip_id: Optional[str] = None
    assets: List[AssetRequest]
    start_time: float = 0.0
    duration: float = 5.0
    transition_in: Optional[str] = None
    transition_out: Optional[str] = None
    effects: List[str] = []


class RenderJobRequest(BaseModel):
    clips: List[ClipRequest]
    output_format: str = "mp4"
    aspect_ratio: str = "9:16"
    resolution: Optional[str] = None
    frame_rate: int = 30
    provider: str = "shotstack"


class RenderJobResponse(BaseModel):
    job_id: str
    user_id: str
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    output_url: Optional[str]
    error_message: Optional[str]
    progress: int
    provider: str
    cost_estimate: Optional[float]
    timeline: Dict[str, Any]


class RenderStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    output_url: Optional[str]
    error_message: Optional[str]
    estimated_completion: Optional[str]


@router.post("/render-engine/create-job", response_model=RenderJobResponse)
async def create_render_job(
    request: RenderJobRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Create a new render job from timeline clips."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Validate request
    if not request.clips:
        raise HTTPException(status_code=400, detail="At least one clip is required")
    
    # Convert request to timeline clips
    timeline_clips = []
    for i, clip_req in enumerate(request.clips):
        # Convert assets
        assets = []
        for asset_req in clip_req.assets:
            try:
                asset_type = AssetType(asset_req.asset_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid asset type: {asset_req.asset_type}"
                )
            
            assets.append(TimelineAsset(
                asset_id=f"asset_{i}_{len(assets)}",
                asset_type=asset_type,
                source_url=asset_req.source_url,
                start_time=asset_req.start_time,
                duration=asset_req.duration,
                track=asset_req.track,
                metadata=asset_req.metadata,
            ))
        
        # Create timeline clip
        timeline_clip = TimelineClip(
            clip_id=clip_req.clip_id or f"clip_{i}",
            assets=assets,
            start_time=clip_req.start_time,
            duration=clip_req.duration,
            transition_in=clip_req.transition_in,
            transition_out=clip_req.transition_out,
            effects=clip_req.effects,
        )
        
        timeline_clips.append(timeline_clip)
    
    # Validate format and aspect ratio
    try:
        output_format = OutputFormat(request.output_format.lower())
        aspect_ratio = AspectRatio(request.aspect_ratio.lower())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid format or aspect ratio: {str(e)}")
    
    # Determine resolution if not provided
    resolution = request.resolution
    if not resolution:
        resolution_map = {
            "9:16": "1080x1920",
            "16:9": "1920x1080", 
            "1:1": "1080x1080",
            "4:5": "1080x1350",
        }
        resolution = resolution_map.get(request.aspect_ratio, "1080x1920")
    
    # Create render engine and job
    render_engine = RenderEngine(settings)
    job = render_engine.create_render_job(
        user_id=user_id,
        clips=timeline_clips,
        output_format=output_format,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        frame_rate=request.frame_rate,
        provider=request.provider,
    )
    
    # Estimate cost
    cost_estimate = render_engine.estimate_render_cost(job.timeline)
    
    # Update job with cost estimate
    job = RenderJob(
        **{**job.__dict__, "cost_estimate": cost_estimate}
    )
    render_engine.active_jobs[job.job_id] = job
    
    # Submit job in background
    background_tasks.add_task(render_engine.submit_render_job, job.job_id)
    
    return RenderJobResponse(
        job_id=job.job_id,
        user_id=job.user_id,
        status=job.status.value,
        created_at=job.created_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        output_url=job.output_url,
        error_message=job.error_message,
        progress=job.progress,
        provider=job.provider,
        cost_estimate=job.cost_estimate,
        timeline={
            "timeline_id": job.timeline.timeline_id,
            "total_duration": job.timeline.total_duration,
            "output_format": job.timeline.output_format.value,
            "aspect_ratio": job.timeline.aspect_ratio.value,
            "resolution": job.timeline.resolution,
            "frame_rate": job.timeline.frame_rate,
            "clip_count": len(job.timeline.clips),
        }
    )


@router.get("/render-engine/job/{job_id}", response_model=RenderStatusResponse)
async def get_render_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get status of a specific render job."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    render_engine = RenderEngine(settings)
    job = render_engine.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify user owns this job
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Estimate completion time
    estimated_completion = None
    if job.status in [RenderStatus.pending, RenderStatus.processing, RenderStatus.rendering]:
        # Simple estimate: 30 seconds per clip + 10 seconds base
        estimated_seconds = 30 + (len(job.timeline.clips) * 30)
        estimated_completion = datetime.fromtimestamp(
            job.created_at.timestamp() + estimated_seconds
        ).isoformat()
    
    return RenderStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        progress=job.progress,
        output_url=job.output_url,
        error_message=job.error_message,
        estimated_completion=estimated_completion,
    )


@router.get("/render-engine/jobs")
async def get_user_render_jobs(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get all render jobs for the current user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    render_engine = RenderEngine(settings)
    jobs = render_engine.get_user_jobs(user_id)
    
    return JSONResponse(content={
        "jobs": [
            {
                "job_id": job.job_id,
                "status": job.status.value,
                "progress": job.progress,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "output_url": job.output_url,
                "cost_estimate": job.cost_estimate,
                "timeline": {
                    "total_duration": job.timeline.total_duration,
                    "clip_count": len(job.timeline.clips),
                    "output_format": job.timeline.output_format.value,
                }
            }
            for job in jobs
        ]
    })


@router.post("/render-engine/cancel/{job_id}")
async def cancel_render_job(
    job_id: str,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Cancel a render job."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    render_engine = RenderEngine(settings)
    job = render_engine.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify user owns this job
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = render_engine.cancel_job(job_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel job (already completed/failed)")
    
    return JSONResponse(content={
        "message": "Job cancelled successfully",
        "job_id": job_id,
        "status": "cancelled"
    })


@router.post("/render-engine/create-from-clips")
async def create_render_from_clips(
    clip_data: List[Dict[str, Any]],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Create render job from simplified clip data (for existing LWA clips)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    if not clip_data:
        raise HTTPException(status_code=400, detail="Clip data is required")
    
    # Create render engine and build timeline
    render_engine = RenderEngine(settings)
    timeline = render_engine.create_timeline_from_clips(clip_data=clip_data)
    
    # Create render job
    job = render_engine.create_render_job(
        user_id=user_id,
        clips=timeline.clips,
        output_format=timeline.output_format,
        aspect_ratio=timeline.aspect_ratio,
        resolution=timeline.resolution,
        frame_rate=timeline.frame_rate,
    )
    
    # Estimate cost
    cost_estimate = render_engine.estimate_render_cost(timeline)
    job = RenderJob(
        **{**job.__dict__, "cost_estimate": cost_estimate}
    )
    render_engine.active_jobs[job.job_id] = job
    
    # Submit job in background
    background_tasks.add_task(render_engine.submit_render_job, job.job_id)
    
    return JSONResponse(content={
        "job_id": job.job_id,
        "status": job.status.value,
        "estimated_cost": cost_estimate,
        "timeline": {
            "total_duration": timeline.total_duration,
            "clip_count": len(timeline.clips),
            "output_format": timeline.output_format.value,
            "aspect_ratio": timeline.aspect_ratio.value,
            "resolution": timeline.resolution,
        }
    })


@router.get("/render-engine/capabilities")
async def get_render_capabilities(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get render engine capabilities and supported formats."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    render_engine = RenderEngine(settings)
    capabilities = render_engine.get_supported_formats()
    
    return JSONResponse(content={
        "capabilities": capabilities,
        "providers": ["shotstack", "ffmpeg", "custom"],
        "features": {
            "timeline_editing": True,
            "transitions": ["fade", "slide", "dissolve"],
            "effects": ["blur", "color_grade", "speed_ramp"],
            "text_overlays": True,
            "audio_mixing": True,
            "multi_track": True,
        },
        "limits": {
            "max_duration": capabilities["max_duration"],
            "max_clips": capabilities["max_clips"],
            "max_file_size": "500MB",
        }
    })


@router.get("/render-engine/estimate-cost")
async def estimate_render_cost(
    clip_data: List[Dict[str, Any]],
    output_format: str = "mp4",
    aspect_ratio: str = "9:16",
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Estimate render cost for a given timeline."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not clip_data:
        raise HTTPException(status_code=400, detail="Clip data is required")
    
    # Create timeline for cost estimation
    render_engine = RenderEngine(settings)
    timeline = render_engine.create_timeline_from_clips(
        clip_data=clip_data,
        output_format=OutputFormat(output_format.lower()),
        aspect_ratio=AspectRatio(aspect_ratio.lower()),
    )
    
    cost = render_engine.estimate_render_cost(timeline)
    
    return JSONResponse(content={
        "estimated_cost": cost,
        "currency": "USD",
        "factors": {
            "base_cost": 0.01,
            "duration_cost": timeline.total_duration * 0.002,
            "complexity_cost": len(timeline.clips) * 0.005,
            "total_duration": timeline.total_duration,
            "clip_count": len(timeline.clips),
        }
    })
