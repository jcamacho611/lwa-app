export type PlatformOption = "TikTok" | "Instagram Reels" | "YouTube Shorts";

export type ShotPlanStep = {
  role: "hook" | "context" | "payoff" | "loop_end";
  duration_seconds?: number;
  camera_direction?: string | null;
  visual_direction?: string | null;
  motion_direction?: string | null;
  text_overlay?: string | null;
  subtitle_behavior?: string | null;
  transition?: string | null;
  retention_goal?: string | null;
};

export type UserProfile = {
  id: string;
  email: string;
  display_name?: string | null;
  plan_code?: string;
  role?: string;
  created_at?: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: UserProfile;
};

export type UploadAsset = {
  id?: string;
  file_id?: string;
  filename?: string;
  file_name?: string;
  content_type?: string;
  size_bytes?: number;
  file_size?: number;
  public_url?: string | null;
  storage_path?: string;
  source_type?: string | null;
  created_at?: string;
  source_ref?: {
    source_kind: string;
    upload_id?: string;
    source_type?: string;
  };
};

export type BatchSourceRef = {
  source_kind: "url" | "upload";
  video_url?: string;
  upload_id?: string;
};

export type ClipPackSummary = {
  request_id: string;
  source_title?: string | null;
  video_url?: string | null;
  target_platform?: string | null;
  clip_count?: number;
  top_score?: number | null;
  created_at?: string | null;
};

export type WalletLedgerEntry = {
  id: string;
  user_id?: string;
  amount_cents: number;
  kind?: string;
  type?: string;
  status?: string;
  description?: string;
  note?: string | null;
  reference_type?: string | null;
  reference_id?: string | null;
  created_at?: string;
};

export type WalletSummary = {
  pending_cents?: number;
  available_cents?: number;
  lifetime_cents?: number;
  pending_debits_cents?: number;
  eligible_payout_cents?: number;
  currency?: string;
  recent_entries?: WalletLedgerEntry[];
  submission_summary?: SubmissionSummary;
};

export type FeatureFlags = {
  clip_limit?: number;
  alt_hooks?: boolean;
  campaign_mode?: boolean;
  batch_mode?: boolean;
  packaging_profiles?: boolean;
  history_limit?: number;
  caption_editor?: boolean;
  timeline_editor?: boolean;
  wallet_view?: boolean;
  posting_queue?: boolean;
  max_uploads_per_day?: number;
  max_upload_mb?: number;
  max_generations_per_day?: number;
  premium_exports?: boolean;
  priority_processing?: boolean;
  export_bundle?: boolean;
  analytics_feedback?: boolean;
  uploads_enabled?: boolean;
  thumbnail_preview?: boolean;
  export_profiles?: boolean;
  caption_styles?: boolean;
};

export type PayoutRequest = {
  id: string;
  user_id: string;
  amount_cents: number;
  status: string;
  balance_cents?: number;
  created_at?: string;
};

export type BatchSummary = {
  id: string;
  title: string;
  target_platform?: string;
  selected_trend?: string | null;
  status: string;
  total_sources: number;
  completed_sources: number;
  failed_sources?: number;
  request_count?: number;
  clip_count?: number;
  rendered_clip_count?: number;
  strategy_only_clip_count?: number;
  approved_clip_count?: number;
  needs_review_clip_count?: number;
  needs_edit_clip_count?: number;
  evergreen_clip_count?: number;
  trend_tied_clip_count?: number;
  top_clip_score?: number;
  created_at?: string;
  sources?: Array<{
    id: string;
    source_kind: string;
    source_value?: string;
    video_url?: string | null;
    upload_id?: string | null;
    request_id?: string | null;
    status: string;
    clip_count?: number;
    rendered_clip_count?: number;
    strategy_only_clip_count?: number;
    approved_clip_count?: number;
    needs_review_clip_count?: number;
    needs_edit_clip_count?: number;
    evergreen_clip_count?: number;
    trend_tied_clip_count?: number;
    top_clip_score?: number;
    created_at?: string;
  }>;
};

