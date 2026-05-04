"""Command Center summary API for LWA.

Provides aggregated overview data for the Command Center dashboard.
"""

from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ...dependencies.auth import get_platform_store, require_user
from ...core.config import get_settings

router = APIRouter(prefix="/api/v1/command-center", tags=["command_center"])
platform_store = get_platform_store()
settings = get_settings()


class WorldProfileSummary(BaseModel):
    display_name: str = "Creator"
    class_name: str = "Clip strategist"
    faction: str = "Independent"
    level: int = 1
    xp: int = 0
    next_level_xp: int = 100
    badges: List[str] = Field(default_factory=list)
    relics: List[str] = Field(default_factory=list)


class CampaignSummary(BaseModel):
    total_count: int
    open_count: int
    review_ready_count: int


class EarningsSummary(BaseModel):
    approved_cents: int
    pending_review_cents: int
    available_cents: int
    eligible_payout_cents: int


class CommandCenterSummaryResponse(BaseModel):
    success: bool
    world: WorldProfileSummary
    campaigns: CampaignSummary
    earnings: EarningsSummary
    generated_at: str


@router.get("/summary", response_model=CommandCenterSummaryResponse)
async def get_command_center_summary(request: Request):
    """Get aggregated summary data for Command Center overview."""
    try:
        user = require_user(request)
        
        # Get wallet data
        wallet = platform_store.get_wallet(user_id=user.id)
        submission_summary = platform_store.get_user_submission_summary(user_id=user.id)
        
        # Get campaigns
        campaigns_list = platform_store.list_campaigns(user_id=user.id)
        
        # Calculate campaign stats
        total_campaigns = len(campaigns_list)
        open_campaigns = sum(1 for c in campaigns_list if c.get("status") == "open")
        review_ready = sum(1 for c in campaigns_list if c.get("status") == "review_ready")
        
        # Calculate earnings
        credits = [entry["amount_cents"] for entry in wallet["transactions"] if entry["amount_cents"] > 0]
        pending_payouts = sum(payout["amount_cents"] for payout in wallet["payouts"] if payout["status"] == "pending")
        
        # Build world profile (could be enhanced with real XP/level system)
        # For now, derive from user activity
        total_clips = len(platform_store.list_clip_packs(user_id=user.id))
        level = min(10, 1 + total_clips // 5)  # Simple leveling formula
        xp = total_clips * 10
        next_level_xp = level * 100
        
        badges = []
        if total_clips > 0:
            badges.append("first_clip")
        if total_campaigns > 0:
            badges.append("campaign_creator")
        if submission_summary["eligible_payout_cents"] > 0:
            badges.append("earner")
        if total_clips >= 10:
            badges.append("clip_master")
            
        return CommandCenterSummaryResponse(
            success=True,
            world=WorldProfileSummary(
                display_name=user.email.split("@")[0] if user.email else "Creator",
                class_name="Clip strategist",
                faction="Independent",
                level=level,
                xp=xp,
                next_level_xp=next_level_xp,
                badges=badges,
                relics=[],
            ),
            campaigns=CampaignSummary(
                total_count=total_campaigns,
                open_count=open_campaigns,
                review_ready_count=review_ready,
            ),
            earnings=EarningsSummary(
                approved_cents=submission_summary["eligible_payout_cents"],
                pending_review_cents=pending_payouts,
                available_cents=max(wallet["balance_cents"], 0),
                eligible_payout_cents=submission_summary["eligible_payout_cents"],
            ),
            generated_at=datetime.utcnow().isoformat(),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load command center summary: {exc}"
        ) from exc
