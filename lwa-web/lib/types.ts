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
  created_at?: string;
  source_ref?: {
    source_kind: string;
    upload_id?: string;
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
  packaging_profiles?: boolean;
  history_limit?: number;
  caption_editor?: boolean;
  timeline_editor?: boolean;
  wallet_view?: boolean;
  posting_queue?: boolean;
  max_uploads_per_day?: number;
  max_generations_per_day?: number;
  premium_exports?: boolean;
  priority_processing?: boolean;
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
  rank?: number | null;
  post_rank?: number | null;
  reason?: string | null;
  why_this_matters?: string | null;
  cta_suggestion?: string | null;
  thumbnail_text?: string | null;
  packaging_angle?: string | null;
  platform_fit?: string | null;
  best_post_order?: number | null;
  hook_variants?: string[];
  caption_variants?: Record<string, string>;
  caption_style?: string | null;
  duration?: number | null;
  timestamp_start?: string | null;
  timestamp_end?: string | null;
  transcript?: string | null;
  cta?: string | null;
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
  is_rendered?: boolean;
  is_strategy_only?: boolean;
  render_status?: "pending" | "rendering" | "ready" | "failed" | string | null;
  render_error?: string | null;
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
};

export type GenerateResponse = {
  request_id: string;
  video_url: string;
  status: string;
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
    visual_engine_enabled?: boolean;
    visual_engine_attempted_count?: number;
    visual_engine_ready_count?: number;
    visual_engine_failed_count?: number;
    rendered_clip_count?: number;
    strategy_only_clip_count?: number;
    bulk_export_ready?: boolean;
    manifest_url?: string | null;
    campaign_name?: string | null;
    feature_flags?: FeatureFlags;
  };
  clips: ClipResult[];
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
