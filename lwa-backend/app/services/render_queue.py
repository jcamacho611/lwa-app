from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..core.config import Settings
from ..services.render_job_store import RenderJobStore
from ..services.clip_status_store import update_clip_status

logger = logging.getLogger("uvicorn.error")


class RenderQueueService:
    """Service for managing render job queue and processing."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.job_store = RenderJobStore(settings)
        self._queue = asyncio.Queue()
        self._processing = set()
        self._workers = []
    
    async def start_workers(self, num_workers: int = 2) -> None:
        """Start background workers for processing render jobs."""
        self._workers = [
            asyncio.create_task(self._worker_loop())
            for _ in range(num_workers)
        ]
        logger.info(f"render_queue_started workers={num_workers}")
    
    async def _worker_loop(self) -> None:
        """Worker loop for processing render jobs."""
        while True:
            try:
                # Get next job from queue
                job_data = await self._queue.get()
                if not job_data:
                    await asyncio.sleep(1)
                    continue
                
                job_id = job_data["id"]
                clip_id = job_data["clip_id"]
                request_id = job_data["request_id"]
                
                # Mark as processing
                self._processing.add(job_id)
                
                try:
                    # Process the render job
                    await self._process_render_job(job_data)
                    
                    # Mark as completed
                    self.job_store.update_job(
                        job_id=job_id,
                        status="completed",
                        render_status="completed"
                    )
                    
                    logger.info(f"render_job_completed job_id={job_id} clip_id={clip_id}")
                    
                except Exception as error:
                    # Mark as failed
                    self.job_store.update_job(
                        job_id=job_id,
                        status="failed",
                        error=str(error)
                    )
                    
                    self.job_store.log_job_event(
                        job_id=job_id,
                        level="error",
                        message=str(error)
                    )
                    
                    logger.error(f"render_job_failed job_id={job_id} error={str(error)}")
                
                finally:
                    # Remove from processing set
                    self._processing.discard(job_id)
                    
            except asyncio.CancelledError:
                logger.info("render_queue_worker_stopped")
                break
            except Exception as error:
                logger.error(f"render_queue_worker_error error={str(error)}")
                await asyncio.sleep(5)
    
    async def enqueue_render_job(
        self,
        *,
        clip_id: str,
        request_id: str,
        output_path: Optional[str] = None,
        input_path: Optional[str] = None,
        title_text: str = "",
        subtitle_text: str = "",
    ) -> str:
        """Enqueue a render job for processing."""
        job_id = f"render_job_{uuid4().hex[:12]}"
        
        # Create job in store
        job = self.job_store.create_job(
            clip_id=clip_id,
            request_id=request_id,
            status="queued",
            output_path=output_path,
            input_path=input_path,
            title_text=title_text,
            subtitle_text=subtitle_text,
        )
        
        # Add to queue
        await self._queue.put(job)
        
        # Update clip status to processing
        update_clip_status(
            clip_id=clip_id,
            request_id=request_id,
            updates={
                "render_status": "queued",
                "status": "processing"
            },
        )
        
        logger.info(f"render_job_enqueued job_id={job_id} clip_id={clip_id}")
        return job_id
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status and statistics."""
        pending_jobs = await self.job_store.get_pending_jobs()
        processing_jobs = list(self._processing)
        
        return {
            "queue_length": self._queue.qsize(),
            "pending_jobs": len(pending_jobs),
            "processing_jobs": len(processing_jobs),
            "active_workers": len(self._workers),
            "total_capacity": len(self._workers) * 2,  # 2 jobs per worker
        }
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific render job."""
        return await self.job_store.get_job(job_id)
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a render job if not yet processing."""
        job = await self.job_store.get_job(job_id)
        if not job:
            return False
        
        if job["status"] == "processing":
            return False
        
        # Mark as cancelled
        await self.job_store.update_job(
            job_id=job_id,
            status="cancelled"
        )
        
        logger.info(f"render_job_cancelled job_id={job_id}")
        return True
