"""
Video Service v0

Central service for managing video rendering operations across multiple providers.
Integrates local FFmpeg renderer and cloud providers for flexible video processing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass

from app.models.video_job import VideoJob, VideoJobStatus
from app.services.video.base_renderer import BaseRenderer, RenderContext, RenderResult
from app.services.video.renderers.ffmpeg_renderer import ffmpeg_renderer

logger = logging.getLogger(__name__)


@dataclass
class VideoServiceConfig:
    """Configuration for the video service."""
    
    # Renderer settings
    enable_local_ffmpeg: bool = True
    enable_cloud_providers: bool = True
    
    # Performance settings
    max_concurrent_renders: int = 3
    default_timeout_seconds: int = 3600  # 1 hour
    
    # Quality settings
    default_quality: str = "high"
    enable_gpu_acceleration: bool = True
    
    # Storage settings
    output_base_path: str = "uploads/renders"
    temp_path: str = "temp/video_renders"


class VideoService:
    """
    Central video service managing multiple renderers and job orchestration.
    
    Provides unified interface for video rendering across FFmpeg and cloud providers.
    """
    
    def __init__(self, config: Optional[VideoServiceConfig] = None):
        self.config = config or VideoServiceConfig()
        self.renderers: Dict[str, BaseRenderer] = {}
        self.active_renders: Dict[str, asyncio.Task] = {}
        self.render_semaphore = asyncio.Semaphore(self.config.max_concurrent_renders)
        
        # Initialize renderers
        self._initialize_renderers()
    
    def _initialize_renderers(self):
        """Initialize available video renderers."""
        
        # Add FFmpeg renderer if enabled
        if self.config.enable_local_ffmpeg:
            self.renderers["ffmpeg_local"] = ffmpeg_renderer
            logger.info("FFmpeg local renderer initialized")
        
        # TODO: Add cloud renderers when enabled
        if self.config.enable_cloud_providers:
            # self.renderers["runway"] = runway_renderer
            # self.renderers["pika"] = pika_renderer
            # self.renderers["stable_diffusion_video"] = sdv_renderer
            logger.info("Cloud renderers will be initialized when available")
    
    async def get_available_renderers(self) -> List[Dict[str, Any]]:
        """Get list of available renderers with their capabilities."""
        
        renderers = []
        for name, renderer in self.renderers.items():
            try:
                capabilities = await renderer.get_capabilities()
                renderers.append({
                    "name": name,
                    "display_name": capabilities.get("display_name", name),
                    "version": capabilities.get("version", "unknown"),
                    "available": capabilities.get("available", False),
                    "capabilities": capabilities.get("capabilities", {}),
                    "supported_formats": capabilities.get("supported_formats", []),
                    "max_resolution": capabilities.get("max_resolution", "1080x1920"),
                    "max_duration": capabilities.get("max_duration", 3600),
                    "gpu_acceleration": capabilities.get("gpu_acceleration", False),
                })
            except Exception as e:
                logger.error(f"Failed to get capabilities for renderer {name}: {e}")
                renderers.append({
                    "name": name,
                    "display_name": name,
                    "available": False,
                    "error": str(e)
                })
        
        return renderers
    
    async def render_video(
        self, 
        job: VideoJob, 
        renderer_name: Optional[str] = None,
        timeline: Optional[Dict[str, Any]] = None
    ) -> RenderResult:
        """
        Render video using specified or optimal renderer.
        
        Args:
            job: Video job to render
            renderer_name: Specific renderer to use (optional)
            timeline: Timeline configuration for rendering
            
        Returns:
            RenderResult with output information
        """
        
        # Select renderer
        if renderer_name and renderer_name in self.renderers:
            renderer = self.renderers[renderer_name]
        else:
            renderer = await self._select_optimal_renderer(job)
        
        if not renderer:
            return RenderResult(
                success=False,
                error_message="No suitable renderer available"
            )
        
        # Check if renderer is available
        capabilities = await renderer.get_capabilities()
        if not capabilities.get("available", False):
            return RenderResult(
                success=False,
                error_message=f"Renderer {renderer_name} is not available"
            )
        
        # Validate job compatibility
        if not renderer.supports_duration(job.duration_seconds):
            return RenderResult(
                success=False,
                error_message=f"Duration {job.duration_seconds}s exceeds renderer limit"
            )
        
        if not renderer.supports_resolution(job.resolution or "1080x1920"):
            return RenderResult(
                success=False,
                error_message=f"Resolution {job.resolution} not supported by renderer"
            )
        
        # Create render context
        context = RenderContext(
            job=job,
            timeline=timeline,
            render_settings={
                "quality": self.config.default_quality,
                "enable_gpu": self.config.enable_gpu_acceleration,
                "timeout": self.config.default_timeout_seconds,
            },
            temp_dir=self.config.temp_path
        )
        
        # Execute render with concurrency control
        async with self.render_semaphore:
            try:
                # Check if job is already being rendered
                if job.job_id in self.active_renders:
                    return RenderResult(
                        success=False,
                        error_message="Job is already being rendered"
                    )
                
                # Start render task
                render_task = asyncio.create_task(
                    self._execute_render_with_timeout(renderer, context)
                )
                self.active_renders[job.job_id] = render_task
                
                # Wait for completion
                result = await render_task
                
                # Clean up
                del self.active_renders[job.job_id]
                
                # Cleanup temporary files
                await renderer.cleanup(context)
                
                return result
                
            except asyncio.TimeoutError:
                logger.error(f"Render timeout for job {job.job_id}")
                del self.active_renders[job.job_id]
                await renderer.cleanup(context)
                
                return RenderResult(
                    success=False,
                    error_message="Render operation timed out"
                )
            
            except Exception as e:
                logger.error(f"Render failed for job {job.job_id}: {e}")
                if job.job_id in self.active_renders:
                    del self.active_renders[job.job_id]
                await renderer.cleanup(context)
                
                return RenderResult(
                    success=False,
                    error_message=str(e)
                )
    
    async def _execute_render_with_timeout(
        self, 
        renderer: BaseRenderer, 
        context: RenderContext
    ) -> RenderResult:
        """Execute render with timeout handling."""
        
        timeout = context.render_settings.get("timeout", self.config.default_timeout_seconds)
        
        try:
            return await asyncio.wait_for(
                renderer.render(context),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise
    
    async def _select_optimal_renderer(self, job: VideoJob) -> Optional[BaseRenderer]:
        """Select the optimal renderer for the given job."""
        
        available_renderers = []
        
        for name, renderer in self.renderers.items():
            try:
                capabilities = await renderer.get_capabilities()
                
                # Check availability and compatibility
                if (capabilities.get("available", False) and
                    renderer.supports_duration(job.duration_seconds) and
                    renderer.supports_resolution(job.resolution or "1080x1920")):
                    
                    available_renderers.append((name, renderer, capabilities))
                    
            except Exception as e:
                logger.warning(f"Failed to check renderer {name}: {e}")
        
        if not available_renderers:
            return None
        
        # Prioritize local FFmpeg for speed and cost
        for name, renderer, capabilities in available_renderers:
            if name == "ffmpeg_local":
                return renderer
        
        # Return first available renderer
        return available_renderers[0][1]
    
    async def get_render_progress(self, job_id: str) -> Optional[float]:
        """Get render progress for a specific job."""
        
        # Try to get progress from active renders
        if job_id in self.active_renders:
            # Check each renderer for progress
            for renderer in self.renderers.values():
                try:
                    progress = await renderer.get_render_progress(job_id)
                    if progress is not None:
                        return progress
                except Exception as e:
                    logger.warning(f"Failed to get progress from renderer: {e}")
        
        return None
    
    async def cancel_render(self, job_id: str) -> bool:
        """Cancel an active render job."""
        
        if job_id not in self.active_renders:
            return False
        
        try:
            # Cancel the task
            render_task = self.active_renders[job_id]
            render_task.cancel()
            
            # Try renderer-specific cancellation
            for renderer in self.renderers.values():
                try:
                    cancelled = await renderer.cancel_render(job_id)
                    if cancelled:
                        break
                except Exception as e:
                    logger.warning(f"Renderer cancellation failed: {e}")
            
            # Clean up
            del self.active_renders[job_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel render {job_id}: {e}")
            return False
    
    async def test_all_renderers(self) -> Dict[str, bool]:
        """Test all available renderers."""
        
        results = {}
        
        for name, renderer in self.renderers.items():
            try:
                results[name] = await renderer.test_render()
            except Exception as e:
                logger.error(f"Test failed for renderer {name}: {e}")
                results[name] = False
        
        return results
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get overall service status and statistics."""
        
        # Get renderer status
        renderers = await self.get_available_renderers()
        
        # Count active renders
        active_count = len(self.active_renders)
        
        # Get system resource info
        import psutil
        system_info = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        }
        
        return {
            "service_name": "LWA Video Service",
            "version": "1.0.0",
            "status": "healthy" if len(renderers) > 0 else "degraded",
            "renderers": renderers,
            "active_renders": active_count,
            "max_concurrent_renders": self.config.max_concurrent_renders,
            "system_info": system_info,
            "config": {
                "enable_local_ffmpeg": self.config.enable_local_ffmpeg,
                "enable_cloud_providers": self.config.enable_cloud_providers,
                "default_timeout": self.config.default_timeout_seconds,
            }
        }
    
    async def cleanup_completed_renders(self) -> int:
        """Clean up completed render tasks."""
        
        completed_count = 0
        
        for job_id, task in list(self.active_renders.items()):
            if task.done():
                del self.active_renders[job_id]
                completed_count += 1
        
        return completed_count


# Singleton instance
video_service = VideoService()
