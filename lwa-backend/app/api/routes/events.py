"""Event tracking API routes for LWA.

Provides endpoints for tracking user interactions, clip engagement,
and system events for analytics and ML training.
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ...services.event_log import emit_event
from ...core.config import get_settings

router = APIRouter(prefix="/api/v1/events", tags=["events"])

EventType = Literal[
    "clip_view",
    "clip_play",
    "clip_save",
    "clip_share",
    "clip_export",
    "clip_vote_good",
    "clip_vote_bad",
    "clip_queue",
    "clip_recover",
    "hook_copy",
    "caption_copy",
    "cta_copy",
    "package_copy",
    "proof_save",
    "style_feedback",
    "generate_start",
    "generate_complete",
    "generate_error",
    "page_view",
    "feature_click",
    "error",
]

EventSource = Literal["web", "api", "ios", "extension", "widget"]


class TrackEventRequest(BaseModel):
    event_type: EventType
    clip_id: Optional[str] = None
    source_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: EventSource = "web"
    session_id: Optional[str] = None


class TrackEventResponse(BaseModel):
    success: bool
    event_id: str
    message: str


class BatchTrackRequest(BaseModel):
    events: list[TrackEventRequest] = Field(..., min_length=1, max_length=100)


class BatchTrackResponse(BaseModel):
    success: bool
    tracked_count: int
    failed_count: int
    event_ids: list[str]


class EventStatusResponse(BaseModel):
    success: bool
    event_tracking_enabled: bool
    supported_event_types: list[str]
    supported_sources: list[str]


def _create_event_payload(
    request: TrackEventRequest,
    request_id: str | None = None,
    ip_hash: str | None = None,
) -> Dict[str, Any]:
    """Create standardized event payload."""
    return {
        "event_id": f"evt_{uuid4().hex[:16]}",
        "event_type": request.event_type,
        "clip_id": request.clip_id,
        "source_id": request.source_id,
        "source": request.source,
        "session_id": request.session_id,
        "request_id": request_id,
        "ip_hash": ip_hash,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metadata": request.metadata,
    }


@router.post("/track", response_model=TrackEventResponse)
async def track_event(
    request: TrackEventRequest,
    http_request: Request,
):
    """Track a single user or system event."""
    try:
        settings = get_settings()
        
        # Create IP hash for privacy-safe tracking
        client_ip = http_request.client.host if http_request.client else None
        ip_hash = None
        if client_ip:
            import hashlib
            ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
        
        # Generate request ID
        request_id = f"req_{uuid4().hex[:12]}"
        
        # Create event payload
        payload = _create_event_payload(request, request_id, ip_hash)
        
        # Emit to event log
        emit_event(
            settings=settings,
            event=f"user_event:{request.event_type}",
            request_id=request_id,
            metadata=payload,
        )
        
        return TrackEventResponse(
            success=True,
            event_id=payload["event_id"],
            message="Event tracked successfully",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track event: {exc}"
        ) from exc


@router.post("/batch", response_model=BatchTrackResponse)
async def track_batch_events(
    request: BatchTrackRequest,
    http_request: Request,
):
    """Track multiple events in a single batch request."""
    try:
        settings = get_settings()
        
        # Create IP hash for privacy-safe tracking
        client_ip = http_request.client.host if http_request.client else None
        ip_hash = None
        if client_ip:
            import hashlib
            ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
        
        event_ids = []
        failed = 0
        
        for event in request.events:
            try:
                request_id = f"req_{uuid4().hex[:12]}"
                payload = _create_event_payload(event, request_id, ip_hash)
                
                emit_event(
                    settings=settings,
                    event=f"user_event:{event.event_type}",
                    request_id=request_id,
                    metadata=payload,
                )
                
                event_ids.append(payload["event_id"])
            except Exception:
                failed += 1
        
        return BatchTrackResponse(
            success=True,
            tracked_count=len(event_ids),
            failed_count=failed,
            event_ids=event_ids,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track batch events: {exc}"
        ) from exc


@router.get("/status", response_model=EventStatusResponse)
async def get_event_tracking_status():
    """Get event tracking system status."""
    return EventStatusResponse(
        success=True,
        event_tracking_enabled=True,
        supported_event_types=list(EventType.__args__),
        supported_sources=list(EventSource.__args__),
    )
