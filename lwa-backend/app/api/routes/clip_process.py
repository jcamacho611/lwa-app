"""
Clip Processing API Routes
MVP endpoints for ingest, process, variant generation, and export.
"""
from __future__ import annotations

import uuid
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl

from ...worlds.models import (
    Clip,
    ClipPack,
    GenerateRequest,
    GenerateResponse,
    VariantRequest,
    VariantResponse,
    ProcessingStatus,
    ExportRequest,
    ExportResponse,
    Segment,
)
from ...offline_engine import process_video_offline
from ...ai_engine import analyze_clip, rank_clips, AIClipAnalysis
from ...variant_engine import generate_strategy_pack

router = APIRouter(tags=["clip-processing"])

# In-memory store for MVP (replace with Redis/DB in production)
processing_store: Dict[str, Dict] = {}
clip_store: Dict[str, List[Clip]] = {}


class IngestRequest(BaseModel):
    source_url: str
    description: Optional[str] = None


class IngestResponse(BaseModel):
    request_id: str
    status: str
    message: str


@router.post("/ingest", response_model=IngestResponse)
async def ingest_video(request: IngestRequest) -> IngestResponse:
    """
    Ingest a video source URL for processing.
    Returns a request_id to track processing status.
    """
    request_id = str(uuid.uuid4())[:8]
    
    processing_store[request_id] = {
        "source_url": request.source_url,
        "description": request.description,
        "status": "ingesting",
        "progress": 0,
        "clips": [],
    }
    
    return IngestResponse(
        request_id=request_id,
        status="queued",
        message="Video ingestion queued. Use /status/{request_id} to track progress."
    )


@router.get("/status/{request_id}", response_model=ProcessingStatus)
async def get_processing_status(request_id: str) -> ProcessingStatus:
    """
    Get current processing status for a request.
    """
    if request_id not in processing_store:
        raise HTTPException(status_code=404, detail="Request not found")
    
    data = processing_store[request_id]
    clips = clip_store.get(request_id, [])
    
    return ProcessingStatus(
        request_id=request_id,
        stage=data.get("status", "unknown"),
        progress=data.get("progress", 0),
        clips_ready=len(clips),
        total_clips=data.get("total_clips", 0),
    )


@router.post("/process/{request_id}", response_model=GenerateResponse)
async def process_video(
    request_id: str,
    background_tasks: BackgroundTasks,
    use_ai: bool = False,
) -> GenerateResponse:
    """
    Start processing a video that has been ingested.
    If use_ai=True and user has credits, AI analysis will be applied.
    """
    if request_id not in processing_store:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Update status
    processing_store[request_id]["status"] = "cutting"
    processing_store[request_id]["progress"] = 25
    
    # Mock processing for MVP
    # In production, this would trigger Celery tasks
    
    # Generate mock clips
    mock_segments = [
        Segment(start=0.0, end=15.0, type="kept"),
        Segment(start=15.0, end=30.0, type="suggested"),
        Segment(start=30.0, end=45.0, type="kept"),
    ]
    
    clips: List[Clip] = []
    for i in range(3):
        clip_id = f"{request_id}-clip-{i+1:03d}"
        
        # AI analysis if requested (mock for MVP)
        ai_data: Optional[AIClipAnalysis] = None
        if use_ai:
            ai_data = analyze_clip(clip_id, "", 15.0, {})
        
        clip = Clip(
            clip_id=clip_id,
            preview_url=None,  # Strategy-only for MVP
            segments=mock_segments,
            hook=ai_data.hook if ai_data else f"Clip {i+1} hook text",
            caption=ai_data.caption if ai_data else f"Caption for clip {i+1}",
            cta=ai_data.cta if ai_data else "Follow for more",
            virality_score=ai_data.virality_score if ai_data else 50.0 + (i * 10),
            thumbnail_text=ai_data.thumbnail_text if ai_data else "Thumbnail text",
            platform_tags=ai_data.platform_tags if ai_data else ["tiktok", "reels"],
            render_status="strategy_only",
        )
        clips.append(clip)
    
    # Rank clips if AI was used
    if use_ai:
        clips = sorted(clips, key=lambda c: c.virality_score, reverse=True)
    
    clip_store[request_id] = clips
    processing_store[request_id]["status"] = "complete"
    processing_store[request_id]["progress"] = 100
    processing_store[request_id]["total_clips"] = len(clips)
    
    return GenerateResponse(
        request_id=request_id,
        status="complete",
        clips=clips,
        strategy_only=not use_ai,
    )


@router.get("/clips/{request_id}", response_model=List[Clip])
async def get_clips(request_id: str) -> List[Clip]:
    """
    Get all clips for a request.
    """
    if request_id not in clip_store:
        raise HTTPException(status_code=404, detail="No clips found for this request")
    
    return clip_store[request_id]


@router.post("/variants/{request_id}", response_model=VariantResponse)
async def generate_variants(
    request_id: str,
    request: VariantRequest,
) -> VariantResponse:
    """
    Generate variant clip packs for a request.
    """
    if request_id not in clip_store:
        raise HTTPException(status_code=404, detail="No clips found for this request")
    
    base_clips = clip_store[request_id]
    clip_ids = [c.clip_id for c in base_clips]
    
    # Generate strategy pack
    strategy_pack = generate_strategy_pack(clip_ids, request_id, user_goal="engagement")
    
    # Convert to ClipPack format (mock for MVP)
    variants: List[ClipPack] = []
    for i in range(min(request.count, 3)):
        pack = ClipPack(
            pack_id=f"{request_id}-pack-{i+1:03d}",
            request_id=request_id,
            clips=base_clips,
            best_clip_id=base_clips[0].clip_id if base_clips else None,
            total_duration=45.0,
            created_at="2026-05-05",
        )
        variants.append(pack)
    
    return VariantResponse(variants=variants)


@router.post("/export/{request_id}", response_model=ExportResponse)
async def export_clips(
    request_id: str,
    request: ExportRequest,
) -> ExportResponse:
    """
    Export clips in specified format.
    """
    if request_id not in clip_store:
        raise HTTPException(status_code=404, detail="No clips found for this request")
    
    clips = clip_store[request_id]
    
    # Generate markdown export
    if request.format == "markdown":
        md_content = f"# Clip Pack Export\\n\\nRequest: {request_id}\\nPack: {request.pack_id}\\n\\n"
        for clip in clips:
            md_content += f"## {clip.clip_id}\\n\\n"
            md_content += f"**Hook:** {clip.hook}\\n\\n"
            md_content += f"**Caption:** {clip.caption}\\n\\n"
            md_content += f"**CTA:** {clip.cta}\\n\\n"
            md_content += f"**Score:** {clip.virality_score}\\n\\n"
            md_content += f"**Tags:** {', '.join(clip.platform_tags)}\\n\\n"
            md_content += "---\\n\\n"
        
        return ExportResponse(
            download_url=None,
            markdown_content=md_content,
        )
    
    # JSON export handled by API response structure
    elif request.format == "json":
        return ExportResponse(
            download_url=f"/api/download/json?request_id={request_id}&pack_id={request.pack_id}",
            markdown_content=None,
        )
    
    # Plain text export
    else:
        txt_content = f"CLIP PACK: {request.pack_id}\\n\\n"
        for clip in clips:
            txt_content += f"CLIP: {clip.clip_id}\\n"
            txt_content += f"Hook: {clip.hook}\\n"
            txt_content += f"Caption: {clip.caption}\\n"
            txt_content += f"CTA: {clip.cta}\\n\\n"
        
        return ExportResponse(
            download_url=None,
            markdown_content=txt_content,
        )
