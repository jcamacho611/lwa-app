"""Clips listing API for LWA.

Provides endpoints for listing and filtering clips for batch review.
"""

from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, Field

from ...dependencies.auth import get_platform_store, require_user

router = APIRouter(prefix="/api/v1", tags=["clips"])
platform_store = get_platform_store()


class ClipItem(BaseModel):
    clip_id: str
    hook: str
    caption: str
    duration: int
    ai_score: float
    status: str
    platform: str
    source_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: str
    updated_at: str


class ClipListResponse(BaseModel):
    success: bool
    clips: List[ClipItem]
    count: int
    total_count: int


@router.get("/clips", response_model=ClipListResponse)
async def list_clips(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected, edited"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List clips for batch review with optional filtering."""
    try:
        user = require_user(request)
        
        # Get all clip packs for the user
        clip_packs = platform_store.list_clip_packs(user_id=user.id)
        
        # Extract all clips from all packs
        all_clips: List[dict] = []
        for pack in clip_packs:
            pack_clips = pack.get("clips", [])
            for clip in pack_clips:
                clip_data = {
                    "clip_id": clip.get("clip_id", clip.get("id", "")),
                    "hook": clip.get("hook", clip.get("title", "Untitled")),
                    "caption": clip.get("caption", clip.get("description", "")),
                    "duration": clip.get("duration_seconds", clip.get("duration", 15)),
                    "ai_score": clip.get("score", clip.get("ai_score", 0.5)),
                    "status": clip.get("status", "pending"),
                    "platform": clip.get("platform", "tiktok"),
                    "source_url": clip.get("source_url"),
                    "thumbnail_url": clip.get("thumbnail_url"),
                    "created_at": clip.get("created_at", datetime.utcnow().isoformat()),
                    "updated_at": clip.get("updated_at", datetime.utcnow().isoformat()),
                }
                all_clips.append(clip_data)
        
        # Apply filters
        filtered_clips = all_clips
        if status:
            filtered_clips = [c for c in filtered_clips if c["status"] == status]
        if platform:
            filtered_clips = [c for c in filtered_clips if c["platform"] == platform]
        
        # Apply pagination
        total_count = len(filtered_clips)
        paginated_clips = filtered_clips[offset : offset + limit]
        
        return ClipListResponse(
            success=True,
            clips=[ClipItem(**clip) for clip in paginated_clips],
            count=len(paginated_clips),
            total_count=total_count,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list clips: {exc}"
        ) from exc
