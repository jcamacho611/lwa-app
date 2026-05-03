from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
import asyncio
import json

from ..core.config import Settings, get_settings


class RenderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    rendering = "rendering"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class OutputFormat(str, Enum):
    mp4 = "mp4"
    mov = "mov"
    webm = "webm"


class AspectRatio(str, Enum):
    vertical_9_16 = "9:16"
    horizontal_16_9 = "16:9"
    square_1_1 = "1:1"
    vertical_4_5 = "4:5"


class AssetType(str, Enum):
    video = "video"
    image = "image"
    audio = "audio"
    text = "text"
    transition = "transition"


@dataclass(frozen=True)
class TimelineAsset:
    asset_id: str
    asset_type: AssetType
    source_url: str
    start_time: float  # Position in timeline (seconds)
    duration: float   # Duration on timeline (seconds)
    track: int        # Which track (0=video, 1=audio, 2=overlay, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TimelineClip:
    clip_id: str
    assets: List[TimelineAsset]
    start_time: float
    duration: float
    transition_in: Optional[str] = None
    transition_out: Optional[str] = None
    effects: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RenderTimeline:
    timeline_id: str
    clips: List[TimelineClip]
    total_duration: float
    output_format: OutputFormat
    aspect_ratio: AspectRatio
    resolution: str  # e.g., "1080x1920"
    frame_rate: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderJob:
    job_id: str
    user_id: str
    timeline: RenderTimeline
    status: RenderStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_url: Optional[str] = None
    error_message: Optional[str] = None
    progress: int = 0  # 0-100
    provider: str = "shotstack"  # Default provider
    provider_job_id: Optional[str] = None
    cost_estimate: Optional[float] = None


class RenderEngine:
    """Backend render engine that turns timelines into finished MP4s."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.active_jobs: Dict[str, RenderJob] = {}
    
    def create_render_job(
        self,
        *,
        user_id: str,
        clips: List[TimelineClip],
        output_format: OutputFormat = OutputFormat.mp4,
        aspect_ratio: AspectRatio = AspectRatio.vertical_9_16,
        resolution: str = "1080x1920",
        frame_rate: int = 30,
        provider: str = "shotstack",
    ) -> RenderJob:
        """Create a new render job from timeline clips."""
        
        # Calculate total duration
        total_duration = max(
            (clip.start_time + clip.duration) for clip in clips
        ) if clips else 0
        
        # Create timeline
        timeline = RenderTimeline(
            timeline_id=f"timeline_{uuid.uuid4().hex[:8]}",
            clips=clips,
            total_duration=total_duration,
            output_format=output_format,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            frame_rate=frame_rate,
        )
        
        # Create render job
        job = RenderJob(
            job_id=f"render_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            timeline=timeline,
            status=RenderStatus.pending,
            created_at=datetime.now(),
            provider=provider,
        )
        
        # Store job
        self.active_jobs[job.job_id] = job
        
        return job
    
    async def submit_render_job(self, job_id: str) -> bool:
        """Submit render job to provider (Shotstack, etc.)."""
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        
        # Update status
        updated_job = RenderJob(
            **{**job.__dict__, "status": RenderStatus.processing, "started_at": datetime.now()}
        )
        self.active_jobs[job_id] = updated_job
        
        # TODO: Implement actual provider submission
        # For now, simulate async processing
        asyncio.create_task(self._simulate_render_processing(job_id))
        
        return True
    
    async def _simulate_render_processing(self, job_id: str):
        """Simulate render processing (replace with real provider call)."""
        job = self.active_jobs[job_id]
        
        # Simulate processing stages
        stages = [
            (RenderStatus.rendering, 25),
            (RenderStatus.rendering, 50),
            (RenderStatus.rendering, 75),
            (RenderStatus.rendering, 90),
            (RenderStatus.completed, 100),
        ]
        
        for status, progress in stages:
            await asyncio.sleep(2)  # Simulate processing time
            
            updated_job = RenderJob(
                **{**job.__dict__, "status": status, "progress": progress}
            )
            self.active_jobs[job_id] = updated_job
            job = updated_job
        
        # Final completion
        final_job = RenderJob(
            **{**job.__dict__, 
               "status": RenderStatus.completed,
               "progress": 100,
               "completed_at": datetime.now(),
               "output_url": f"https://cdn.lwa.app/renders/{job_id}.mp4"
            }
        )
        self.active_jobs[job_id] = final_job
    
    def get_job_status(self, job_id: str) -> Optional[RenderJob]:
        """Get current status of render job."""
        return self.active_jobs.get(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a render job."""
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        if job.status in [RenderStatus.completed, RenderStatus.failed, RenderStatus.cancelled]:
            return False
        
        updated_job = RenderJob(
            **{**job.__dict__, "status": RenderStatus.cancelled}
        )
        self.active_jobs[job_id] = updated_job
        
        return True
    
    def get_user_jobs(self, user_id: str) -> List[RenderJob]:
        """Get all render jobs for a user."""
        return [job for job in self.active_jobs.values() if job.user_id == user_id]
    
    def create_timeline_from_clips(
        self,
        *,
        clip_data: List[Dict[str, Any]],
        output_format: OutputFormat = OutputFormat.mp4,
        aspect_ratio: AspectRatio = AspectRatio.vertical_9_16,
    ) -> RenderTimeline:
        """Create timeline from clip data (simplified builder)."""
        
        timeline_clips = []
        
        for i, clip_info in enumerate(clip_data):
            # Create assets for this clip
            assets = []
            
            # Main video asset
            if clip_info.get("video_url"):
                assets.append(TimelineAsset(
                    asset_id=f"video_{i}",
                    asset_type=AssetType.video,
                    source_url=clip_info["video_url"],
                    start_time=0,
                    duration=clip_info.get("duration", 5),
                    track=0,
                ))
            
            # Audio asset
            if clip_info.get("audio_url"):
                assets.append(TimelineAsset(
                    asset_id=f"audio_{i}",
                    asset_type=AssetType.audio,
                    source_url=clip_info["audio_url"],
                    start_time=0,
                    duration=clip_info.get("duration", 5),
                    track=1,
                ))
            
            # Text overlay
            if clip_info.get("text"):
                assets.append(TimelineAsset(
                    asset_id=f"text_{i}",
                    asset_type=AssetType.text,
                    source_url=clip_info["text"],
                    start_time=0,
                    duration=clip_info.get("duration", 5),
                    track=2,
                    metadata={"style": "title", "position": "center"}
                ))
            
            # Create timeline clip
            timeline_clip = TimelineClip(
                clip_id=f"clip_{i}",
                assets=assets,
                start_time=clip_info.get("start_time", i * 5),  # Default 5s spacing
                duration=clip_info.get("duration", 5),
                transition_in=clip_info.get("transition_in"),
                transition_out=clip_info.get("transition_out"),
                effects=clip_info.get("effects", []),
            )
            
            timeline_clips.append(timeline_clip)
        
        # Calculate total duration
        total_duration = max(
            (clip.start_time + clip.duration) for clip in timeline_clips
        ) if timeline_clips else 0
        
        return RenderTimeline(
            timeline_id=f"timeline_{uuid.uuid4().hex[:8]}",
            clips=timeline_clips,
            total_duration=total_duration,
            output_format=output_format,
            aspect_ratio=aspect_ratio,
            resolution="1080x1920" if aspect_ratio == AspectRatio.vertical_9_16 else "1920x1080",
        )
    
    def estimate_render_cost(self, timeline: RenderTimeline) -> float:
        """Estimate render cost based on duration and complexity."""
        base_cost = 0.01  # Base cost per render
        duration_cost = timeline.total_duration * 0.002  # $0.002 per second
        complexity_cost = len(timeline.clips) * 0.005  # $0.005 per clip
        
        return base_cost + duration_cost + complexity_cost
    
    def get_supported_formats(self) -> Dict[str, Any]:
        """Get supported output formats and configurations."""
        return {
            "formats": [fmt.value for fmt in OutputFormat],
            "aspect_ratios": [ratio.value for ratio in AspectRatio],
            "resolutions": {
                "9:16": ["1080x1920", "720x1280", "480x854"],
                "16:9": ["1920x1080", "1280x720", "854x480"],
                "1:1": ["1080x1080", "720x720", "480x480"],
                "4:5": ["1080x1350", "720x900", "480x600"],
            },
            "frame_rates": [24, 30, 60],
            "max_duration": 300,  # 5 minutes max
            "max_clips": 50,
        }


