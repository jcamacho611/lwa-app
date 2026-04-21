from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from ..core.config import Settings
from ..models.schemas import ClipBatchResponse
from ..services.clip_analysis_service import run_video_analysis
from ..dependencies.auth import get_platform_store
from ..services.render_queue import RenderQueueService
from ..services.render_job_store import RenderJobStore
from ..services.output_builder import OutputBuilder

logger = logging.getLogger("uvicorn.error")


class AnalyzeWorker:
    """Background worker for processing video analysis and queuing renders."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.platform_store = get_platform_store()
        self.render_queue = RenderQueueService(settings)
        self.job_store = RenderJobStore(settings)
        self.output_builder = OutputBuilder(settings)
        self._running = False
    
    async def start(self, num_workers: int = 2) -> None:
        """Start the analyze worker with background processes."""
        if self._running:
            logger.warning("analyze_worker_already_running")
            return
        
        self._running = True
        await self.render_queue.start_workers(num_workers)
        logger.info(f"analyze_worker_started workers={num_workers}")
    
    async def stop(self) -> None:
        """Stop the analyze worker."""
        self._running = False
        logger.info("analyze_worker_stopped")
    
    async def process_video_analysis(
        self,
        *,
        request_id: str,
        video_url: Optional[str] = None,
        upload_file_id: Optional[str] = None,
        target_platform: Optional[str] = None,
        mode: Optional[str] = None,
    ) -> ClipBatchResponse:
        """Process a complete video analysis workflow."""
        try:
            logger.info(f"video_analysis_started request_id={request_id}")
            
            # Step 1: Source ingestion
            if video_url:
                from ..services.source_ingest import SourceIngestService
                ingest_service = SourceIngestService(self.settings)
                source_data = await ingest_service.ingest_from_url(video_url)
                local_path = source_data.get("local_path")
            elif upload_file_id:
                from ..services.source_ingest import SourceIngestService
                ingest_service = SourceIngestService(self.settings)
                source_data = await ingest_service.ingest_from_upload(upload_file_id)
                local_path = source_data.get("local_path")
            else:
                raise ValueError("Either video_url or upload_file_id must be provided")
            
            # Step 2: Video analysis
            analysis_result = run_video_analysis(
                settings=self.settings,
                video_id=request_id,
                video_url=video_url,
                target_platform=target_platform,
                mode=mode,
            )
            
            # Step 3: Queue render jobs for all clips
            render_job_ids = []
            for clip in analysis_result.clips:
                if clip.id and clipHasRenderableMedia(clip):
                    job_id = await self.render_queue.enqueue_render_job(
                        clip_id=clip.id,
                        request_id=request_id,
                        input_path=local_path,
                        title_text=clip.hook or "",
                        subtitle_text=clip.caption or "",
                    )
                    render_job_ids.append(job_id)
            
            # Step 4: Create output bundle if requested
            bundle_info = None
            if len(render_job_ids) > 0:
                bundle_info = await self.output_builder.create_clip_bundle(
                    request_id=request_id,
                    clips=[clip.model_dump() for clip in analysis_result.clips if clipHasRenderableMedia(clip)],
                    bundle_format="zip",
                    include_metadata=True,
                )
            
            # Step 5: Persist analysis results
            self.platform_store.persist_clip_batch(
                request_id=request_id,
                user_id=None,  # Will be set by auth middleware
                campaign_id=None,
                response=analysis_result,
                local_asset_paths={
                    clip.id: local_path
                    for clip in analysis_result.clips
                    if clip.id and clipHasRenderableMedia(clip)
                },
            )
            
            logger.info(f"video_analysis_completed request_id={request_id} clips={len(analysis_result.clips)} render_jobs={len(render_job_ids)}")
            
            return analysis_result.model_copy(update={
                "render_job_ids": render_job_ids,
                "bundle_info": bundle_info,
            })
            
        except Exception as error:
            logger.error(f"video_analysis_failed request_id={request_id} error={str(error)}")
            raise
    
    async def get_analysis_status(self, request_id: str) -> Dict[str, Any]:
        """Get current status of video analysis."""
        # Check if analysis exists
        clips = self.platform_store.get_clip_pack(request_id=request_id)
        if not clips:
            return {"status": "not_found", "request_id": request_id}
        
        # Get render job status
        render_jobs = []
        for clip in clips.get("clips", []):
            if clip.get("id"):
                jobs = self.job_store.get_jobs_by_clip(clip["id"])
                render_jobs.extend(jobs)
        
        # Determine overall status
        if not render_jobs:
            return {
                "status": "analysis_complete",
                "request_id": request_id,
                "clip_count": len(clips.get("clips", [])),
            }
        
        # Check render job statuses
        completed_jobs = [job for job in render_jobs if job.get("status") == "completed"]
        failed_jobs = [job for job in render_jobs if job.get("status") == "failed"]
        processing_jobs = [job for job in render_jobs if job.get("status") in ["queued", "rendering"]]
        
        overall_status = "processing"
        if len(completed_jobs) == len(render_jobs):
            overall_status = "completed"
        elif len(failed_jobs) > 0:
            overall_status = "completed_with_errors"
        
        return {
            "status": overall_status,
            "request_id": request_id,
            "clip_count": len(clips.get("clips", [])),
            "render_jobs": {
                "total": len(render_jobs),
                "completed": len(completed_jobs),
                "failed": len(failed_jobs),
                "processing": len(processing_jobs),
            },
        }
    
    async def retry_failed_renders(self, request_id: str) -> Dict[str, Any]:
        """Retry all failed render jobs for a request."""
        clips = self.platform_store.get_clip_pack(request_id=request_id)
        if not clips:
            return {"status": "not_found", "request_id": request_id}
        
        retry_count = 0
        for clip in clips.get("clips", []):
            if not clip.get("id"):
                continue
            
            # Get failed jobs for this clip
            jobs = self.job_store.get_jobs_by_clip(clip["id"])
            failed_jobs = [job for job in jobs if job.get("status") == "failed"]
            
            for job in failed_jobs:
                # Re-queue the failed job
                job_id = await self.render_queue.enqueue_render_job(
                    clip_id=clip["id"],
                    request_id=request_id,
                    input_path=job.get("input_path"),
                    title_text=job.get("title_text", ""),
                    subtitle_text=job.get("subtitle_text", ""),
                )
                retry_count += 1
        
        logger.info(f"render_jobs_retried request_id={request_id} retried={retry_count}")
        return {
            "status": "retried",
            "request_id": request_id,
            "retry_count": retry_count,
        }


def clipHasRenderableMedia(clip: Any) -> bool:
    """Check if a clip has media that can be rendered."""
    return bool(
        getattr(clip, "preview_url", None) or
        getattr(clip, "download_url", None) or
        getattr(clip, "raw_clip_url", None)
    )
