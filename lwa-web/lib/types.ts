export type PlatformOption = "TikTok" | "Instagram Reels" | "YouTube Shorts";

export type UserProfile = {
  id: string;
  email: string;
  display_name?: string | null;
  plan_code?: string;
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
  currency?: string;
  recent_entries?: WalletLedgerEntry[];
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
  created_at?: string;
  sources?: Array<{
    id: string;
    source_kind: string;
    source_value: string;
    request_id?: string | null;
    status: string;
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
  confidence?: number | null;
  rank?: number | null;
  reason?: string | null;
  cta_suggestion?: string | null;
  thumbnail_text?: string | null;
  packaging_angle?: string | null;
  platform_fit?: string | null;
  best_post_order?: number | null;
  hook_variants?: string[];
  clip_url?: string | null;
  edited_clip_url?: string | null;
  raw_clip_url?: string | null;
  preview_image_url?: string | null;
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
  source_platform: string;
  processing_summary?: {
    target_platform?: string;
    ai_provider?: string;
    plan_name?: string;
    estimated_turnaround?: string;
  };
  clips: ClipResult[];
};

export type EditableClip = ClipResult;

export type ClipPackDetail = {
  request_id: string;
  clips: EditableClip[];
};
