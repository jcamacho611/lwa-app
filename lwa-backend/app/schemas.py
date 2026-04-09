from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ProcessRequest(BaseModel):
    video_url: HttpUrl = Field(..., description="Public URL for the source video")
    selected_trend: Optional[str] = None
    trend_source: Optional[str] = None
    target_platform: Optional[str] = None
    content_angle: Optional[str] = None


class TrendItem(BaseModel):
    id: str
    title: str
    source: str
    detail: str
    url: Optional[str] = None


class ClipResult(BaseModel):
    id: str
    title: str
    hook: str
    caption: str
    start_time: str
    end_time: str
    score: int
    format: str
    clip_url: Optional[str] = None
    raw_clip_url: Optional[str] = None
    edited_clip_url: Optional[str] = None
    transcript_excerpt: Optional[str] = None
    edit_profile: Optional[str] = None
    aspect_ratio: Optional[str] = None


class ProcessingSummary(BaseModel):
    plan_name: str
    credits_remaining: int
    estimated_turnaround: str
    recommended_next_step: str
    ai_provider: str
    target_platform: str
    trend_used: Optional[str] = None
    sources_considered: List[str]
    processing_mode: str
    selection_strategy: str
    source_title: Optional[str] = None
    source_duration_seconds: Optional[int] = None
    assets_created: int = 0
    edited_assets_created: int = 0


class ClipBatchResponse(BaseModel):
    request_id: str
    video_url: HttpUrl
    status: str
    source_platform: str
    processing_summary: ProcessingSummary
    trend_context: List[TrendItem]
    clips: List[ClipResult]


class TrendsResponse(BaseModel):
    status: str
    updated_at: str
    trends: List[TrendItem]


class JobCreatedResponse(BaseModel):
    job_id: str
    status: str
    poll_url: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: str
    created_at: str
    updated_at: str
    result: Optional[ClipBatchResponse] = None
    error: Optional[str] = None
