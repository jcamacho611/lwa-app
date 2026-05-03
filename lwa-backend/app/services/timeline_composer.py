from __future__ import annotations

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class TimelineTrackType(Enum):
    """Types of timeline tracks."""
    VIDEO = "video"
    BROLL = "broll"
    AUDIO = "audio"
    CAPTIONS = "captions"
    OVERLAYS = "overlays"
    VOICEOVER = "voiceover"
    MUSIC = "music"


class TimelineStatus(Enum):
    """Status of timeline composition."""
    DRAFT = "draft"
    COMPOSING = "composing"
    READY = "ready"
    FAILED = "failed"
    SENT_TO_RENDER = "sent_to_render"


@dataclass
class TimelineAssetRef:
    """Reference to an asset used in timeline."""
    asset_id: Optional[str] = None
    asset_type: Optional[str] = None
    source_url: Optional[str] = None
    start_time: float = 0.0
    end_time: Optional[float] = None
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TimelineSegment:
    """A segment within a timeline track."""
    segment_id: str
    track_type: TimelineTrackType
    start_time: float
    duration: float
    asset_ref: Optional[TimelineAssetRef] = None
    content: Optional[str] = None  # For text overlays, captions, etc.
    style: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TimelineTrack:
    """A track in the timeline."""
    track_id: str
    track_type: TimelineTrackType
    segments: List[TimelineSegment] = field(default_factory=list)
    muted: bool = False
    volume: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TimelineCaptionLayer:
    """Caption layer configuration."""
    style: Optional[str] = None
    position: str = "bottom"
    font_size: str = "medium"
    color: str = "white"
    background: str = "none"
    timing: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TimelineAudioLayer:
    """Audio layer configuration."""
    track_type: str
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    ducking: bool = False
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TimelineOverlayLayer:
    """Overlay layer configuration."""
    overlay_type: str
    position: str = "center"
    opacity: float = 1.0
    duration: float = 0.0
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TimelineRenderSettings:
    """Render settings for the timeline."""
    aspect_ratio: str = "9:16"
    resolution: str = "1080p"
    frame_rate: float = 30.0
    quality: str = "medium"
    format: str = "mp4"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TimelinePlan:
    """A complete timeline plan."""
    timeline_id: str
    user_id: str
    status: TimelineStatus
    title: str
    strategy_summary: str
    total_duration_seconds: float
    aspect_ratio: str
    render_settings: TimelineRenderSettings
    tracks: List[TimelineTrack] = field(default_factory=list)
    caption_layer: Optional[TimelineCaptionLayer] = None
    audio_layers: List[TimelineAudioLayer] = field(default_factory=list)
    overlay_layers: List[TimelineOverlayLayer] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommended_render_job_payload: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class TimelineComposerRequest:
    """Request to compose a timeline."""
    source_asset_ids: Optional[List[str]] = None
    clip_ids: Optional[List[str]] = None
    input_urls: Optional[List[str]] = None
    prompt: Optional[str] = None
    goal: Optional[str] = None
    platform: Optional[str] = None
    aspect_ratio: Optional[str] = None
    duration_seconds: Optional[float] = None
    style_preset: Optional[str] = None
    caption_style: Optional[str] = None
    music_style: Optional[str] = None
    include_cta: bool = False
    include_hook: bool = False
    include_broll: bool = False
    include_captions: bool = False


