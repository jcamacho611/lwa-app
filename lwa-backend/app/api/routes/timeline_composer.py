from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.core.auth import get_current_user_optional
from app.services.timeline_composer import (
    TimelineComposer,
    TimelineComposerRequest,
    TimelinePlan,
    TimelineStatus,
    get_timeline_composer,
)


router = APIRouter()


class TimelineComposerRequestModel(BaseModel):
    source_asset_ids: Optional[List[str]] = Field(None, description="Source asset IDs to use")
    clip_ids: Optional[List[str]] = Field(None, description="Clip IDs to use")
    input_urls: Optional[List[str]] = Field(None, description="Direct URLs to use")
    prompt: Optional[str] = Field(None, description="Prompt for timeline generation")
    goal: Optional[str] = Field(None, description="Goal of the video")
    platform: Optional[str] = Field(None, description="Target platform")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio (e.g., 9:16, 16:9)")
    duration_seconds: Optional[float] = Field(None, description="Target duration in seconds")
    style_preset: Optional[str] = Field(None, description="Style preset")
    caption_style: Optional[str] = Field(None, description="Caption style")
    music_style: Optional[str] = Field(None, description="Music style")
    include_cta: bool = Field(False, description="Include call-to-action")
    include_hook: bool = Field(False, description="Include hook segment")
    include_broll: bool = Field(False, description="Include b-roll")
    include_captions: bool = Field(False, description="Include captions")


class TimelineResponse(BaseModel):
    timeline_id: str
    user_id: str
    status: str
    title: str
    strategy_summary: str
    total_duration_seconds: float
    aspect_ratio: str
    render_settings: Dict[str, Any]
    tracks: List[Dict[str, Any]]
    caption_layer: Optional[Dict[str, Any]]
    audio_layers: List[Dict[str, Any]]
    overlay_layers: List[Dict[str, Any]]
    warnings: List[str]
    recommended_render_job_payload: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class TimelineListResponse(BaseModel):
    timelines: List[TimelineResponse]
    total_count: int


class SendToRenderResponse(BaseModel):
    success: bool
    timeline_id: str
    render_job_payload: Optional[Dict[str, Any]]
    message: str
    error: Optional[str] = None


def get_timeline_composer_instance() -> TimelineComposer:
    """Get the timeline composer instance."""
    return get_timeline_composer()


def _timeline_to_response(timeline: TimelinePlan) -> TimelineResponse:
    """Convert TimelinePlan to response model."""
    # Convert tracks to response format
    tracks_response = []
    for track in timeline.tracks:
        track_response = {
            "track_id": track.track_id,
            "track_type": track.track_type.value,
            "segments": [],
            "muted": track.muted,
            "volume": track.volume,
            "metadata": track.metadata
        }
        
        for segment in track.segments:
            segment_response = {
                "segment_id": segment.segment_id,
                "track_type": segment.track_type.value,
                "start_time": segment.start_time,
                "duration": segment.duration,
                "content": segment.content,
                "style": segment.style,
                "metadata": segment.metadata
            }
            
            if segment.asset_ref:
                segment_response["asset_ref"] = {
                    "asset_id": segment.asset_ref.asset_id,
                    "asset_type": segment.asset_ref.asset_type,
                    "source_url": segment.asset_ref.source_url,
                    "start_time": segment.asset_ref.start_time,
                    "end_time": segment.asset_ref.end_time,
                    "duration": segment.asset_ref.duration,
                    "metadata": segment.asset_ref.metadata
                }
                # Remove None values
                segment_response["asset_ref"] = {k: v for k, v in segment_response["asset_ref"].items() if v is not None}
            
            track_response["segments"].append(segment_response)
        
        tracks_response.append(track_response)
    
    # Convert caption layer
    caption_layer_response = None
    if timeline.caption_layer:
        caption_layer_response = {
            "style": timeline.caption_layer.style,
            "position": timeline.caption_layer.position,
            "font_size": timeline.caption_layer.font_size,
            "color": timeline.caption_layer.color,
            "background": timeline.caption_layer.background,
            "timing": timeline.caption_layer.timing
        }
    
    # Convert audio layers
    audio_layers_response = []
    for layer in timeline.audio_layers:
        audio_layer_response = {
            "track_type": layer.track_type,
            "volume": layer.volume,
            "fade_in": layer.fade_in,
            "fade_out": layer.fade_out,
            "ducking": layer.ducking,
            "metadata": layer.metadata
        }
        # Remove None values
        audio_layer_response = {k: v for k, v in audio_layer_response.items() if v is not None}
        audio_layers_response.append(audio_layer_response)
    
    # Convert overlay layers
    overlay_layers_response = []
    for layer in timeline.overlay_layers:
        overlay_layer_response = {
            "overlay_type": layer.overlay_type,
            "position": layer.position,
            "opacity": layer.opacity,
            "duration": layer.duration,
            "content": layer.content,
            "metadata": layer.metadata
        }
        # Remove None values
        overlay_layer_response = {k: v for k, v in overlay_layer_response.items() if v is not None}
        overlay_layers_response.append(overlay_layer_response)
    
    # Convert render settings
    render_settings_response = {
        "aspect_ratio": timeline.render_settings.aspect_ratio,
        "resolution": timeline.render_settings.resolution,
        "frame_rate": timeline.render_settings.frame_rate,
        "quality": timeline.render_settings.quality,
        "format": timeline.render_settings.format,
        "metadata": timeline.render_settings.metadata
    }
    # Remove None values
    render_settings_response = {k: v for k, v in render_settings_response.items() if v is not None}
    
    return TimelineResponse(
        timeline_id=timeline.timeline_id,
        user_id=timeline.user_id,
        status=timeline.status.value,
        title=timeline.title,
        strategy_summary=timeline.strategy_summary,
        total_duration_seconds=timeline.total_duration_seconds,
        aspect_ratio=timeline.aspect_ratio,
        render_settings=render_settings_response,
        tracks=tracks_response,
        caption_layer=caption_layer_response,
        audio_layers=audio_layers_response,
        overlay_layers=overlay_layers_response,
        warnings=timeline.warnings,
        recommended_render_job_payload=timeline.recommended_render_job_payload,
        created_at=timeline.created_at,
        updated_at=timeline.updated_at
    )


