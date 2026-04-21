from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ...core.config import get_settings
from ...dependencies.auth import get_platform_store, require_user
from ...models.schemas import ProcessRequest
from ...services.analyze_worker import AnalyzeWorker
from ...services.entitlements import require_feature_access

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
    bundle_info: dict[str, str] | None = None


def require_analysis_unlocked(request: Request):
    user = require_user(request)
    require_feature_access(
        settings=settings,
        user=user,
        feature_name="clip_generation",
        detail="Upgrade to Pro to unlock video analysis features.",
    )
    return user


@router.post("/analyze")
async def start_video_analysis(payload: VideoAnalysisRequest, request: Request) -> VideoAnalysisResponse:
    """Start a new video analysis with render job queuing."""
    user = require_analysis_unlocked(request)
    
    # Validate request
    if not payload.video_url and not payload.upload_file_id:
        raise HTTPException(status_code=400, detail="Either video_url or upload_file_id must be provided")
    
    try:
        # Start background analysis worker
        worker = AnalyzeWorker(settings)
        request_id = f"analysis_{user.id}_{payload.video_url or payload.upload_file_id}_{hash(payload.video_url or payload.upload_file_id)}"
        
        # Start the analysis
        analysis_result = await worker.process_video_analysis(
            request_id=request_id,
            video_url=payload.video_url,
            upload_file_id=payload.upload_file_id,
            target_platform=payload.target_platform,
            mode=payload.mode,
        )
        
        logger.info(f"video_analysis_started request_id={request_id} user_id={user.id}")
        
        return VideoAnalysisResponse(
            request_id=request_id,
            status="processing",
            message="Video analysis started successfully",
            clip_count=analysis_result.clip_count if hasattr(analysis_result, 'clip_count') else len(analysis_result.clips),
            render_jobs=analysis_result.render_job_ids if hasattr(analysis_result, 'render_job_ids') else {},
            bundle_info=analysis_result.bundle_info if hasattr(analysis_result, 'bundle_info') else None,
        )
        
    except Exception as error:
        logger.error(f"video_analysis_failed request_id={request_id} error={str(error)}")
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(error)}")


@router.get("/status/{request_id}")
async def get_analysis_status(request_id: str, request: Request) -> VideoAnalysisResponse:
    """Get status of a video analysis request."""
    user = require_analysis_unlocked(request)
    
    try:
        worker = AnalyzeWorker(settings)
        status = await worker.get_analysis_status(request_id)
        
        logger.info(f"video_analysis_status_checked request_id={request_id} user_id={user.id}")
        
        return VideoAnalysisResponse(
            request_id=request_id,
            status=status["status"],
            message=status.get("message", ""),
            clip_count=status.get("clip_count"),
            render_jobs=status.get("render_jobs", {}),
            bundle_info=status.get("bundle_info"),
        )
        
    except Exception as error:
        logger.error(f"video_analysis_status_failed request_id={request_id} error={str(error)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis status: {str(error)}")


@router.post("/retry/{request_id}")
async def retry_failed_renders(request_id: str, request: Request) -> VideoAnalysisResponse:
    """Retry all failed render jobs for an analysis request."""
    user = require_analysis_unlocked(request)
    
    try:
        worker = AnalyzeWorker(settings)
        result = await worker.retry_failed_renders(request_id)
        
        logger.info(f"video_analysis_retried request_id={request_id} user_id={user.id}")
        
        return VideoAnalysisResponse(
            request_id=request_id,
            status=result["status"],
            message=result.get("message", ""),
            clip_count=result.get("retry_count"),
            render_jobs=None,
            bundle_info=None,
        )
        
    except Exception as error:
        logger.error(f"video_analysis_retry_failed request_id={request_id} error={str(error)}")
        raise HTTPException(status_code=500, detail=f"Failed to retry renders: {str(error)}")


@router.get("/queue-status")
async def get_queue_status(request: Request) -> dict[str, object]:
    """Get current queue status for video analysis."""
    user = require_analysis_unlocked(request)
    
    try:
        worker = AnalyzeWorker(settings)
        queue_status = await worker.render_queue.get_queue_status()
        
        logger.info(f"video_analysis_queue_status_checked user_id={user.id}")
        
        return {
            "queue_length": queue_status["queue_length"],
            "pending_jobs": queue_status["pending_jobs"],
            "processing_jobs": queue_status["processing_jobs"],
            "active_workers": queue_status["active_workers"],
            "total_capacity": queue_status["total_capacity"],
        }
        
    except Exception as error:
        logger.error(f"video_analysis_queue_status_failed user_id={user.id} error={str(error)}")
        raise HTTPException(status_code=500, detail=f"Failed to get queue status: {str(error)}")


@router.post("/export/{request_id}")
async def export_bundle(request_id: str, request: Request) -> dict[str, object]:
    """Export a bundle for a completed analysis request."""
    user = require_analysis_unlocked(request)
    
    try:
        # Get analysis results
        from ...dependencies.auth import get_platform_store
        platform_store = get_platform_store()
        clips = platform_store.get_clip_pack(request_id=request_id)
        
        if not clips:
            raise HTTPException(status_code=404, detail="Analysis request not found")
        
        # Create export bundle
        from ...services.output_builder import OutputBuilder
        output_builder = OutputBuilder(settings)
        bundle = output_builder.create_clip_bundle(
            request_id=request_id,
            clips=clips.get("clips", []),
            bundle_format="zip",
            include_metadata=True,
        )
        
        logger.info(f"video_analysis_export_created request_id={request_id} user_id={user.id}")
        
        return {
            "bundle_id": bundle["bundle_id"],
            "file_name": bundle["file_name"],
            "download_url": bundle["download_url"],
            "clip_count": bundle["clip_count"],
            "size_bytes": bundle["size_bytes"],
        }
        
    except Exception as error:
        logger.error(f"video_analysis_export_failed request_id={request_id} error={str(error)}")
        raise HTTPException(status_code=500, detail=f"Failed to export bundle: {str(error)}")
