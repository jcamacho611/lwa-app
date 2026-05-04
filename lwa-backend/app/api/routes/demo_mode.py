"""Demo Mode API routes for LWA.

Provides endpoints for new users to try the platform
with sample content without needing their own video.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...services.demo_mode_service import (
    get_demo_source,
    get_demo_clips,
    create_demo_campaign_pack,
    save_demo_proof,
    get_demo_mode_status,
)

router = APIRouter(prefix="/api/v1/demo", tags=["demo_mode"])


class DemoSourceResponse(BaseModel):
    success: bool
    source: dict
    message: str


class DemoClipsResponse(BaseModel):
    success: bool
    clips: list[dict]
    count: int
    source_id: str
    is_demo: bool
    message: str


class DemoCampaignResponse(BaseModel):
    success: bool
    campaign: dict
    message: str


class DemoSaveProofResponse(BaseModel):
    success: bool
    user_id: str
    saved_assets: list[dict]
    count: int
    message: str


class DemoStatusResponse(BaseModel):
    success: bool
    demo_mode_enabled: bool
    sample_source_available: bool
    sample_clips_count: int
    features: list[str]
    limitations: list[str]


@router.get("/source", response_model=DemoSourceResponse)
async def api_get_demo_source():
    """Get the sample demo source for new users."""
    try:
        result = get_demo_source()
        return DemoSourceResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Demo source failed: {exc}")


@router.get("/clips", response_model=DemoClipsResponse)
async def api_get_demo_clips():
    """Get sample clips for the demo source."""
    try:
        result = get_demo_clips()
        return DemoClipsResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Demo clips failed: {exc}")


@router.get("/campaign", response_model=DemoCampaignResponse)
async def api_create_demo_campaign():
    """Create a full demo campaign pack ready for export."""
    try:
        result = create_demo_campaign_pack()
        return DemoCampaignResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Demo campaign failed: {exc}")


@router.post("/save-proof", response_model=DemoSaveProofResponse)
async def api_save_demo_proof():
    """Save demo clips to Proof Vault."""
    try:
        # Mock user ID - replace with auth
        user_id = "user_demo_001"
        result = save_demo_proof(user_id)
        return DemoSaveProofResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Save demo proof failed: {exc}")


@router.get("/status", response_model=DemoStatusResponse)
async def api_get_demo_status():
    """Get Demo Mode system status."""
    try:
        result = get_demo_mode_status()
        return DemoStatusResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Demo status failed: {exc}")