class TimelineComposer:
    """Service for composing timeline plans."""
    
    def __init__(self) -> None:
        self._timelines: Dict[str, TimelinePlan] = {}  # In-memory storage for v0
    
    def compose_timeline(self, request: TimelineComposerRequest, user_id: str = "guest:unknown") -> TimelinePlan:
        """Compose a timeline plan from the request."""
        timeline_id = f"timeline_{uuid4().hex}"
        
        # Set defaults
        aspect_ratio = request.aspect_ratio or "9:16"
        duration_seconds = request.duration_seconds or 30.0
        platform = request.platform or "tiktok"
        
        # Create render settings
        render_settings = TimelineRenderSettings(
            aspect_ratio=aspect_ratio,
            resolution="1080p",
            frame_rate=30.0,
            quality="medium",
            format="mp4"
        )
        
        # Create timeline plan
        timeline = TimelinePlan(
            timeline_id=timeline_id,
            user_id=user_id,
            status=TimelineStatus.READY,
            title=self._generate_title(request),
            strategy_summary=self._generate_strategy_summary(request),
            total_duration_seconds=duration_seconds,
            aspect_ratio=aspect_ratio,
            render_settings=render_settings
        )
        
        # Compose tracks based on request
        self._compose_video_track(timeline, request)
        self._compose_audio_track(timeline, request)
        self._compose_caption_track(timeline, request)
        self._compose_overlay_track(timeline, request)
        self._compose_broll_track(timeline, request)
        
        # Generate render job payload
        timeline.recommended_render_job_payload = self._generate_render_payload(timeline, request)
        
        # Store timeline
        self._timelines[timeline_id] = timeline
        
        return timeline
    
    def get_timeline(self, timeline_id: str) -> Optional[TimelinePlan]:
        """Get a timeline by ID."""
        return self._timelines.get(timeline_id)
    
    def list_timelines(self, user_id: Optional[str] = None) -> List[TimelinePlan]:
        """List timelines, optionally filtered by user."""
        timelines = list(self._timelines.values())
        if user_id:
            timelines = [timeline for timeline in timelines if timeline.user_id == user_id]
        # Sort by created_at descending
        timelines.sort(key=lambda x: x.created_at, reverse=True)
        return timelines
    
    def delete_timeline(self, timeline_id: str) -> bool:
        """Delete a timeline."""
        if timeline_id in self._timelines:
            del self._timelines[timeline_id]
            return True
        return False
    
    def send_to_render(self, timeline_id: str) -> Dict[str, Any]:
        """Send timeline to render engine."""
        timeline = self.get_timeline(timeline_id)
        if not timeline:
            return {"error": "Timeline not found"}
        
        # Update status
        timeline.status = TimelineStatus.SENT_TO_RENDER
        timeline.updated_at = datetime.utcnow().isoformat()
        
        # Check if render engine is available (mock for v0)
        render_available = True  # In v0, we assume it's available
        
        if not render_available:
            return {
                "error": "render_engine_not_available",
                "message": "Render engine is not available"
            }
        
        # Create render job payload
        render_payload = timeline.recommended_render_job_payload or self._generate_render_payload(timeline)
        
        return {
            "success": True,
            "timeline_id": timeline_id,
            "render_job_payload": render_payload,
            "message": "Timeline sent to render engine"
        }
    
    def _generate_title(self, request: TimelineComposerRequest) -> str:
        """Generate a title for the timeline."""
        if request.prompt:
            # Extract first few words from prompt
            words = request.prompt.split()[:5]
            return " ".join(words).title() + " Timeline"
        
        if request.goal:
            return f"{request.goal.title()} Video Timeline"
        
        return "Generated Video Timeline"
    
    def _generate_strategy_summary(self, request: TimelineComposerRequest) -> str:
        """Generate a strategy summary."""
        parts = []
        
        if request.goal:
            parts.append(f"Goal: {request.goal}")
        
        if request.platform:
            parts.append(f"Platform: {request.platform}")
        
        if request.style_preset:
            parts.append(f"Style: {request.style_preset}")
        
        if request.include_cta:
            parts.append("Includes CTA")
        
        if request.include_hook:
            parts.append("Includes hook")
        
        if request.include_captions:
            parts.append("Includes captions")
        
        if not parts:
            return "Standard video composition"
        
        return " | ".join(parts)
    
    def _compose_video_track(self, timeline: TimelinePlan, request: TimelineComposerRequest) -> None:
        """Compose the main video track."""
        video_track = TimelineTrack(
            track_id=f"track_video_{uuid4().hex}",
            track_type=TimelineTrackType.VIDEO
        )
        
        current_time = 0.0
        
        # Hook segment first if requested
        if request.include_hook:
            hook_segment = TimelineSegment(
                segment_id=f"segment_hook_{uuid4().hex}",
                track_type=TimelineTrackType.VIDEO,
                start_time=current_time,
                duration=3.0,  # 3 second hook
                content="Hook: " + (request.prompt or "Engaging opening"),
                style=request.style_preset
            )
            video_track.segments.append(hook_segment)
            current_time += 3.0
        
        # Main content from source assets or URLs
        if request.source_asset_ids:
            for i, asset_id in enumerate(request.source_asset_ids):
                asset_ref = TimelineAssetRef(
                    asset_id=asset_id,
                    start_time=current_time,
                    duration=10.0  # Default 10 seconds per asset
                )
                segment = TimelineSegment(
                    segment_id=f"segment_asset_{i}_{uuid4().hex}",
                    track_type=TimelineTrackType.VIDEO,
                    start_time=current_time,
                    duration=10.0,
                    asset_ref=asset_ref
                )
                video_track.segments.append(segment)
                current_time += 10.0
        elif request.input_urls:
            for i, url in enumerate(request.input_urls):
                asset_ref = TimelineAssetRef(
                    source_url=url,
                    start_time=current_time,
                    duration=10.0
                )
                segment = TimelineSegment(
                    segment_id=f"segment_url_{i}_{uuid4().hex}",
                    track_type=TimelineTrackType.VIDEO,
                    start_time=current_time,
                    duration=10.0,
                    asset_ref=asset_ref
                )
                video_track.segments.append(segment)
                current_time += 10.0
        
        # CTA segment last if requested
        if request.include_cta and current_time < timeline.total_duration_seconds - 3.0:
            cta_start = timeline.total_duration_seconds - 3.0
            cta_segment = TimelineSegment(
                segment_id=f"segment_cta_{uuid4().hex}",
                track_type=TimelineTrackType.VIDEO,
                start_time=cta_start,
                duration=3.0,
                content="CTA: " + (request.goal or "Call to action"),
                style=request.style_preset
            )
            video_track.segments.append(cta_segment)
        
        timeline.tracks.append(video_track)
    
    def _compose_audio_track(self, timeline: TimelinePlan, request: TimelineComposerRequest) -> None:
        """Compose audio track."""
        if request.music_style:
            audio_layer = TimelineAudioLayer(
                track_type="music",
                volume=0.3,  # Background music volume
                metadata={"style": request.music_style}
            )
            timeline.audio_layers.append(audio_layer)
    
    def _compose_caption_track(self, timeline: TimelinePlan, request: TimelineComposerRequest) -> None:
        """Compose caption track."""
        if request.include_captions:
            caption_layer = TimelineCaptionLayer(
                style=request.caption_style or "default",
                position="bottom"
            )
            
            # Generate mock caption timing
            video_segments = [seg for track in timeline.tracks if track.track_type == TimelineTrackType.VIDEO for seg in track.segments]
            for segment in video_segments:
                caption_timing = {
                    "start": segment.start_time,
                    "end": segment.start_time + segment.duration,
                    "text": segment.content or f"Caption for {segment.segment_id}"
                }
                caption_layer.timing.append(caption_timing)
            
            timeline.caption_layer = caption_layer
    
    def _compose_overlay_track(self, timeline: TimelinePlan, request: TimelineComposerRequest) -> None:
        """Compose overlay track."""
        if request.style_preset and request.style_preset != "minimal":
            overlay_layer = TimelineOverlayLayer(
                overlay_type="style_overlay",
                position="bottom_right",
                opacity=0.8,
                metadata={"style": request.style_preset}
            )
            timeline.overlay_layers.append(overlay_layer)
    
    def _compose_broll_track(self, timeline: TimelinePlan, request: TimelineComposerRequest) -> None:
        """Compose b-roll track."""
        if request.include_broll:
            broll_track = TimelineTrack(
                track_id=f"track_broll_{uuid4().hex}",
                track_type=TimelineTrackType.BROLL,
                muted=True
            )
            
            # Add placeholder b-roll segments
            video_segments = [seg for track in timeline.tracks if track.track_type == TimelineTrackType.VIDEO for seg in track.segments]
            for i, segment in enumerate(video_segments[1:]):  # Skip hook
                if i % 2 == 0:  # Every other segment gets b-roll
                    broll_segment = TimelineSegment(
                        segment_id=f"segment_broll_{i}_{uuid4().hex}",
                        track_type=TimelineTrackType.BROLL,
                        start_time=segment.start_time + 2.0,  # Start 2 seconds into main segment
                        duration=min(3.0, segment.duration - 2.0),
                        content=f"B-roll for {segment.segment_id}"
                    )
                    broll_track.segments.append(broll_segment)
            
            if broll_track.segments:
                timeline.tracks.append(broll_track)
    
    def _generate_render_payload(self, timeline: TimelinePlan, request: Optional[TimelineComposerRequest] = None) -> Dict[str, Any]:
        """Generate render job payload."""
        payload = {
            "job_type": "timeline_render",
            "timeline_id": timeline.timeline_id,
            "aspect_ratio": timeline.aspect_ratio,
            "duration_seconds": timeline.total_duration_seconds,
            "resolution": timeline.render_settings.resolution,
            "style_preset": request.style_preset if request else None,
            "tracks": []
        }
        
        # Convert tracks to render format
        for track in timeline.tracks:
            track_payload = {
                "track_type": track.track_type.value,
                "segments": []
            }
            
            for segment in track.segments:
                segment_payload = {
                    "start_time": segment.start_time,
                    "duration": segment.duration,
                    "content": segment.content
                }
                
                if segment.asset_ref:
                    if segment.asset_ref.asset_id:
                        segment_payload["asset_id"] = segment.asset_ref.asset_id
                    elif segment.asset_ref.source_url:
                        segment_payload["source_url"] = segment.asset_ref.source_url
                
                track_payload["segments"].append(segment_payload)
            
            payload["tracks"].append(track_payload)
        
        # Add caption layer if present
        if timeline.caption_layer:
            payload["caption_layer"] = {
                "style": timeline.caption_layer.style,
                "position": timeline.caption_layer.position,
                "timing": timeline.caption_layer.timing
            }
        
        # Add audio layers if present
        if timeline.audio_layers:
            payload["audio_layers"] = [
                {
                    "track_type": layer.track_type,
                    "volume": layer.volume,
                    "metadata": layer.metadata
                }
                for layer in timeline.audio_layers
            ]
        
        return payload


# Global instance for v0
_timeline_composer_instance = None


def get_timeline_composer() -> TimelineComposer:
    """Get the global timeline composer instance."""
    global _timeline_composer_instance
    if _timeline_composer_instance is None:
        _timeline_composer_instance = TimelineComposer()
    return _timeline_composer_instance
