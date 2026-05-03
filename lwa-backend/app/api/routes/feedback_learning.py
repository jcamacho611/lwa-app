"""
Feedback Learning API Routes

Provides endpoints for feedback learning functionality:
- Insight generation
- Learning metrics
- Feedback submission
- Performance analytics
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from ...services.feedback_learning_engine import feedback_learning_engine

router = APIRouter(prefix="/v1/feedback-learning", tags=["feedback-learning"])

# Request/Response Models
class FeedbackEventRequest(BaseModel):
    clip_id: str
    event_type: str
    platform: str
    metrics: Dict[str, float]
    user_feedback: Optional[str] = None

class InsightRequest(BaseModel):
    campaign_id: Optional[str] = None
    insight_types: List[str] = []
    time_range_days: int = 7

# Feedback Events
@router.post("/events")
async def submit_feedback_event(request: FeedbackEventRequest) -> Dict[str, Any]:
    """Submit a feedback learning event."""
    try:
        # Mock feedback event submission
        event_id = f"event_{hash(request.clip_id + request.event_type)}"
        
        return {
            "success": True,
            "event_id": event_id,
            "processed": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_feedback_events(limit: int = 100, offset: int = 0, clip_id: Optional[str] = None) -> Dict[str, Any]:
    """Get feedback events."""
    try:
        # Mock feedback event data
        events = [
            {
                "id": "event_1",
                "clip_id": "clip_1",
                "event_type": "view",
                "platform": "tiktok",
                "metrics": {
                    "views": 15420,
                    "likes": 892,
                    "shares": 234,
                    "comments": 89,
                    "engagement_rate": 0.078
                },
                "created_at": "2026-05-03T12:00:00Z"
            },
            {
                "id": "event_2",
                "clip_id": "clip_1",
                "event_type": "completion",
                "platform": "tiktok",
                "metrics": {
                    "watch_time": 15.2,
                    "completion_rate": 0.85,
                    "rewatch_count": 23
                },
                "created_at": "2026-05-03T12:15:00Z"
            }
        ]
        
        return {
            "success": True,
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Insights
@router.get("/insights")
async def get_insights(limit: int = 50, offset: int = 0, campaign_id: Optional[str] = None) -> Dict[str, Any]:
    """Get feedback learning insights."""
    try:
        # Mock insight data
        insights = [
            {
                "id": "insight_1",
                "campaign_id": "campaign_1",
                "insight_type": "performance",
                "title": "High Engagement on Gaming Clips",
                "description": "Gaming content showing 45% higher engagement than average",
                "confidence_score": 0.92,
                "impact_level": "high",
                "created_at": "2026-05-03T10:00:00Z",
                "applied": False,
                "recommendations": [
                    "Increase gaming content production",
                    "Focus on TikTok gaming niche",
                    "Use similar editing patterns"
                ]
            },
            {
                "id": "insight_2",
                "campaign_id": "campaign_1",
                "insight_type": "timing",
                "title": "Optimal Posting Time Identified",
                "description": "Best posting time is 7-9 PM for target audience",
                "confidence_score": 0.87,
                "impact_level": "medium",
                "created_at": "2026-05-03T09:30:00Z",
                "applied": True,
                "recommendations": [
                    "Schedule posts for 7-9 PM",
                    "Test weekend posting",
                    "Analyze timezone performance"
                ]
            },
            {
                "id": "insight_3",
                "insight_type": "content",
                "title": "Hook Performance Analysis",
                "description": "Question-based hooks showing 23% better retention",
                "confidence_score": 0.78,
                "impact_level": "medium",
                "created_at": "2026-05-03T08:45:00Z",
                "applied": False,
                "recommendations": [
                    "Use more question-based hooks",
                    "Test hook variations",
                    "Analyze first 3 seconds performance"
                ]
            }
        ]
        
        return {
            "success": True,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights/generate")
async def generate_insights(request: InsightRequest) -> Dict[str, Any]:
    """Generate new insights from feedback data."""
    try:
        # Mock insight generation
        insight_id = f"insight_{hash(str(request.campaign_id) + str(request.time_range_days))}"
        
        return {
            "success": True,
            "insight_id": insight_id,
            "status": "processing",
            "estimated_completion": "2026-05-03T11:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights/{insight_id}/apply")
async def apply_insight(insight_id: str) -> Dict[str, Any]:
    """Apply an insight recommendation."""
    try:
        # Mock insight application
        return {
            "success": True,
            "insight_id": insight_id,
            "applied": True,
            "applied_at": "2026-05-03T10:30:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Learning Metrics
@router.get("/metrics")
async def get_learning_metrics() -> Dict[str, Any]:
    """Get learning system metrics."""
    try:
        # Mock learning metrics
        metrics = [
            {
                "metric_name": "Average Engagement Rate",
                "current_value": 7.8,
                "previous_value": 6.9,
                "change_percentage": 13.0,
                "trend": "up",
                "last_updated": "2026-05-03T12:00:00Z"
            },
            {
                "metric_name": "Clip Completion Rate",
                "current_value": 72.5,
                "previous_value": 68.2,
                "change_percentage": 6.3,
                "trend": "up",
                "last_updated": "2026-05-03T12:00:00Z"
            },
            {
                "metric_name": "Viral Hit Rate",
                "current_value": 3.2,
                "previous_value": 2.8,
                "change_percentage": 14.3,
                "trend": "up",
                "last_updated": "2026-05-03T12:00:00Z"
            },
            {
                "metric_name": "Average Watch Time",
                "current_value": 12.4,
                "previous_value": 11.8,
                "change_percentage": 5.1,
                "trend": "up",
                "last_updated": "2026-05-03T12:00:00Z"
            },
            {
                "metric_name": "Share Rate",
                "current_value": 4.1,
                "previous_value": 4.5,
                "change_percentage": -8.9,
                "trend": "down",
                "last_updated": "2026-05-03T12:00:00Z"
            }
        ]
        
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/performance")
async def get_performance_analytics(time_range_days: int = 30) -> Dict[str, Any]:
    """Get performance analytics."""
    try:
        # Mock performance analytics
        analytics = {
            "period_days": time_range_days,
            "total_clips": 156,
            "total_views": 2450000,
            "total_engagement": 191000,
            "average_engagement_rate": 7.8,
            "top_performing_platforms": [
                {"platform": "tiktok", "engagement_rate": 9.2, "clip_count": 89},
                {"platform": "youtube", "engagement_rate": 6.1, "clip_count": 45},
                {"platform": "instagram", "engagement_rate": 5.8, "clip_count": 22}
            ],
            "trending_topics": [
                {"topic": "gaming", "growth_rate": 23.4},
                {"topic": "tech", "growth_rate": 18.7},
                {"topic": "lifestyle", "growth_rate": 12.1}
            ]
        }
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Learning Configuration
@router.get("/insight-types")
async def get_insight_types() -> Dict[str, List[str]]:
    """Get available insight types."""
    return {
        "insight_types": ["performance", "timing", "content", "audience", "trend", "technical"]
    }

@router.get("/event-types")
async def get_event_types() -> Dict[str, List[str]]:
    """Get available event types."""
    return {
        "event_types": ["view", "like", "share", "comment", "completion", "click", "save", "report"]
    }

# Health check
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Check health of feedback learning system."""
    return {
        "status": "healthy",
        "services": "events, insights, metrics, analytics"
    }