# Shotstack-specific implementation (future)
class ShotstackRenderer:
    """Shotstack-specific renderer implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.shotstack.io/v1"
    
    def timeline_to_shotstack(self, timeline: RenderTimeline) -> Dict[str, Any]:
        """Convert LWA timeline to Shotstack format."""
        
        shotstack_timeline = {
            "output": {
                "format": timeline.output_format.value,
                "resolution": timeline.resolution,
                "fps": timeline.frame_rate,
            },
            "timeline": {
                "tracks": []
            }
        }
        
        # Group assets by track
        tracks_by_id = {}
        for clip in timeline.clips:
            for asset in clip.assets:
                if asset.track not in tracks_by_id:
                    tracks_by_id[asset.track] = []
                
                shotstack_clip = {
                    "asset": self._asset_to_shotstack(asset),
                    "start": asset.start_time,
                    "length": asset.duration,
                }
                
                # Add transitions
                if asset.asset_type == AssetType.video and clip.transition_in:
                    shotstack_clip["transition"] = {
                        "type": clip.transition_in,
                        "duration": 0.5
                    }
                
                tracks_by_id[asset.track].append(shotstack_clip)
        
        # Convert to Shotstack track format
        for track_id, clips in tracks_by_id.items():
            shotstack_timeline["timeline"]["tracks"].append({
                "clips": clips
            })
        
        return shotstack_timeline
    
    def _asset_to_shotstack(self, asset: TimelineAsset) -> Dict[str, Any]:
        """Convert LWA asset to Shotstack asset format."""
        if asset.asset_type == AssetType.video:
            return {
                "type": "video",
                "src": asset.source_url
            }
        elif asset.asset_type == AssetType.image:
            return {
                "type": "image",
                "src": asset.source_url
            }
        elif asset.asset_type == AssetType.audio:
            return {
                "type": "audio",
                "src": asset.source_url
            }
        elif asset.asset_type == AssetType.text:
            return {
                "type": "title",
                "text": asset.source_url,
                "style": asset.metadata.get("style", "pop"),
                "position": asset.metadata.get("position", "center")
            }
        else:
            return {
                "type": "video",
                "src": asset.source_url
            }
