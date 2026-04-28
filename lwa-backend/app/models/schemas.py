from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class ProcessRequest(BaseModel):
    video_url: Optional[str] = Field(default=None, description="Public URL for the source video")
    upload_file_id: Optional[str] = None
    prompt: Optional[str] = None
    text_prompt: Optional[str] = None
    source_type: Optional[str] = None
    upload_content_type: Optional[str] = None
    selected_trend: Optional[str] = None
    trend_source: Optional[str] = None
    target_platform: Optional[str] = None
    content_angle: Optional[str] = None
    clip_count: Optional[int] = Field(default=None, ge=1, le=50)
    campaign_brief: Optional[str] = None
    target_audience: Optional[str] = None
    allowed_platforms: Optional[List[str]] = None
    campaign_goal: Optional[str] = None
    required_hashtags: Optional[List[str]] = None
    forbidden_terms: Optional[List[str]] = None

    @model_validator(mode="after")
    def ensure_source(self) -> "ProcessRequest":
        has_prompt = bool((self.prompt or "").strip() or (self.text_prompt or "").strip())
        if not self.video_url and not self.upload_file_id and not has_prompt:
            raise ValueError("Provide video_url, upload_file_id, prompt, or text_prompt")
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
    bundle_format: Optional[str] = None
    manifest_ready: bool = False
    artifact_types: List[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    hook_score: int = 0
    retention_score: int = 0
    emotional_spike_score: int = 0
    clarity_score: int = 0
    platform_fit_score: int = 0
    visual_energy_score: int = 0
    audio_energy_score: int = 0
    controversy_score: int = 0
    educational_value_score: int = 0
    share_comment_score: int = 0
    render_readiness_score: int = 0
    commercial_value_score: int = 0


class CampaignRequirementCheck(BaseModel):
    status: Literal["pass", "warning", "fail", "unknown"] = "unknown"
    requirement: str
    message: str


class GeneratedScripts(BaseModel):
    main: str
    variants: List[str] = Field(default_factory=list)
    hooks: List[str] = Field(default_factory=list)
    titles: List[str] = Field(default_factory=list)
    ctas: List[str] = Field(default_factory=list)


class ShotPlanStep(BaseModel):
    role: Literal["hook", "context", "payoff", "loop_end"]
    duration_seconds: int = 0
    camera_direction: Optional[str] = None
    visual_direction: Optional[str] = None
    motion_direction: Optional[str] = None
    text_overlay: Optional[str] = None
    subtitle_behavior: Optional[str] = None
    transition: Optional[str] = None
    retention_goal: Optional[str] = None


class ClipResult(BaseModel):
    record_id: Optional[str] = None
    id: str
    title: str
    hook: str
    caption: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    score: int
    hook_score: Optional[int] = None
    confidence_score: Optional[int] = None
    confidence: Optional[float] = None
    confidence_label: Optional[str] = None
    reason: Optional[str] = None
    why_this_matters: Optional[str] = None
    first_three_seconds_assessment: Optional[str] = None
    hook_strength: Optional[str | int | float] = None
    retention_reason: Optional[str] = None
    score_breakdown: Optional[ScoreBreakdown] = None
    signals: Optional[Dict[str, float]] = None
    scoring_explanation: Optional[str] = None
    category: Optional[str] = None
    detected_category: Optional[str] = None
    format: Optional[str] = None
    preview_url: Optional[str] = None
    raw_clip_url: Optional[str] = None
    edited_clip_url: Optional[str] = None
    clip_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    preview_image_url: Optional[str] = None
    caption_txt_url: Optional[str] = None
    caption_srt_url: Optional[str] = None
    caption_vtt_url: Optional[str] = None
    burned_caption_url: Optional[str] = None
    export_filename: Optional[str] = None
    render_status: Optional[str] = None
    rendered_status: Optional[str] = None
    is_rendered: Optional[bool] = None
    is_strategy_only: Optional[bool] = None
    rendered: Optional[bool] = None
    strategy_only: Optional[bool] = None
    is_best_clip: Optional[bool] = None
    fallback_reason: Optional[str] = None
    post_rank: Optional[int] = None
    best_post_order: Optional[int] = None
    virality_score: Optional[int] = None
    rank: Optional[int] = None
    source_index: Optional[int] = None
    source_label: Optional[str] = None
    batch_group: Optional[str] = None
    selection_reason: Optional[str] = None
    duplicate_risk: Optional[str] = None
    diversity_bucket: Optional[str] = None
    target_platform: Optional[str] = None
    platform_compatibility: Optional[Dict[str, bool]] = None
    frontend_badges: Optional[List[Dict[str, Any]]] = None
    transcript_excerpt: Optional[str] = None
    edit_profile: Optional[str] = None
    aspect_ratio: Optional[str] = None
    thumbnail_text: Optional[str] = None
    cta_suggestion: Optional[str] = None
    hook_variants: List[str] = Field(default_factory=list)
    hooks: Optional[List[Dict[str, Any]]] = None
    caption_variants: dict[str, str] = Field(default_factory=dict)
    caption_style: Optional[str] = None
    caption_preset: Optional[str] = None
    caption_track: Optional[Dict[str, Any]] = None
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
    package_text: Optional[str] = None
    export_ready: bool = False
    asset_manifest: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None
    render_error: Optional[str] = None
    request_id: Optional[str] = None
    clip_type: Optional[str] = None
    viral_trigger: Optional[str] = None
    energy_level: Optional[str] = None
    shot_plan: List[ShotPlanStep] = Field(default_factory=list)
    shot_plan_confidence: Optional[int] = None
    visual_engine_prompt: Optional[str] = None
    motion_prompt: Optional[str] = None
    render_provider: Optional[str] = None
    rendered_by: Optional[str] = None
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    visual_engine_status: Optional[str] = None
    render_quality_score: Optional[int] = None
    render_readiness_score: Optional[int] = None
    strategy_only_reason: Optional[str] = None
    recovery_recommendation: Optional[str] = None
    text_overlay_plan: Optional[str] = None
    subtitle_guidance: Optional[str] = None
    transition_plan: Optional[str] = None
    trend_match_score: Optional[int] = None
    trend_alignment_reason: Optional[str] = None
    reuse_potential: Optional[int] = None
    evergreen_status: Optional[str] = None
    time_sensitivity: Optional[str] = None
    approval_state: Optional[str] = None
    risk_flags: List[str] = Field(default_factory=list)
    campaign_requirement_checks: List[CampaignRequirementCheck] = Field(default_factory=list)
    campaign_fit_score: Optional[int] = None
    campaign_fit_reason: Optional[str] = None
    platform_notes: List[str] = Field(default_factory=list)
    required_hashtag_suggestions: List[str] = Field(default_factory=list)
    compliance_notes: List[str] = Field(default_factory=list)


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
    batch_mode: bool = False
    export_bundle: bool = False
    analytics_feedback: bool = False


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
    fallback_reason: Optional[str] = None
    source_title: Optional[str] = None
    source_type: Optional[str] = None
    source_duration_seconds: Optional[int] = None
    source_count: Optional[int] = None
    clip_count_requested: Optional[int] = None
    clip_count_returned: Optional[int] = None
    batch_mode: bool = False
    batch_id: Optional[str] = None
    generation_mode: Optional[str] = None
    workflow_stage: Optional[str] = None
    upgrade_reason: Optional[str] = None
    campaign_mode: bool = False
    campaign_goal: Optional[str] = None
    allowed_platforms: List[str] = Field(default_factory=list)
    campaign_readiness: Optional[str] = None
    campaign_notes: List[str] = Field(default_factory=list)
    assets_created: int = 0
    raw_assets_created: int = 0
    edited_assets_created: int = 0
    visual_engine_enabled: bool = False
    visual_engine_attempted_count: int = 0
    visual_engine_ready_count: int = 0
    visual_engine_failed_count: int = 0
    rendered_clip_count: int = 0
    strategy_only_clip_count: int = 0
    export_bundle_available: bool = False
    export_bundle_format: Optional[str] = None
    export_bundle_manifest_url: Optional[str] = None
    export_bundle_notes: List[str] = Field(default_factory=list)
    bulk_export_ready: bool = False
    manifest_url: Optional[str] = None
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
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    plan_code: Optional[str] = None
    generation_mode: Optional[str] = None
    rendered_clip_count: Optional[int] = None
    strategy_only_clip_count: Optional[int] = None
    fallback_used: Optional[bool] = None
    error_type: Optional[str] = None
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


class GenerationBackgroundRequest(BaseModel):
    prompt: str
    style_preset: Optional[str] = None
    motion_profile: Optional[str] = None
    duration_seconds: int = Field(default=6, ge=1, le=30)
    aspect_ratio: str = "9:16"
    seed: Optional[int] = None
    reference_image_url: Optional[str] = None
    source_clip_url: Optional[str] = None
    source_asset_id: Optional[str] = None


class GenerationAssetResponse(BaseModel):
    asset_id: Optional[str] = None
    provider: str = "lwa"
    status: Optional[str] = None
    asset_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    public_url: Optional[str] = None
    local_path: Optional[str] = None
    content_type: Optional[str] = None
    duration_seconds: Optional[int] = None
    aspect_ratio: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerationJobResponse(BaseModel):
    job_id: str
    provider_job_id: Optional[str] = None
    status: str
    message: str
    poll_url: str
    asset: Optional[GenerationAssetResponse] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerationJobStatusResponse(BaseModel):
    job_id: str
    provider_job_id: Optional[str] = None
    status: str
    message: str
    created_at: str
    updated_at: str
    asset: Optional[GenerationAssetResponse] = None
    error: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


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


class GenerationRequest(BaseModel):
    mode: Literal["video", "image", "idea"] = "video"
    prompt: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    upload_file_id: Optional[str] = None
    target_platform: Optional[str] = None
    style_preset: Optional[str] = None
    motion_profile: Optional[str] = None
    duration_seconds: Optional[int] = 8
    seed: Optional[int] = None
    reference_image_url: Optional[str] = None
    source_clip_url: Optional[str] = None
    source_asset_id: Optional[str] = None
    text_prompt: Optional[str] = None
    image_path: Optional[str] = None
    provider: str = "lwa"
    duration: Optional[float] = 30.0
    style: Optional[str] = None
    aspect_ratio: str = "9:16"
    motion_strength: str = "medium"
    user_id: Optional[str] = None


class GeneratedAsset(BaseModel):
    id: str
    provider: str
    asset_type: str
    status: str
    prompt: Optional[str] = None
    preview_url: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    source_refs: dict[str, str] = Field(default_factory=dict)
    created_at: Optional[str] = None
    error: Optional[str] = None


class GenerationResponse(BaseModel):
    clips: List[ClipResult]
    request_id: str
    generation_type: str
    provider: str
    total_clips: int
    processing_summary: Dict[str, Any]
    metadata: Dict[str, Any]


class EditClipRequest(BaseModel):
    clip_id: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    caption_text: Optional[str] = None
