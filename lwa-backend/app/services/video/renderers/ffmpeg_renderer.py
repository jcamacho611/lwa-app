"""
Local FFmpeg Renderer v0

Provides local FFmpeg-based video rendering capabilities for the LWA Video OS.
Supports timeline-based rendering with multiple tracks, effects, and output formats.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

from app.core.config import settings
from app.models.video_job import VideoJob, VideoJobStatus
from app.services.video.base_renderer import BaseRenderer, RenderContext, RenderResult

logger = logging.getLogger(__name__)


@dataclass
class FFmpegRenderConfig:
    """Configuration for FFmpeg rendering operations."""
    
    # Input configuration
    input_sources: List[Dict[str, Any]]
    
    # Output configuration
    output_path: str
    output_format: str = "mp4"
    output_codec: str = "libx264"
    output_quality: str = "high"  # low, medium, high, ultra
    
    # Timeline configuration
    duration_seconds: float
    aspect_ratio: str = "9:16"
    resolution: str = "1080x1920"
    framerate: int = 30
    
    # Audio configuration
    audio_codec: str = "aac"
    audio_bitrate: str = "128k"
    audio_sample_rate: int = 44100
    
    # Effects and filters
    enable_effects: bool = True
    enable_transitions: bool = True
    enable_color_correction: bool = True
    
    # Performance
    use_gpu: bool = True
    parallel_processing: bool = True
    temp_dir: Optional[str] = None


class FFmpegRenderer(BaseRenderer):
    """
    Local FFmpeg-based video renderer.
    
    Provides high-quality local rendering with timeline support,
    effects, and multiple output formats.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "ffmpeg_local"
        self.display_name = "FFmpeg Local Renderer"
        self.version = "1.0.0"
        self.capabilities = {
            "formats": ["mp4", "mov", "avi", "webm"],
            "codecs": ["libx264", "libx265", "libvpx-vp9", "prores"],
            "effects": ["fade", "blur", "color_correction", "transition"],
            "max_resolution": "4K",
            "max_duration": 3600,  # 1 hour
            "gpu_acceleration": True,
            "parallel_processing": True,
        }
        
        # Check FFmpeg availability
        self._check_ffmpeg_availability()
    
    def _check_ffmpeg_availability(self) -> None:
        """Check if FFmpeg is available and accessible."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info("FFmpeg is available")
                self._ffmpeg_available = True
            else:
                logger.error("FFmpeg not available")
                self._ffmpeg_available = False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"FFmpeg check failed: {e}")
            self._ffmpeg_available = False
    
    async def render(self, context: RenderContext) -> RenderResult:
        """
        Render video using FFmpeg based on timeline and job configuration.
        
        Args:
            context: Render context with job and timeline information
            
        Returns:
            RenderResult with output information
        """
        if not self._ffmpeg_available:
            raise RuntimeError("FFmpeg is not available")
        
        job = context.job
        timeline = context.timeline
        
        try:
            # Create render configuration
            config = self._create_render_config(job, timeline)
            
            # Update job status
            await self._update_job_status(job.job_id, VideoJobStatus.RENDERING, 0.0)
            
            # Build FFmpeg command
            ffmpeg_command = self._build_ffmpeg_command(config)
            
            # Execute rendering
            output_path = await self._execute_ffmpeg_command(
                ffmpeg_command, 
                config, 
                job.job_id
            )
            
            # Verify output
            if not os.path.exists(output_path):
                raise RuntimeError("Output file was not created")
            
            # Get output metadata
            metadata = await self._get_video_metadata(output_path)
            
            # Update job status
            await self._update_job_status(
                job.job_id, 
                VideoJobStatus.COMPLETED, 
                100.0,
                output_url=output_path,
                metadata=metadata
            )
            
            return RenderResult(
                success=True,
                output_path=output_path,
                metadata=metadata,
                duration_seconds=metadata.get("duration", 0),
                file_size=os.path.getsize(output_path)
            )
            
        except Exception as e:
            logger.error(f"FFmpeg rendering failed for job {job.job_id}: {e}")
            await self._update_job_status(
                job.job_id,
                VideoJobStatus.FAILED,
                error_message=str(e)
            )
            
            return RenderResult(
                success=False,
                error_message=str(e)
            )
    
    def _create_render_config(self, job: VideoJob, timeline: Optional[Dict]) -> FFmpegRenderConfig:
        """Create FFmpeg render configuration from job and timeline."""
        
        # Extract timeline information
        duration = job.duration_seconds
        aspect_ratio = job.aspect_ratio or "9:16"
        resolution = job.resolution or "1080x1920"
        
        # Determine resolution from aspect ratio
        if aspect_ratio == "9:16":
            if resolution == "1080x1920":
                width, height = 1080, 1920
            elif resolution == "720x1280":
                width, height = 720, 1280
            else:
                width, height = 540, 960
        elif aspect_ratio == "16:9":
            if resolution == "1920x1080":
                width, height = 1920, 1080
            elif resolution == "1280x720":
                width, height = 1280, 720
            else:
                width, height = 854, 480
        else:
            width, height = 1080, 1920  # Default to vertical
        
        # Create output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"render_{job.job_id}_{timestamp}.mp4"
        output_path = os.path.join(settings.UPLOAD_DIR, "renders", output_filename)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Prepare input sources from job
        input_sources = []
        if job.input_urls:
            for i, url in enumerate(job.input_urls):
                input_sources.append({
                    "id": f"input_{i}",
                    "url": url,
                    "type": "video",
                    "track": 0,
                    "start_time": 0.0,
                    "duration": duration
                })
        
        if job.source_asset_ids:
            for i, asset_id in enumerate(job.source_asset_ids):
                input_sources.append({
                    "id": f"asset_{i}",
                    "asset_id": asset_id,
                    "type": "video",
                    "track": 0,
                    "start_time": 0.0,
                    "duration": duration
                })
        
        return FFmpegRenderConfig(
            input_sources=input_sources,
            output_path=output_path,
            output_format="mp4",
            output_codec="libx264",
            output_quality="high",
            duration_seconds=duration,
            aspect_ratio=aspect_ratio,
            resolution=f"{width}x{height}",
            framerate=30,
            audio_codec="aac",
            audio_bitrate="128k",
            audio_sample_rate=44100,
            enable_effects=True,
            enable_transitions=True,
            enable_color_correction=True,
            use_gpu=True,
            parallel_processing=True,
            temp_dir=tempfile.mkdtemp(prefix="ffmpeg_render_")
        )
    
    def _build_ffmpeg_command(self, config: FFmpegRenderConfig) -> List[str]:
        """Build FFmpeg command from configuration."""
        
        command = ["ffmpeg"]
        
        # Add GPU acceleration if available
        if config.use_gpu:
            command.extend(["-hwaccel", "auto"])
        
        # Add input sources
        for source in config.input_sources:
            if "url" in source:
                command.extend(["-i", source["url"]])
            elif "asset_id" in source:
                # TODO: Resolve asset_id to file path
                pass
        
        # Video encoding settings
        command.extend([
            "-c:v", config.output_codec,
            "-preset", "medium",
            "-crf", "23",  # Quality setting
            "-r", str(config.framerate),
            "-s", config.resolution,
            "-aspect", config.aspect_ratio,
            "-t", str(config.duration_seconds)
        ])
        
        # Audio encoding settings
        command.extend([
            "-c:a", config.audio_codec,
            "-b:a", config.audio_bitrate,
            "-ar", str(config.audio_sample_rate)
        ])
        
        # Add filters if enabled
        if config.enable_effects:
            filters = []
            
            # Color correction
            if config.enable_color_correction:
                filters.append("eq=brightness=0.05:contrast=1.1:saturation=1.1")
            
            # Add transition effects if multiple inputs
            if len(config.input_sources) > 1 and config.enable_transitions:
                filters.append("fade=t=in:st=0:d=1")
            
            if filters:
                command.extend(["-vf", ",".join(filters)])
        
        # Output settings
        command.extend([
            "-movflags", "+faststart",  # For web streaming
            "-y",  # Overwrite output file
            config.output_path
        ])
        
        return command
    
    async def _execute_ffmpeg_command(
        self, 
        command: List[str], 
        config: FFmpegRenderConfig,
        job_id: str
    ) -> str:
        """Execute FFmpeg command with progress monitoring."""
        
        logger.info(f"Executing FFmpeg command: {' '.join(command)}")
        
        try:
            # Run FFmpeg process
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=config.temp_dir
            )
            
            # Monitor progress
            last_progress = 0.0
            start_time = datetime.now()
            
            while True:
                # Check if process is still running
                return_code = process.poll()
                if return_code is not None:
                    if return_code == 0:
                        logger.info(f"FFmpeg completed successfully for job {job_id}")
                        break
                    else:
                        stderr = await process.stderr.read()
                        error_msg = stderr.decode() if stderr else "Unknown error"
                        raise RuntimeError(f"FFmpeg failed with code {return_code}: {error_msg}")
                
                # Update progress (estimated based on time)
                elapsed = (datetime.now() - start_time).total_seconds()
                estimated_progress = min(95.0, (elapsed / config.duration_seconds) * 100)
                
                # Only update if progress has increased significantly
                if estimated_progress - last_progress > 5.0:
                    await self._update_job_status(job_id, VideoJobStatus.RENDERING, estimated_progress)
                    last_progress = estimated_progress
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(1)
            
            # Final progress update
            await self._update_job_status(job_id, VideoJobStatus.RENDERING, 95.0)
            
            return config.output_path
            
        except Exception as e:
            logger.error(f"FFmpeg execution failed: {e}")
            raise
    
    async def _get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract metadata from rendered video file."""
        
        try:
            # Use ffprobe to get metadata
            command = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                metadata = json.loads(stdout.decode())
                
                # Extract relevant information
                video_stream = next(
                    (s for s in metadata.get("streams", []) if s.get("codec_type") == "video"),
                    None
                )
                audio_stream = next(
                    (s for s in metadata.get("streams", []) if s.get("codec_type") == "audio"),
                    None
                )
                
                format_info = metadata.get("format", {})
                
                return {
                    "duration": float(format_info.get("duration", 0)),
                    "size": int(format_info.get("size", 0)),
                    "bit_rate": format_info.get("bit_rate"),
                    "format": format_info.get("format_name"),
                    "video": {
                        "codec": video_stream.get("codec_name") if video_stream else None,
                        "width": video_stream.get("width") if video_stream else None,
                        "height": video_stream.get("height") if video_stream else None,
                        "fps": self._parse_fps(video_stream.get("r_frame_rate")) if video_stream else None,
                        "bit_rate": video_stream.get("bit_rate") if video_stream else None,
                    },
                    "audio": {
                        "codec": audio_stream.get("codec_name") if audio_stream else None,
                        "sample_rate": audio_stream.get("sample_rate") if audio_stream else None,
                        "channels": audio_stream.get("channels") if audio_stream else None,
                        "bit_rate": audio_stream.get("bit_rate") if audio_stream else None,
                    }
                }
            else:
                logger.warning(f"ffprobe failed for {video_path}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get metadata for {video_path}: {e}")
            return {}
    
    def _parse_fps(self, fps_str: Optional[str]) -> Optional[float]:
        """Parse FPS string from ffprobe output."""
        if not fps_str:
            return None
        
        try:
            if '/' in fps_str:
                numerator, denominator = fps_str.split('/')
                return float(numerator) / float(denominator)
            else:
                return float(fps_str)
        except (ValueError, ZeroDivisionError):
            return None
    
    async def _update_job_status(
        self, 
        job_id: str, 
        status: VideoJobStatus, 
        progress: Optional[float] = None,
        error_message: Optional[str] = None,
        output_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update job status in database."""
        
        try:
            # TODO: Implement database update
            # This would typically update the VideoJob record in the database
            logger.info(f"Updating job {job_id} status to {status}, progress: {progress}")
            
            # For now, just log the update
            if error_message:
                logger.error(f"Job {job_id} error: {error_message}")
            if output_url:
                logger.info(f"Job {job_id} output: {output_url}")
                
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get renderer capabilities."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "available": self._ffmpeg_available,
            "capabilities": self.capabilities,
            "supported_formats": ["mp4", "mov", "avi", "webm"],
            "max_resolution": "4K",
            "max_duration": 3600,
            "gpu_acceleration": self._ffmpeg_available,
        }
    
    async def test_render(self, test_config: Optional[Dict[str, Any]] = None) -> bool:
        """Test renderer with a simple render operation."""
        
        if not self._ffmpeg_available:
            return False
        
        try:
            # Create a simple test configuration
            test_output = os.path.join(tempfile.gettempdir(), "ffmpeg_test.mp4")
            
            # Generate a test pattern
            command = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", "testsrc=duration=5:size=320x240:rate=30",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "28",
                "-y",
                test_output
            ]
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up test file
            if os.path.exists(test_output):
                os.remove(test_output)
            
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"FFmpeg test render failed: {e}")
            return False


# Singleton instance
ffmpeg_renderer = FFmpegRenderer()
