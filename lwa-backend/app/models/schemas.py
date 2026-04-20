from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field, model_validator


class ProcessRequest(BaseModel):
    video_url: Optional[str] = Field(default=None, description="Public URL for the source video")
    upload_file_id: Optional[str] = None
    source_type: Optional[str] = None
    upload_content_type: Optional[str] = None
    selected_trend: Optional[str] = None
    trend_source: Optional[str] = None
    target_platform: Optional[str] = None
    content_angle: Optional[str] = None

    @model_validator(mode="after")
    def ensure_source(self) -> "ProcessRequest":
        if not self.video_url and not self.upload_file_id:
            raise ValueError("Provide either video_url or upload_file_id")
        return self


class TrendItem(BaseModel):
    id: str
    title: str
    source: str
    detail: str
    url: Optional[str] = None


class CaptionModes(BaseModel):
    primary: Optional[str] = None
    short: Optional[str] = None
    story: Optional[str] = None
    educational: Optional[str] = None
    controversial: Optional[str] = None
    style: Optional[str] = None
    angle: Optional[str] = None


class EditPlan(BaseModel):
    opening_beat: Optional[str] = None
    pacing: Optional[str] = None
    visual_focus: Optional[str] = None
    overlay_plan: Optional[str] = None
    posting_role: Optional[str] = None


class ExportBundle(BaseModel):
    post_order: Optional[int] = None
    post_sequence_label: Optional[str] = None
    packaging_angle: Optional[str] = None
    thumbnail_text: Optional[str] = None
    cta: Optional[str] = None
    preview_ready: bool = False
    download_ready: bool = False


class GeneratedScripts(BaseModel):
    main: str
    variants: List[str] = Field(default_factory=list)
    hooks: List[str] = Field(default_factory=list)
    titles: List[str] = Field(default_factory=list)
    ctas: List[str] = Field(default_factory=list)


class ClipResult(BaseModel):
    record_id: Optional[str] = None
    id: str
    title: str
    hook: str
    caption: str
    start_time: str
    end_time: str
    score: int
    virality_score: Optional[int] = None
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
    caption_variants: dict[str, str] = Field(default_factory=dict)
    caption_style: Optional[str] = None
    caption_modes: Optional[CaptionModes] = None
    edit_plan: Optional[EditPlan] = None
    export_bundle: Optional[ExportBundle] = None
    platform_fit: Optional[str] = None
    packaging_angle: Optional[str] = None
    duration: Optional[int] = None
    timestamp_start: Optional[str] = None
    timestamp_end: Optional[str] = None
    transcript: Optional[str] = None
    cta: Optional[str] = None
    preview_url: Optional[str] = None
    download_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class FeatureFlags(BaseModel):
    clip_limit: int = 3
    alt_hooks: bool = False
    campaign_mode: bool = False
    packaging_profiles: bool = False
    history_limit: int = 10
    caption_editor: bool = False
    timeline_editor: bool = False
    wallet_view: bool = False
    posting_queue: bool = False
    max_uploads_per_day: int = 0
    max_generations_per_day: int = 0
    premium_exports: bool = False
    priority_processing: bool = False


class ProcessingSummary(BaseModel):
    plan_code: str = "free"
    plan_name: str
    credits_remaining: int
    estimated_turnaround: str
    recommended_next_step: str
    ai_provider: str
    target_platform: str
    platform_decision: str = "auto"
    recommended_platform: Optional[str] = None
    platform_recommendation_reason: Optional[str] = None
    recommended_content_type: Optional[str] = None
    recommended_output_style: Optional[str] = None
    manual_platform_override: bool = False
    trend_used: Optional[str] = None
    sources_considered: List[str]
    processing_mode: str
    selection_strategy: str
    source_title: Optional[str] = None
    source_type: Optional[str] = None
    source_duration_seconds: Optional[int] = None
    assets_created: int = 0
    edited_assets_created: int = 0
    rendered_clip_count: int = 0
    strategy_only_clip_count: int = 0
    free_preview_unlocked: bool = True
    persistence_requires_signup: bool = False
    upgrade_prompt: Optional[str] = None
    feature_flags: FeatureFlags = Field(default_factory=FeatureFlags)


