"""Admin/Operator API routes for LWA.

Provides endpoints for operator observability, system status,
event analytics, and admin-level operations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...services.event_log import get_recent_events, get_system_metrics
from ...core.config import get_settings

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class RecentEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: str
    clip_id: Optional[str] = None
    source_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecentEventsResponse(BaseModel):
    success: bool
    events: List[RecentEvent]
    count: int
    time_range_minutes: int


class SystemMetric(BaseModel):
    metric_name: str
    value: float
    unit: str
    timestamp: str


class SystemMetricsResponse(BaseModel):
    success: bool
    metrics: List[SystemMetric]
    generated_at: str


class OperatorStatusResponse(BaseModel):
    success: bool
    system_healthy: bool
    event_tracking_enabled: bool
    recent_event_count: int
    api_status: str
    last_error: Optional[str] = None
    checked_at: str


@router.get("/events/recent", response_model=RecentEventsResponse)
async def get_recent_lwa_events(
    minutes: int = Query(default=60, ge=1, le=1440),
    event_type: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
):
    """Get recent events for operator observability.
    
    Args:
        minutes: Time range in minutes (1-1440)
        event_type: Filter by specific event type
        limit: Maximum events to return (1-1000)
    """
    try:
        settings = get_settings()
        events = get_recent_events(
            settings=settings,
            minutes=minutes,
            event_type=event_type,
            limit=limit,
        )
        
        return RecentEventsResponse(
            success=True,
            events=[
                RecentEvent(
                    event_id=e.get("event_id", f"evt_{uuid4().hex[:12]}"),
                    event_type=e.get("event_type", "unknown"),
                    timestamp=e.get("timestamp", datetime.utcnow().isoformat()),
                    clip_id=e.get("clip_id"),
                    source_id=e.get("source_id"),
                    user_id=e.get("user_id"),
                    metadata=e.get("metadata", {}),
                )
                for e in events
            ],
            count=len(events),
            time_range_minutes=minutes,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recent events: {exc}"
        ) from exc


@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_admin_metrics():
    """Get system metrics for operator dashboard."""
    try:
        settings = get_settings()
        metrics = get_system_metrics(settings=settings)
        
        return SystemMetricsResponse(
            success=True,
            metrics=[
                SystemMetric(
                    metric_name=m["name"],
                    value=m["value"],
                    unit=m.get("unit", "count"),
                    timestamp=m.get("timestamp", datetime.utcnow().isoformat()),
                )
                for m in metrics
            ],
            generated_at=datetime.utcnow().isoformat(),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch system metrics: {exc}"
        ) from exc


@router.get("/status", response_model=OperatorStatusResponse)
async def get_admin_ops_status():
    """Get overall operator status for system health check."""
    try:
        settings = get_settings()
        
        # Check recent events count
        recent = get_recent_events(settings=settings, minutes=5, limit=1)
        recent_count = len(get_recent_events(settings=settings, minutes=60, limit=1000))
        
        # Determine system health
        healthy = recent_count >= 0  # Any response means system is up
        
        return OperatorStatusResponse(
            success=True,
            system_healthy=healthy,
            event_tracking_enabled=True,
            recent_event_count=recent_count,
            api_status="operational",
            last_error=None,
            checked_at=datetime.utcnow().isoformat(),
        )
    except Exception as exc:
        return OperatorStatusResponse(
            success=True,  # Endpoint responded
            system_healthy=False,
            event_tracking_enabled=False,
            recent_event_count=0,
            api_status="degraded",
            last_error=str(exc),
            checked_at=datetime.utcnow().isoformat(),
        )
