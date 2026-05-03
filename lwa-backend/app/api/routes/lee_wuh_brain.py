"""
Lee-Wuh Brain API Routes

Provides endpoints for Lee-Wuh AI Brain guidance,
council summaries, and next-best-actions.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...services.lee_wuh_brain import lee_wuh_brain, CouncilInput, AppScreen, LeeWuhVisualState

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/v1/lee-wuh", tags=["lee-wuh-brain"])


class CouncilInputRequest(BaseModel):
    """Request model for council input."""
    
    app_state: str = Field(default="idle", description="Current application state")
    current_screen: str = Field(default="homepage", description="Current screen")
    source_asset_ids: list[str] = Field(default_factory=list, description="Source asset IDs")
    timeline_id: Optional[str] = Field(default=None, description="Timeline ID")
    render_job_id: Optional[str] = Field(default=None, description="Render job ID")
    clip_id: Optional[str] = Field(default=None, description="Clip ID")
    user_goal: Optional[str] = Field(default=None, description="User's current goal")
    platform: Optional[str] = Field(default=None, description="Target platform")
    warnings: list[str] = Field(default_factory=list, description="Current warnings")
    engine_statuses: dict[str, str] = Field(default_factory=dict, description="Engine statuses")
    user_id: Optional[str] = Field(default=None, description="User ID")
    has_credits: bool = Field(default=True, description="Whether user has credits")
    has_sources: bool = Field(default=False, description="Whether user has sources")
    has_clips: bool = Field(default=False, description="Whether user has clips")
    has_timeline: bool = Field(default=False, description="Whether user has timeline")


class CouncilOutputResponse(BaseModel):
    """Response model for council output."""
    
    mascot_message: str = Field(description="Lee-Wuh mascot message")
    council_summary: str = Field(description="Council summary")
    next_best_action: str = Field(description="Recommended next action")
    recommended_engine: Optional[str] = Field(default=None, description="Recommended engine")
    warnings: list[str] = Field(default_factory=list, description="Warnings")
    confidence: int = Field(default=80, description="Confidence score (0-100)")
    visual_state: str = Field(description="Lee-Wuh visual state")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


@router.post("/guidance", response_model=CouncilOutputResponse)
async def get_council_guidance(request: CouncilInputRequest) -> CouncilOutputResponse:
    """
    Get Lee-Wuh AI Brain guidance.
    
    Processes current app state and provides mascot message,
    council summary, and next-best-action recommendations.
    """
    
    try:
        # Convert screen string to enum
        try:
            screen_enum = AppScreen(request.current_screen.lower())
        except ValueError:
            screen_enum = AppScreen.HOMEPAGE
            logger.warning(f"invalid_screen requested={request.current_screen} defaulting=homepage")
        
        # Build council input
        council_input = CouncilInput(
            app_state=request.app_state,
            current_screen=screen_enum,
            source_asset_ids=request.source_asset_ids,
            timeline_id=request.timeline_id,
            render_job_id=request.render_job_id,
            clip_id=request.clip_id,
            user_goal=request.user_goal,
            platform=request.platform,
            warnings=request.warnings,
            engine_statuses=request.engine_statuses,
            user_id=request.user_id,
            has_credits=request.has_credits,
            has_sources=request.has_sources,
            has_clips=request.has_clips,
            has_timeline=request.has_timeline,
        )
        
        # Process through Lee-Wuh brain
        council_output = await lee_wuh_brain.process(council_input)
        
        return CouncilOutputResponse(
            mascot_message=council_output.mascot_message,
            council_summary=council_output.council_summary,
            next_best_action=council_output.next_best_action,
            recommended_engine=council_output.recommended_engine,
            warnings=council_output.warnings,
            confidence=council_output.confidence,
            visual_state=council_output.visual_state.value,
            metadata=council_output.metadata,
        )
        
    except Exception as error:
        logger.error(f"council_guidance_failed error={str(error)}")
        raise HTTPException(status_code=500, detail="Council guidance processing failed")


@router.get("/health")
async def brain_health() -> dict[str, str]:
    """Health check for Lee-Wuh brain service."""
    
    return {
        "status": "ok",
        "service": "lee-wuh-brain",
        "visual_states": [state.value for state in LeeWuhVisualState],
        "screens": [screen.value for screen in AppScreen],
    }


@router.get("/dialogue-states")
async def get_dialogue_states() -> dict[str, list[str]]:
    """Get available dialogue states for Lee-Wuh."""
    
    return {
        "greeting": [
            "Welcome to LWA. I'm Lee-Wuh, your creative guide.",
            "Ready to create something powerful?",
            "Let's turn your content into impact.",
        ],
        "success": [
            "Excellent work. This one's ready to shine.",
            "Boss-level clip detected. Post this first.",
            "This one builds trust. Save it as proof.",
            "This one sells. Package it for conversion.",
        ],
        "thinking": [
            "I'm analyzing your source for breakout moments.",
            "Scanning hooks, proof, silence, and energy.",
            "The council is reviewing your content.",
        ],
        "warning": [
            "I see a potential issue. Let's address it together.",
            "This needs attention before proceeding.",
            "Mock mode is training ground. Real render comes next.",
        ],
        "error": [
            "Something went wrong. I'm working on a fix.",
            "Let me recalibrate. Give me a moment.",
            "The council is troubleshooting this issue.",
        ],
        "rendering": [
            "Render in progress. I'm monitoring quality and timing.",
            "Quality is my priority. This may take a moment.",
            "The forge is working on your content.",
        ],
    }