class ClipBatchResponse(BaseModel):
    request_id: str
    video_url: str
    status: str
    source_type: str = "url"
    source_title: Optional[str] = None
    source_platform: Optional[str] = None
    transcript: Optional[str] = None
    visual_summary: Optional[str] = None
    preview_asset_url: Optional[str] = None
    download_asset_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    processing_summary: ProcessingSummary
    trend_context: List[TrendItem]
    clips: List[ClipResult]
    scripts: Optional[GeneratedScripts] = None


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


class ClipRecoveryJobResponse(BaseModel):
    job_id: str
    clip_id: str
    status: str
    message: str
    poll_url: str


class ClipRecoveryStatusResponse(BaseModel):
    job_id: str
    clip_id: str
    status: str
    message: str
    created_at: str
    updated_at: str
    recovered_clip: Optional[ClipResult] = None
    error: Optional[str] = None


class SeedanceBackgroundRequest(BaseModel):
    prompt: str
    style_preset: Optional[str] = None
    motion_profile: Optional[str] = None
    duration_seconds: int = Field(default=6, ge=1, le=30)
    aspect_ratio: str = "9:16"
    seed: Optional[int] = None
    reference_image_url: Optional[str] = None
    source_clip_url: Optional[str] = None
    source_asset_id: Optional[str] = None


class SeedanceAssetResponse(BaseModel):
    asset_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SeedanceJobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    poll_url: str
    asset: Optional[SeedanceAssetResponse] = None


class SeedanceJobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: str
    created_at: str
    updated_at: str
    asset: Optional[SeedanceAssetResponse] = None
    error: Optional[str] = None


class AuthRequest(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size_bytes: int
    public_url: Optional[str] = None
    storage_path: str
    source_ref: dict[str, str]


class ClipPatchRequest(BaseModel):
    trim_start_seconds: Optional[float] = None
    trim_end_seconds: Optional[float] = None
    caption_override: Optional[str] = None
    hook_override: Optional[str] = None
    cta_override: Optional[str] = None
    thumbnail_text_override: Optional[str] = None
    caption_style_override: Optional[str] = None
    packaging_angle_override: Optional[str] = None


class CampaignCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    allowed_platforms: List[str] = Field(default_factory=list)
    target_angle: Optional[str] = None
    requirements: Optional[str] = None
    payout_cents_per_1000_views: Optional[int] = None


class CampaignPatchRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    allowed_platforms: Optional[List[str]] = None
    target_angle: Optional[str] = None
    requirements: Optional[str] = None
    payout_cents_per_1000_views: Optional[int] = None
    status: Optional[str] = None


class CampaignAssignmentCreateRequest(BaseModel):
    request_id: Optional[str] = None
    clip_ids: List[str] = Field(default_factory=list)
    target_platform: Optional[str] = None
    packaging_angle: Optional[str] = None
    assignee_role: Optional[str] = "creator"
    assignee_label: Optional[str] = None
    note: Optional[str] = None
    payout_amount_cents: Optional[int] = None


class CampaignAssignmentPatchRequest(BaseModel):
    status: Optional[str] = None
    assignee_role: Optional[str] = None
    assignee_label: Optional[str] = None
    note: Optional[str] = None
    payout_amount_cents: Optional[int] = None


class PayoutRequestCreate(BaseModel):
    amount_cents: int = Field(..., gt=0)


class PostingConnectionCreate(BaseModel):
    provider: str
    account_label: Optional[str] = None


class ScheduledPostCreate(BaseModel):
    clip_id: str
    provider: str
    caption: Optional[str] = None
    scheduled_for: Optional[str] = None


class ScheduledPostPatch(BaseModel):
    status: Optional[str] = None
    caption: Optional[str] = None
    scheduled_for: Optional[str] = None


class EditClipRequest(BaseModel):
    clip_id: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    caption_text: Optional[str] = None
