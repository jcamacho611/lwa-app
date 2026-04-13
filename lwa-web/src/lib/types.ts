// ─── Request ────────────────────────────────────────────────────────────────

export interface GenerateRequest {
  video_url: string;
  target_platform?: string;
  content_angle?: string;
  selected_trend?: string;
}

// ─── Response ────────────────────────────────────────────────────────────────

export interface TrendItem {
  id: string;
  title: string;
  source: string;
  detail: string;
  url?: string;
}

export interface FeatureFlags {
  clip_limit: number;
  alt_hooks: boolean;
  campaign_mode: boolean;
  packaging_profiles: boolean;
  history_limit: number;
  premium_exports: boolean;
  priority_processing: boolean;
}

export interface ProcessingSummary {
  plan_name: string;
  credits_remaining: number;
  estimated_turnaround: string;
  recommended_next_step: string;
  ai_provider: string;
  target_platform: string;
  trend_used?: string;
  sources_considered: string[];
  processing_mode: string;
  selection_strategy: string;
  source_title?: string;
  source_duration_seconds?: number;
  assets_created: number;
  edited_assets_created: number;
  feature_flags: FeatureFlags;
}

export interface ClipResult {
  id: string;
  title: string;
  hook: string;
  caption: string;
  start_time: string;
  end_time: string;
  score: number;
  confidence?: number;
  rank?: number;
  reason?: string;
  format: string;
  clip_url?: string;
  raw_clip_url?: string;
  edited_clip_url?: string;
  preview_image_url?: string;
  transcript_excerpt?: string;
  edit_profile?: string;
  aspect_ratio?: string;
  why_this_matters?: string;
  confidence_score?: number;
  thumbnail_text?: string;
  cta_suggestion?: string;
  post_rank?: number;
  best_post_order?: number;
  hook_variants: string[];
  caption_style?: string;
  platform_fit?: string;
  packaging_angle?: string;
}

export interface ClipBatchResponse {
  request_id: string;
  video_url: string;
  status: string;
  source_platform: string;
  processing_summary: ProcessingSummary;
  trend_context: TrendItem[];
  clips: ClipResult[];
}

// ─── UI State ────────────────────────────────────────────────────────────────

export type GenerationStatus = 'idle' | 'loading' | 'success' | 'error';

export interface GenerationState {
  status: GenerationStatus;
  data: ClipBatchResponse | null;
  error: string | null;
}