export type CampaignSummary = {
  id: string;
  owner_user_id?: string;
  name?: string;
  title?: string;
  description?: string | null;
  allowed_platforms?: string[];
  status: string;
  target_angle?: string | null;
  requirements?: string | null;
  payout_cents_per_1000_views?: number | null;
  created_at?: string;
  submission_summary?: SubmissionSummary;
};

export type SubmissionStatus = "draft" | "ready" | "submitted" | "approved" | "rejected" | "paid";
export type PayoutState = "locked" | "eligible" | "pending" | "paid";
export type WorkspaceRole = "creator" | "clipper" | "admin" | "operator";

export type SubmissionSummary = {
  total_assignments: number;
  status_counts: Record<string, number>;
  role_counts: Record<string, number>;
  assignment_counts: Record<string, number>;
  eligible_payout_cents: number;
  pending_payout_cents: number;
  paid_payout_cents: number;
};

export type CampaignAssignment = {
  id: string;
  campaign_id: string;
  owner_user_id?: string;
  request_id?: string | null;
  clip_id?: string | null;
  assignment_kind: "clip" | "clip_pack";
  title?: string | null;
  hook?: string | null;
  target_platform?: string | null;
  packaging_angle?: string | null;
  assignee_role: "creator" | "clipper" | "admin";
  assignee_label?: string | null;
  status: SubmissionStatus;
  payout_state: PayoutState;
  payout_amount_cents?: number | null;
  note?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type CampaignDetail = {
  campaign: CampaignSummary;
  clips: ClipResult[];
  jobs: Array<{
    id: string;
    status: string;
    message: string;
    created_at?: string;
    updated_at?: string;
  }>;
  assignments: CampaignAssignment[];
  submission_summary: SubmissionSummary;
};

export type PostingConnection = {
  id: string;
  user_id?: string;
  provider: string;
  account_label?: string | null;
  is_active?: boolean;
  created_at?: string;
};

export type ScheduledPost = {
  id: string;
  owner_user_id?: string;
  provider: string;
  status: string;
  scheduled_for?: string | null;
  clip_id: string;
  caption?: string | null;
  created_at?: string;
};

export type CampaignRequirementCheck = {
  status: "pass" | "warning" | "fail" | "unknown";
  requirement: string;
  message: string;
};

export type ClipResult = {
  id: string;
  record_id?: string | null;
  request_id?: string | null;
  clip_id?: string | null;
  title: string;
  hook: string;
  caption: string;
  start_time?: string | null;
  end_time?: string | null;
  score: number;
  virality_score?: number | null;
  confidence?: number | null;
  confidence_score?: number | null;
  confidence_label?: string | null;
  algorithm_version?: string | null;
  hook_score?: number | null;
  hook_strength?: string | number | null;
  render_readiness_score?: number | null;
  quality_gate_status?: "pass" | "warning" | "fail" | "unknown" | string | null;
  quality_gate_warnings?: string[] | null;
  revenue_intent_score?: number | null;
  offer_fit_score?: number | null;
  rank?: number | null;
  post_rank?: number | null;
  suggested_post_order?: number | null;
  is_best_clip?: boolean;
  reason?: string | null;
  why_this_matters?: string | null;
  first_three_seconds_assessment?: string | null;
  retention_reason?: string | null;
  fallback_reason?: string | null;
  scoring_explanation?: string | null;
  cta_suggestion?: string | null;
  thumbnail_text?: string | null;
  packaging_angle?: string | null;
  platform_fit?: string | null;
  platform_recommendation_reason?: string | null;
  recommended_platform?: string | null;
  recommended_content_type?: string | null;
  recommended_output_style?: string | null;
  caption_preset?: string | null;
  target_platform?: string | null;
  suggested_platform?: string | null;
  detected_category?: string | null;
  category?: string | null;
  source_index?: number | null;
  source_label?: string | null;
  batch_group?: string | null;
  selection_reason?: string | null;
  duplicate_risk?: string | null;
  diversity_bucket?: string | null;
  signals?: Record<string, number> | null;
  score_breakdown?: Record<string, number | null | undefined> | null;
  platform_compatibility?: Record<string, boolean> | null;
  frontend_badges?: Array<string | { badge?: string; label?: string; color?: string; priority?: string; placement?: string }> | null;
  platform_notes?: string[];
  best_post_order?: number | null;
  hook_variants?: string[];
  hooks?: Array<Record<string, unknown>> | null;
  caption_variants?: Record<string, string>;
  caption_style?: string | null;
  caption_style_reason?: string | null;
  suggested_caption_style?: string | null;
  suggested_caption_position?: string | null;
  emphasis_words?: string[] | null;
  duration?: number | null;
  timestamp_start?: string | null;
  timestamp_end?: string | null;
  transcript?: string | null;
  cta?: string | null;
  suggested_cta?: string | null;
  preview_url?: string | null;
  download_url?: string | null;
  thumbnail_url?: string | null;
  clip_url?: string | null;
  edited_clip_url?: string | null;
  raw_clip_url?: string | null;
  preview_image_url?: string | null;
  caption_txt_url?: string | null;
  caption_srt_url?: string | null;
  caption_vtt_url?: string | null;
  burned_caption_url?: string | null;
  export_filename?: string | null;
  approval_state?: string | null;
  campaign_requirement_checks?: CampaignRequirementCheck[];
  campaign_role?: string | null;
  campaign_reason?: string | null;
  funnel_stage?: string | null;
  is_rendered?: boolean;
  is_strategy_only?: boolean;
  strategy_only?: boolean;
  reason_not_rendered?: string | null;
  rendered_status?: string | null;
  render_status?: "pending" | "rendering" | "ready" | "failed" | string | null;
  render_error?: string | null;
  rendered?: boolean | null;
  clip_type?: string | null;
  viral_trigger?: string | null;
  energy_level?: string | null;
  shot_plan?: ShotPlanStep[];
  shot_plan_confidence?: number | null;
  visual_engine_prompt?: string | null;
  motion_prompt?: string | null;
  render_provider?: string | null;
  rendered_by?: string | null;
  visual_engine_status?: "ready_now" | "needs_review" | "strategy_only" | "render_failed" | "recoverable" | string | null;
  render_quality_score?: number | null;
  strategy_only_reason?: string | null;
  recovery_recommendation?: string | null;
  campaign_fit_score?: number | null;
  campaign_fit_reason?: string | null;
  required_hashtag_suggestions?: string[];
  compliance_notes?: string[];
  package_text?: string | null;
  export_ready?: boolean;
  asset_manifest?: Record<string, unknown> | null;
  download_asset_url?: string | null;
  selected_trend?: string | null;
  text_overlay_plan?: string | null;
  subtitle_guidance?: string | null;
  transition_plan?: string | null;
  trend_match_score?: number | null;
  trend_alignment_reason?: string | null;
  reuse_potential?: number | null;
  evergreen_status?: string | null;
  time_sensitivity?: string | null;
  burned_caption?: string;
  export_package?: {
    title?: string;
    hook?: string;
    caption?: string;
    thumbnail_text?: string;
    cta?: string;
    platform_fit?: string;
    post_rank?: number;
  };
  export_bundle?: {
    post_order?: number | null;
    post_sequence_label?: string | null;
    packaging_angle?: string | null;
    thumbnail_text?: string | null;
    cta?: string | null;
    preview_ready?: boolean;
    download_ready?: boolean;
    bundle_format?: string | null;
    manifest_ready?: boolean;
    artifact_types?: string[];
  };
  trim_start_seconds?: number | null;
  trim_end_seconds?: number | null;
  caption_style_override?: string | null;
  approved?: boolean;
  created_at?: string | null;
  auto_editor?: {
    status?: string;
    viral_score?: number;
    confidence_score?: number;
    processing_stages?: Array<{
      name: string;
      description: string;
      completed: boolean;
    }>;
    recommendations?: Array<{
      title: string;
      description: string;
    }>;
    issues?: Array<{
      title: string;
      description: string;
    }>;
  };
};

export type GenerateResponse = {
  request_id: string;
  video_url: string;
  status: string;
  status_reason?: string | null;
  source_type?: string;
  source_title?: string | null;
  source_platform?: string | null;
  transcript?: string | null;
  visual_summary?: string | null;
  preview_asset_url?: string | null;
  download_asset_url?: string | null;
  thumbnail_url?: string | null;
  selected_trend?: string | null;
  processing_summary?: {
    target_platform?: string;
    platform_decision?: "auto" | "manual" | string;
    recommended_platform?: string | null;
    platform_recommendation_reason?: string | null;
    recommended_content_type?: string | null;
    recommended_output_style?: string | null;
    manual_platform_override?: boolean;
    ai_provider?: string;
    plan_name?: string;
    plan_code?: string;
    credits_remaining?: number;
    estimated_turnaround?: string;
    recommended_next_step?: string;
    requested_clip_count?: number;
    generated_clip_count?: number;
    clip_count_requested?: number | null;
    clip_count_allowed?: number | null;
    clip_count_returned?: number | null;
    source_count?: number | null;
    batch_mode?: boolean;
    batch_id?: string | null;
    generation_mode?: string | null;
    workflow_stage?: string | null;
    upgrade_reason?: string | null;
    visual_engine_enabled?: boolean;
    visual_engine_attempted_count?: number;
    visual_engine_ready_count?: number;
    visual_engine_failed_count?: number;
    rendered_clip_count?: number;
    strategy_only_clip_count?: number;
    raw_assets_created?: number;
    edited_assets_created?: number;
    fallback_reason?: string | null;
    bulk_export_ready?: boolean;
    export_bundle_available?: boolean;
    export_bundle_format?: string | null;
    export_bundle_manifest_url?: string | null;
    export_bundle_notes?: string[];
    manifest_url?: string | null;
    campaign_name?: string | null;
    campaign_mode?: boolean;
    campaign_goal?: string | null;
    allowed_platforms?: string[];
    campaign_readiness?: string | null;
    campaign_notes?: string[];
    feature_flags?: FeatureFlags;
  };
  clips: ClipResult[];
  clips_summary?: Array<{
    clip_id: string;
    title?: string;
    duration_seconds?: number;
    ai_score?: number;
    render_status?: string;
  }>;
  strategy_only?: boolean;
  generation_method?: string;
  scripts?: GeneratedScripts | null;
};

export type GeneratedScripts = {
  main: string;
  variants: string[];
  hooks: string[];
  titles: string[];
  ctas: string[];
};

export type ExportBundleResponse = {
  bundle_id: string;
  download_url: string;
  file_name: string;
  clip_count: number;
  created_at: string;
  manifest_url?: string | null;
  bundle_format?: string | null;
  artifact_types?: string[];
  artifact_counts?: Record<string, number> | null;
  size_bytes?: number;
};

export type ClipRecoveryJob = {
  job_id: string;
  clip_id: string;
  status: string;
  message: string;
  poll_url: string;
};

export type ClipRecoveryStatus = {
  job_id: string;
  clip_id: string;
  status: "queued" | "processing" | "recovered" | "failed" | string;
  message: string;
  created_at?: string;
  updated_at?: string;
  recovered_clip?: ClipResult | null;
  error?: string | null;
};

export type EditableClip = ClipResult;

export type ClipPackDetail = {
  request_id: string;
  source_title?: string | null;
  source_type?: string | null;
  source_platform?: string | null;
  transcript?: string | null;
  visual_summary?: string | null;
  preview_asset_url?: string | null;
  download_asset_url?: string | null;
  thumbnail_url?: string | null;
  clips: EditableClip[];
};
