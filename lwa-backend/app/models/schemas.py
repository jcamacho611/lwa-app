from __future__ import annotations

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
    confidence: Optional[float] = None
    rank: Optional[int] = None
    reason: Optional[str] = None
    format: str
    clip_url: Optional[str] = None
    raw_clip_url: Optional[str] = None
    edited_clip_url: Optional[str] = None
    preview_image_url: Optional[str] = None
    transcript_excerpt: Optional[str] = None
    edit_profile: Optional[str] = None
    aspect_ratio: Optional[str] = None
    why_this_matters: Optional[str] = None
    confidence_score: Optional[int] = None
    thumbnail_text: Optional[str] = None
    cta_suggestion: Optional[str] = None
    post_rank: Optional[int] = None
    best_post_order: Optional[int] = None
    hook_variants: List[str] = Field(default_factory=list)
    caption_style: Optional[str] = None
    platform_fit: Optional[str] = None
    packaging_angle: Optional[str] = None


class FeatureFlags(BaseModel):
    clip_limit: int = 3
    alt_hooks: bool = False
    campaign_mode: bool = False
    packaging_profiles: bool = False
    history_limit: int = 10
    premium_exports: bool = False
    priority_processing: bool = False


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
    feature_flags: FeatureFlags = Field(default_factory=FeatureFlags)


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