@router.post("/timeline-composer/compose", response_model=TimelineResponse)
async def compose_timeline(
    request: TimelineComposerRequestModel,
    current_user: dict = Depends(get_current_user_optional),
):
    """Compose a new timeline plan."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Create composer request
    composer_request = TimelineComposerRequest(
        source_asset_ids=request.source_asset_ids,
        clip_ids=request.clip_ids,
        input_urls=request.input_urls,
        prompt=request.prompt,
        goal=request.goal,
        platform=request.platform,
        aspect_ratio=request.aspect_ratio,
        duration_seconds=request.duration_seconds,
        style_preset=request.style_preset,
        caption_style=request.caption_style,
        music_style=request.music_style,
        include_cta=request.include_cta,
        include_hook=request.include_hook,
        include_broll=request.include_broll,
        include_captions=request.include_captions,
    )
    
    # Compose timeline
    composer = get_timeline_composer_instance()
    timeline = composer.compose_timeline(composer_request, user_id)
    
    return _timeline_to_response(timeline)


@router.get("/timeline-composer/{timeline_id}", response_model=TimelineResponse)
async def get_timeline(
    timeline_id: str,
    current_user: dict = Depends(get_current_user_optional),
):
    """Get a specific timeline plan."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    composer = get_timeline_composer_instance()
    timeline = composer.get_timeline(timeline_id)
    
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")
    
    # In production, verify user owns this timeline. For v0, skip strict user checking
    
    return _timeline_to_response(timeline)


@router.get("/timeline-composer", response_model=TimelineListResponse)
async def list_timelines(
    current_user: dict = Depends(get_current_user_optional),
):
    """List timeline plans for the current user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    composer = get_timeline_composer_instance()
    timelines = composer.list_timelines(user_id)
    
    timeline_responses = [_timeline_to_response(timeline) for timeline in timelines]
    
    return TimelineListResponse(
        timelines=timeline_responses,
        total_count=len(timeline_responses)
    )


@router.post("/timeline-composer/{timeline_id}/send-to-render", response_model=SendToRenderResponse)
async def send_timeline_to_render(
    timeline_id: str,
    current_user: dict = Depends(get_current_user_optional),
):
    """Send a timeline to the render engine."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    composer = get_timeline_composer_instance()
    
    # Verify timeline exists
    timeline = composer.get_timeline(timeline_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")
    
    # In production, verify user owns this timeline. For v0, skip strict user checking
    
    # Send to render
    result = composer.send_to_render(timeline_id)
    
    if "error" in result:
        return SendToRenderResponse(
            success=False,
            timeline_id=timeline_id,
            render_job_payload=None,
            message=result.get("message", "Failed to send to render"),
            error=result.get("error")
        )
    
    return SendToRenderResponse(
        success=True,
        timeline_id=timeline_id,
        render_job_payload=result.get("render_job_payload"),
        message=result.get("message", "Timeline sent to render engine")
    )


@router.delete("/timeline-composer/{timeline_id}")
async def delete_timeline(
    timeline_id: str,
    current_user: dict = Depends(get_current_user_optional),
):
    """Delete a timeline plan."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    composer = get_timeline_composer_instance()
    
    # Verify timeline exists
    timeline = composer.get_timeline(timeline_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")
    
    # In production, verify user owns this timeline. For v0, skip strict user checking
    
    deleted = composer.delete_timeline(timeline_id)
    
    if deleted:
        return {"message": "Timeline deleted successfully", "timeline_id": timeline_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete timeline")


@router.get("/timeline-composer/capabilities")
async def get_timeline_composer_capabilities(
    current_user: dict = Depends(get_current_user_optional),
):
    """Get timeline composer capabilities and options."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "track_types": [track_type.value for track_type in [
            "video", "broll", "audio", "captions", "overlays", "voiceover", "music"
        ]],
        "aspect_ratios": ["9:16", "16:9", "1:1", "4:5"],
        "platforms": ["tiktok", "instagram", "youtube", "youtube_shorts", "linkedin", "twitter"],
        "style_presets": ["minimal", "professional", "casual", "energetic", "dramatic", "educational"],
        "caption_styles": ["default", "bold", "clean", "minimal", "colorful", "professional"],
        "music_styles": ["upbeat", "corporate", "dramatic", "inspirational", "tech", "ambient"],
        "max_duration_seconds": 300,  # 5 minutes max
        "default_duration_seconds": 30,
        "default_aspect_ratio": "9:16",
        "features": {
            "hook_segments": True,
            "cta_segments": True,
            "broll_tracks": True,
            "caption_layers": True,
            "audio_layers": True,
            "overlay_layers": True,
            "render_integration": True
        }
    }
