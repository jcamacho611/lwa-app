const PLATFORM_BLOCKED_SOURCE_MESSAGE =
  "This platform blocked server access. Upload the video/audio file directly, try another public source, or use prompt mode.";

function extractApiErrorMessage(data: unknown): string {
  if (!data) return "Request failed.";

  if (typeof data === "string") return data;

  if (Array.isArray(data)) {
    return data.map((item) => extractApiErrorMessage(item)).filter(Boolean).join(" ");
  }

  if (typeof data === "object") {
    const record = data as Record<string, unknown>;

    const directMessage =
      record.user_message ||
      record.message ||
      record.error ||
      record.reason ||
      record.detail;

    if (directMessage && directMessage !== data) {
      return extractApiErrorMessage(directMessage);
    }

    return Object.values(record)
      .map((value) => extractApiErrorMessage(value))
      .filter(Boolean)
      .join(" ");
  }

  return String(data);
}

function sanitizeApiErrorMessage(message: unknown): string {
  const value = extractApiErrorMessage(message);
  const lower = value.toLowerCase();

  if (
    lower.includes("sign in to confirm") ||
    lower.includes("not a bot") ||
    lower.includes("yt-dlp") ||
    lower.includes("cookies") ||
    lower.includes("--cookies") ||
    lower.includes("use --cookies-from-browser") ||
    lower.includes("github.com/yt-dlp") ||
    lower.includes("platform_blocked")
  ) {
    return PLATFORM_BLOCKED_SOURCE_MESSAGE;
  }

  return value || "Request failed.";
}

import {
  AuthResponse,
  BatchSourceRef,
  BatchSummary,
  CampaignAssignment,
  CampaignDetail,
  CampaignSummary,
  ClipPackDetail,
  ClipRecoveryJob,
  ClipRecoveryStatus,
  ClipResult,
  ClipPackSummary,
  ExportBundleResponse,
  GenerateResponse,
  PlatformOption,
  PayoutRequest,
  PostingConnection,
  ScheduledPost,
  UploadAsset,
  UserProfile,
  WalletLedgerEntry,
  WalletSummary,
} from "./types";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "";

if (!BASE_URL && typeof window !== "undefined") {
  console.error("[LWA_CONFIG] NEXT_PUBLIC_API_BASE_URL missing");
}

type GeneratePayload = {
  mode?: "video" | "image" | "idea";
  url?: string;
  platform?: PlatformOption;
  uploadFileId?: string;
  contentAngle?: string;
  ideaPrompt?: string;
};

type BatchCreatePayload = {
  title: string;
  target_platform: string;
  selected_trend?: string;
  sources: BatchSourceRef[];
};

type CampaignCreatePayload = {
  title: string;
  description?: string;
  allowed_platforms: string[];
  target_angle?: string;
  requirements?: string;
  payout_cents_per_1000_views?: number;
};

type CampaignUpdatePayload = Partial<CampaignCreatePayload> & {
  status?: string;
};

type PostingConnectionPayload = {
  provider: string;
  account_label?: string;
};

type ScheduledPostPayload = {
  clip_id: string;
  provider: string;
  caption?: string;
  scheduled_for?: string;
};

type ScheduledPostPatchPayload = {
  status?: string;
  caption?: string;
  scheduled_for?: string;
};

function logApiError(endpoint: string, status: number | undefined, message: string) {
  console.error("[LWA_API_ERROR]", {
    endpoint,
    status,
    message,
    timestamp: new Date().toISOString(),
  });
}

async function jsonRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response | undefined;

  try {
    response = await fetch(path, init);
    const text = await response.text();
    const data = (text ? JSON.parse(text) : {}) as T & { detail?: string; error?: string; message?: string };

    if (!response.ok) {
      const message = extractApiErrorMessage(data);
      logApiError(path, response.status, message);
      throw new ApiError(sanitizeApiErrorMessage(message), response.status);
    }

    return data as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      throw error;
    }
    const message = error instanceof Error ? error.message : "Request failed.";
    logApiError(path, response?.status, message);
    throw error;
  }
}

function authHeaders(token?: string | null, contentType = true) {
  return {
    ...(contentType ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export function normalizeUrl(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return trimmed;
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  if (trimmed.startsWith("//")) return `https:${trimmed}`;
  return `https://${trimmed}`;
}

export async function generateClips(
  payload: GeneratePayload,
  token?: string | null,
  options?: { signal?: AbortSignal },
): Promise<GenerateResponse> {
  const normalizedPayload = payload.url
    ? {
        ...payload,
        url: normalizeUrl(payload.url),
      }
    : payload;

  return jsonRequest<GenerateResponse>("/api/generate", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(normalizedPayload),
    signal: options?.signal,
  });
}

export async function exportVideoBundle(requestId: string, token?: string | null): Promise<ExportBundleResponse> {
  return jsonRequest<ExportBundleResponse>(`/api/video-export/${encodeURIComponent(requestId)}`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export async function exportClipBundle(
  payload: { source_url?: string; clips: GenerateResponse["clips"] },
  token?: string | null,
): Promise<ExportBundleResponse> {
  return jsonRequest<ExportBundleResponse>("/api/export-bundle", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function signUp(email: string, password: string) {
  return jsonRequest<AuthResponse>("/api/auth/signup", {
    method: "POST",
    headers: authHeaders(null),
    body: JSON.stringify({ email, password }),
  });
}

export async function logIn(email: string, password: string) {
  return jsonRequest<AuthResponse>("/api/auth/login", {
    method: "POST",
    headers: authHeaders(null),
    body: JSON.stringify({ email, password }),
  });
}

export async function loadMe(token: string) {
  return jsonRequest<UserProfile>("/api/auth/me", {
    headers: authHeaders(token, false),
  });
}

export async function logOut(token: string) {
  return jsonRequest<{ status: string; message: string }>("/api/auth/logout", {
    method: "POST",
    headers: authHeaders(token, false),
  });
}

export async function loadClipPacks(token: string) {
  const payload = await jsonRequest<{ clip_packs: ClipPackSummary[] }>("/api/me/clip-packs", {
    headers: authHeaders(token, false),
  });
  return payload.clip_packs || [];
}

export async function loadClipPack(token: string, requestId: string) {
  return jsonRequest<ClipPackDetail>(`/api/me/clip-packs/${requestId}`, {
    headers: authHeaders(token, false),
  });
}

export async function patchClip(
  token: string,
  clipId: string,
  updates: {
    hook_override?: string;
    caption_override?: string;
    cta_override?: string;
    thumbnail_text_override?: string;
    packaging_angle_override?: string;
    trim_start_seconds?: number;
    trim_end_seconds?: number;
  },
) {
  return jsonRequest(`/api/me/clips/${clipId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(updates),
  });
}

export async function recoverClip(token: string, clipId: string) {
  return jsonRequest<ClipRecoveryJob>(`/api/me/clips/${clipId}/recover`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export async function loadClipRecoveryJob(token: string, jobId: string) {
  return jsonRequest<ClipRecoveryStatus>(`/api/me/recovery-jobs/${jobId}`, {
    headers: authHeaders(token, false),
  });
}

export async function retryClipRender(clipId: string, requestId?: string | null, token?: string | null) {
  const query = requestId ? `?request_id=${encodeURIComponent(requestId)}` : "";
  return jsonRequest<ClipResult>(`/api/clip-status/${encodeURIComponent(clipId)}${query}`, {
    method: "POST",
    headers: authHeaders(token, false),
  });
}

export async function loadClipRenderStatus(clipId: string, requestId?: string | null, token?: string | null) {
  const query = requestId ? `?request_id=${encodeURIComponent(requestId)}` : "";
  return jsonRequest<ClipResult>(`/api/clip-status/${encodeURIComponent(clipId)}${query}`, {
    headers: authHeaders(token, false),
  });
}

export async function loadWallet(token: string) {
  return jsonRequest<WalletSummary>("/api/wallet", {
    headers: authHeaders(token, false),
  });
}

export async function loadWalletLedger(token: string) {
  const payload = await jsonRequest<{ entries: WalletLedgerEntry[] }>("/api/wallet/ledger", {
    headers: authHeaders(token, false),
  });
  return payload.entries || [];
}

export async function createPayoutRequest(token: string, amountCents: number) {
  return jsonRequest<PayoutRequest>("/api/wallet/payout-requests", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ amount_cents: amountCents }),
  });
}

export async function loadUploads(token: string) {
  const payload = await jsonRequest<{ uploads: UploadAsset[] }>("/api/uploads", {
    headers: authHeaders(token, false),
  });
  return payload.uploads || [];
}

export async function uploadSource(file: File, token?: string | null) {
  const formData = new FormData();
  formData.append("file", file);
  return jsonRequest<UploadAsset>("/api/uploads", {
    method: "POST",
    headers: authHeaders(token, false),
    body: formData,
  });
}

export async function loadBatches(token: string) {
  const payload = await jsonRequest<{ batches: BatchSummary[] }>("/api/batches", {
    headers: authHeaders(token, false),
  });
  return payload.batches || [];
}

export async function createBatch(token: string, payload: BatchCreatePayload) {
  return jsonRequest<BatchSummary>("/api/batches", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function loadCampaigns(token: string) {
  const payload = await jsonRequest<{ campaigns: CampaignSummary[] }>("/api/campaigns", {
    headers: authHeaders(token, false),
  });
  return payload.campaigns || [];
}

export async function loadCampaign(token: string, campaignId: string) {
  return jsonRequest<CampaignDetail>(`/api/campaigns/${campaignId}`, {
    headers: authHeaders(token, false),
  });
}

export async function createCampaign(token: string, payload: CampaignCreatePayload) {
  return jsonRequest<CampaignSummary>("/api/campaigns", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateCampaign(token: string, campaignId: string, payload: CampaignUpdatePayload) {
  return jsonRequest<CampaignSummary>(`/api/campaigns/${campaignId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function createCampaignAssignments(
  token: string,
  campaignId: string,
  payload: {
    request_id?: string;
    clip_ids?: string[];
    target_platform?: string;
    packaging_angle?: string;
    assignee_role?: string;
    assignee_label?: string;
    note?: string;
    payout_amount_cents?: number;
  },
) {
  const data = await jsonRequest<{ assignments: CampaignAssignment[] }>(`/api/campaigns/${campaignId}/assignments`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
  return data.assignments || [];
}

export async function updateCampaignAssignment(
  token: string,
  campaignId: string,
  assignmentId: string,
  payload: {
    status?: string;
    assignee_role?: string;
    assignee_label?: string;
    note?: string;
    payout_amount_cents?: number;
  },
) {
  return jsonRequest<CampaignAssignment>(`/api/campaigns/${campaignId}/assignments/${assignmentId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function loadPostingConnections(token: string) {
  const payload = await jsonRequest<{ connections: PostingConnection[] }>("/api/posting/connections", {
    headers: authHeaders(token, false),
  });
  return payload.connections || [];
}

export async function createPostingConnection(token: string, payload: PostingConnectionPayload) {
  return jsonRequest<PostingConnection>("/api/posting/connections", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function loadScheduledPosts(token: string) {
  const payload = await jsonRequest<{ scheduled_posts: ScheduledPost[] }>("/api/posting/scheduled", {
    headers: authHeaders(token, false),
  });
  return payload.scheduled_posts || [];
}

export async function createScheduledPost(token: string, payload: ScheduledPostPayload) {
  return jsonRequest<ScheduledPost>("/api/posting/scheduled", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function updateScheduledPost(token: string, postId: string, payload: ScheduledPostPatchPayload) {
  return jsonRequest<ScheduledPost>(`/api/posting/scheduled/${postId}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

// Source Assets API

export interface SourceAsset {
  asset_id: string;
  user_id: string;
  asset_type: string;
  status: string;
  source_url?: string;
  source_content?: string;
  storage_provider: string;
  storage_path?: string;
  storage_url?: string;
  error_message?: string;
  metadata?: {
    filename?: string;
    file_size_bytes?: number;
    mime_type?: string;
    duration_seconds?: number;
    width?: number;
    height?: number;
    frame_rate?: number;
    sample_rate?: number;
    channels?: number;
    format?: string;
    checksum?: string;
  };
  created_at: string;
  updated_at: string;
}

export interface SourceAssetCreatePayload {
  asset_type: string;
  source_url?: string;
  source_content?: string;
  metadata?: Record<string, any>;
}

export interface SourceAssetListResponse {
  assets: SourceAsset[];
  total_count: number;
}

export async function createSourceAsset(token: string, payload: SourceAssetCreatePayload) {
  return jsonRequest<SourceAsset>("/api/source-assets", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function getSourceAsset(token: string, assetId: string) {
  return jsonRequest<SourceAsset>(`/api/source-assets/${assetId}`, {
    headers: authHeaders(token, false),
  });
}

export async function listSourceAssets(token: string) {
  const payload = await jsonRequest<SourceAssetListResponse>("/api/source-assets", {
    headers: authHeaders(token, false),
  });
  return payload;
}

export async function deleteSourceAsset(token: string, assetId: string) {
  return jsonRequest<{ message: string; asset_id: string; deleted: boolean }>(`/api/source-assets/${assetId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
}

export async function getSourceAssetTypes(token: string) {
  return jsonRequest<{
    asset_types: string[];
    descriptions: Record<string, string>;
  }>("/api/source-assets/types", {
    headers: authHeaders(token, false),
  });
}

export async function getSourceAssetStats(token: string) {
  return jsonRequest<{
    total_assets: number;
    by_type: Record<string, number>;
    by_status: Record<string, number>;
    storage_provider: string;
    metadata_only: boolean;
  }>("/api/source-assets/stats", {
    headers: authHeaders(token, false),
  });
}

export async function createSourceAssetsBatch(token: string, payloads: SourceAssetCreatePayload[]) {
  return jsonRequest<SourceAssetListResponse>("/api/source-assets/batch", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(payloads),
  });
}

// Marketplace API helpers
export async function getMarketplaceProducts(limit = 50, offset = 0, category?: string) {
  return jsonRequest<{
    success: boolean;
    products: Array<{
      id: string;
      name: string;
      description: string;
      product_type: string;
      price: number;
      creator_name: string;
      status: string;
      created_at: string;
      download_count: number;
      rating: number;
      review_count: number;
      preview_url?: string;
      asset_urls: string[];
    }>;
  }>(`/api/v1/marketplace/products?limit=${limit}&offset=${offset}${category ? `&category=${category}` : ''}`);
}

export async function getMarketplaceJobs(limit = 50, offset = 0, status?: string) {
  return jsonRequest<{
    success: boolean;
    jobs: Array<{
      id: string;
      title: string;
      description: string;
      campaign_type: string;
      budget: number;
      status: string;
      created_at: string;
      deadline?: string;
      requirements: string[];
      applicant_count: number;
      creator_profile?: {
        display_name: string;
        rating: number;
      };
    }>;
  }>(`/api/v1/marketplace/jobs?limit=${limit}&offset=${offset}${status ? `&status=${status}` : ''}`);
}

export async function getMarketplaceProfiles(limit = 50, offset = 0) {
  return jsonRequest<{
    success: boolean;
    profiles: Array<{
      id: string;
      display_name: string;
      bio: string;
      specialties: string[];
      rating: number;
      completed_jobs: number;
      earnings: {
        approved: number;
        pending: number;
      };
      status: string;
    }>;
  }>(`/api/v1/marketplace/profiles?limit=${limit}&offset=${offset}`);
}

// Campaign Export API helpers
export async function getCampaigns(limit = 50, offset = 0) {
  return jsonRequest<{
    success: boolean;
    campaigns: Array<{
      id: string;
      name: string;
      description: string;
      platforms: string[];
      status: string;
      created_at: string;
      total_clips: number;
      exported_clips: number;
      export_settings: {
        formats: string[];
        quality: string;
        include_captions: boolean;
        include_thumbnails: boolean;
      };
    }>;
  }>(`/api/v1/campaign-export/campaigns?limit=${limit}&offset=${offset}`);
}

export async function getExportPackages(limit = 50, offset = 0) {
  return jsonRequest<{
    success: boolean;
    packages: Array<{
      id: string;
      campaign_id: string;
      package_name: string;
      status: string;
      created_at: string;
      completed_at?: string;
      file_count: number;
      total_size: number;
      download_url?: string;
      formats: string[];
      quality: string;
    }>;
  }>(`/api/v1/campaign-export/packages?limit=${limit}&offset=${offset}`);
}

// Feedback Learning API helpers
export async function getFeedbackInsights(limit = 50, offset = 0, campaignId?: string) {
  return jsonRequest<{
    success: boolean;
    insights: Array<{
      id: string;
      campaign_id?: string;
      insight_type: string;
      title: string;
      description: string;
      confidence_score: number;
      impact_level: string;
      created_at: string;
      applied: boolean;
      recommendations: string[];
    }>;
  }>(`/api/v1/feedback-learning/insights?limit=${limit}&offset=${offset}${campaignId ? `&campaign_id=${campaignId}` : ''}`);
}

export async function getLearningMetrics() {
  return jsonRequest<{
    success: boolean;
    metrics: Array<{
      metric_name: string;
      current_value: number;
      previous_value: number;
      change_percentage: number;
      trend: string;
      last_updated: string;
    }>;
  }>("/api/v1/feedback-learning/metrics");
}

// Safety API helpers
export async function runSafetyCheck(contentType: string, contentData: any, platform: string) {
  return jsonRequest<{
    success: boolean;
    safety: {
      overall_safe: boolean;
      safety_score: number;
      issues: any[];
      warnings: any[];
      recommendations: string[];
    };
    rights?: {
      rights_clear: boolean;
      rights_score: number;
      issues: any[];
      warnings: any[];
      clearance_status: string;
      attribution_required: boolean;
    };
    cost?: {
      estimated_cost: number;
      cost_breakdown: {
        rendering: number;
        storage: number;
        bandwidth: number;
        platform_fees: number;
      };
      cost_factors: string[];
    };
  }>("/api/v1/safety/check", {
    method: "POST",
    body: JSON.stringify({
      content_type: contentType,
      content_data: contentData,
      platform: platform,
      check_rights: true,
      check_cost: true
    }),
  });
}

// Caption API helpers
export async function generateCaptions(videoId: string, language = "en", style = "standard") {
  return jsonRequest<{
    success: boolean;
    video_id: string;
    language: string;
    style: string;
    captions: Array<{
      id: string;
      start_time: number;
      end_time: number;
      text: string;
      confidence: number;
    }>;
    total_duration: number;
    caption_count: number;
    generated_at: string;
  }>("/api/v1/captions/generate", {
    method: "POST",
    body: JSON.stringify({
      video_id: videoId,
      language: language,
      style: style,
      include_timestamps: true,
      max_line_length: 42
    }),
  });
}

export async function getVideoCaptions(videoId: string, language = "en") {
  return jsonRequest<{
    success: boolean;
    video_id: string;
    language: string;
    captions: Array<{
      id: string;
      start_time: number;
      end_time: number;
      text: string;
      style: string;
      language: string;
    }>;
  }>(`/api/v1/captions/videos/${videoId}/captions?language=${language}`);
}

// Audio API helpers
export async function generateAudio(videoId: string, audioType: string, style: string, mood = "energetic") {
  return jsonRequest<{
    success: boolean;
    video_id: string;
    audio_type: string;
    segments: Array<{
      id: string;
      type: string;
      start_time: number;
      end_time: number;
      style: string;
      mood: string;
      volume: number;
      file_url: string;
      duration: number;
    }>;
    total_duration: number;
    generated_at: string;
  }>("/api/v1/audio/generate", {
    method: "POST",
    body: JSON.stringify({
      video_id: videoId,
      audio_type: audioType,
      style: style,
      mood: mood,
      volume: 0.8
    }),
  });
}

export async function generateMusic(videoId: string, genre: string, mood = "upbeat", intensity = "medium") {
  return jsonRequest<{
    success: boolean;
    music_track: {
      id: string;
      video_id: string;
      genre: string;
      tempo: number;
      mood: string;
      intensity: string;
      duration: number;
      file_url: string;
      waveform_url: string;
      instruments: string[];
      key_signature: string;
      time_signature: string;
      generated_at: string;
    };
  }>("/api/v1/audio/music/generate", {
    method: "POST",
    body: JSON.stringify({
      video_id: videoId,
      genre: genre,
      mood: mood,
      intensity: intensity
    }),
  });
}

export async function synthesizeVoice(text: string, voiceType: string, emotion = "neutral") {
  return jsonRequest<{
    success: boolean;
    voice_audio: {
      id: string;
      text: string;
      voice_type: string;
      speed: number;
      pitch: number;
      emotion: string;
      duration: number;
      file_url: string;
      sample_rate: number;
      bitrate: number;
      synthesized_at: string;
    };
  }>("/api/v1/audio/voice/synthesize", {
    method: "POST",
    body: JSON.stringify({
      text: text,
      voice_type: voiceType,
      speed: 1.0,
      pitch: 1.0,
      emotion: emotion
    }),
  });
}

// =========================
// SLICE 9: PROOF VAULT + STYLE MEMORY API
// =========================

export type ProofAssetPayload = {
  asset_type: "clip" | "hook" | "caption" | "thumbnail" | "full_video" | "campaign";
  source_url?: string | null;
  clip_url?: string | null;
  hook_text?: string | null;
  caption_text?: string | null;
  platform?: string | null;
  duration_seconds?: number | null;
  ai_score?: number | null;
  style_tags?: string[];
  project_id?: string | null;
};

export async function saveProofAsset(payload: ProofAssetPayload) {
  return jsonRequest<{ success: boolean; asset: unknown; message: string }>("/api/v1/proof-vault/assets", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateProofAssetStatus(
  proofId: string,
  payload: {
    status?: "winning" | "rejected" | "pending" | "archived";
    performance_notes?: Record<string, unknown>;
    style_tags?: string[];
    rejected_reason?: string;
    approved_by?: string;
  },
) {
  return jsonRequest<{ success: boolean; asset: unknown; message: string }>(
    `/api/v1/proof-vault/assets/${encodeURIComponent(proofId)}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
}

export async function submitClipStyleFeedback(payload: {
  clip_id: string;
  approved: boolean;
  feedback_notes?: string;
  style_tags?: string[];
}) {
  const params = new URLSearchParams({ clip_id: payload.clip_id, approved: String(payload.approved) });
  if (payload.feedback_notes) params.set("feedback_notes", payload.feedback_notes);
  for (const tag of payload.style_tags || []) params.append("style_tags", tag);

  return jsonRequest<{ success: boolean; message: string; learnings?: string[] }>(
    `/api/v1/style-memory/learn/clip-feedback?${params.toString()}`,
    {
      method: "POST",
    },
  );
}

// =========================
// DIRECTOR BRAIN ML API
// =========================

export type DirectorBrainContentType =
  | "hook"
  | "caption"
  | "title"
  | "offer"
  | "description"
  | "clip_summary"
  | "opportunity"
  | "campaign_angle";

export type DirectorBrainGoal = "engagement" | "conversion" | "viral" | "personal" | "balanced";

export type DirectorBrainScoreRequest = {
  text: string;
  content_type?: DirectorBrainContentType;
  platform?: string | null;
  goal?: DirectorBrainGoal;
  style_memory?: Record<string, unknown> | null;
  proof_signals?: Record<string, unknown> | null;
};

export type DirectorBrainScoreResponse = {
  success: boolean;
  text: string;
  content_type: DirectorBrainContentType;
  platform: string;
  goal: DirectorBrainGoal;
  score: number;
  component_scores: {
    viral_hook_strength: number;
    retention_engagement: number;
    conversion_offer_fit: number;
    user_style_preference: number;
    proof_history_signal: number;
  };
  reasons: string[];
  lee_wuh_recommendation: string;
  suggested_improvement: string;
  confidence: number;
  mode: string;
  algorithm_version: string;
};

export async function scoreDirectorBrain(request: DirectorBrainScoreRequest) {
  return jsonRequest<DirectorBrainScoreResponse>("/api/v1/director-brain/score", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export type DirectorBrainRankRequest = {
  candidates: string[];
  content_type?: DirectorBrainContentType;
  platform?: string | null;
  goal?: DirectorBrainGoal;
  style_memory?: Record<string, unknown> | null;
  proof_signals?: Record<string, unknown> | null;
};

export type DirectorBrainRankResponse = {
  success: boolean;
  ranked_candidates: (DirectorBrainScoreResponse & { rank: number; post_rank: number })[];
  best_candidate: (DirectorBrainScoreResponse & { rank: number; post_rank: number }) | null;
  count: number;
  mode: string;
};

export async function rankDirectorBrain(request: DirectorBrainRankRequest) {
  return jsonRequest<DirectorBrainRankResponse>("/api/v1/director-brain/rank", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export type DirectorBrainLearnRequest = {
  text: string;
  label?: "winning" | "rejected" | "neutral";
  signal_type?: "save" | "share" | "click" | "export" | "purchase" | "manual_feedback";
  weight?: number;
  metadata?: Record<string, unknown> | null;
};

export type DirectorBrainLearnResponse = {
  success: boolean;
  event: {
    id: string;
    text: string;
    label: string;
    signal_type: string;
    weight: number;
    metadata: Record<string, unknown>;
    created_at: string;
  };
  message: string;
};

export async function learnDirectorBrain(request: DirectorBrainLearnRequest) {
  return jsonRequest<DirectorBrainLearnResponse>("/api/v1/director-brain/learn", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export type DirectorBrainStatusResponse = {
  success: boolean;
  mode: string;
  algorithm_version: string;
  learning_event_count: number;
  weights: {
    viral_hook_strength: number;
    retention_engagement: number;
    conversion_offer_fit: number;
    user_style_preference: number;
    proof_history_signal: number;
  };
  supported_content_types: DirectorBrainContentType[];
  supported_goals: DirectorBrainGoal[];
  live_paid_providers_enabled: boolean;
  binary_model_required: boolean;
};

export async function getDirectorBrainStatus() {
  return jsonRequest<DirectorBrainStatusResponse>("/api/v1/director-brain/status");
}

// =========================
// DETERMINISTIC TEXT GENERATION API (No AI Required)
// =========================

export type TextGenerateRequest = {
  text: string;
  campaign_goal?: string | null;
  target_platforms?: string[];
  min_clips?: number;
};

export type DeterministicClip = {
  clip_id: string;
  hook: string;
  caption: string;
  text: string;
  ai_score: number;
  why_this_matters: string;
  cta: string;
  thumbnail_text: string;
  duration_seconds: number;
  render_status: string;
};

export type TextGenerateResponse = {
  success: boolean;
  job_id: string;
  clips: DeterministicClip[];
  source_type: string;
  clips_generated: number;
  strategy_only: boolean;
};

/**
 * Generate clips from plain text using deterministic heuristics.
 * NO AI APIs required - fully offline, always returns results.
 */
export async function generateFromText(request: TextGenerateRequest) {
  return jsonRequest<TextGenerateResponse>("/api/v1/generate-text", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

// =========================
// EVENT TRACKING API
// =========================

export type LwaEventType =
  | "clip_view"
  | "clip_play"
  | "clip_save"
  | "clip_share"
  | "clip_export"
  | "clip_vote_good"
  | "clip_vote_bad"
  | "clip_queue"
  | "clip_recover"
  | "hook_copy"
  | "caption_copy"
  | "cta_copy"
  | "package_copy"
  | "proof_save"
  | "style_feedback"
  | "generate_start"
  | "generate_complete"
  | "generate_error"
  | "page_view"
  | "feature_click"
  | "error";

export type TrackEventRequest = {
  event_type: LwaEventType;
  clip_id?: string | null;
  source_id?: string | null;
  metadata?: Record<string, unknown>;
  source?: "web" | "api" | "ios" | "extension" | "widget";
  session_id?: string | null;
};

export type TrackEventResponse = {
  success: boolean;
  event_id: string;
  message: string;
};

export async function trackLwaEvent(request: TrackEventRequest) {
  return jsonRequest<TrackEventResponse>("/api/v1/events/track", {
    method: "POST",
    body: JSON.stringify({
      ...request,
      source: request.source || "web",
    }),
  });
}

export type BatchTrackRequest = {
  events: TrackEventRequest[];
};

export type BatchTrackResponse = {
  success: boolean;
  tracked_count: number;
  failed_count: number;
  event_ids: string[];
};

export async function trackLwaEventsBatch(request: BatchTrackRequest) {
  return jsonRequest<BatchTrackResponse>("/api/v1/events/batch", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export type EventStatusResponse = {
  success: boolean;
  event_tracking_enabled: boolean;
  supported_event_types: LwaEventType[];
  supported_sources: string[];
};

export async function getEventTrackingStatus() {
  return jsonRequest<EventStatusResponse>("/api/v1/events/status");
}

// =========================
// ENTITLEMENT / CREDITS API
// =========================

export type FeatureCost = {
  clip_generation: number;
  campaign_export: number;
  proof_vault_save: number;
  style_feedback: number;
  director_brain_score: number;
  video_render: number;
  caption_export: number;
  bulk_operation: number;
};

export type EntitlementCheckRequest = {
  feature: string;
};

export type EntitlementCheckResponse = {
  success: boolean;
  user_id: string;
  feature: string;
  cost: number;
  has_access: boolean;
  credits_required: number;
  credits_available: number;
  credits_after: number;
  unlocked: boolean;
  free_mode_active: boolean;
  message: string;
};

export async function checkEntitlement(feature: string) {
  return jsonRequest<EntitlementCheckResponse>("/api/v1/entitlements/check", {
    method: "POST",
    body: JSON.stringify({ feature }),
  });
}

export type SpendCreditRequest = {
  feature: string;
  description?: string;
};

export type SpendCreditResponse = {
  success: boolean;
  user_id: string;
  feature: string;
  cost: number;
  credits_remaining: number;
  credits_spent: number;
  free_mode: boolean;
  transaction_id: string;
  message: string;
};

export async function spendCredit(request: SpendCreditRequest) {
  return jsonRequest<SpendCreditResponse>("/api/v1/entitlements/spend", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export type EntitlementStatusResponse = {
  success: boolean;
  user_id: string;
  credits: {
    remaining: number;
    total_ever: number;
  };
  unlocked_features: string[];
  free_mode_active: boolean;
  feature_costs: FeatureCost;
  recent_transactions: {
    id: string;
    amount: number;
    type: string;
    feature: string;
    description: string;
    created_at: string;
  }[];
};

export async function getEntitlementStatus() {
  return jsonRequest<EntitlementStatusResponse>("/api/v1/entitlements/status");
}

export async function getFeatureCosts() {
  return jsonRequest<{ success: boolean; feature_costs: FeatureCost; free_mode_active: boolean }>(
    "/api/v1/entitlements/feature-costs"
  );
}

// =========================
// DEMO MODE API
// =========================

export type DemoSourceResponse = {
  success: boolean;
  source: {
    id: string;
    title: string;
    description: string;
    duration_seconds: number;
    type: string;
    is_demo: boolean;
    clips_available: number;
  };
  message: string;
};

export async function getDemoSource() {
  return jsonRequest<DemoSourceResponse>("/api/v1/demo/source");
}

export type DemoClip = {
  clip_id: string;
  title: string;
  hook: string;
  caption: string;
  timestamp_start: number;
  timestamp_end: number;
  score: number;
  campaign_role: string;
  funnel_stage: string;
  suggested_cta: string;
  why_this_matters: string;
  is_demo: boolean;
  strategy_only: boolean;
  render_status: string;
};

export type DemoClipsResponse = {
  success: boolean;
  clips: DemoClip[];
  count: number;
  source_id: string;
  is_demo: boolean;
  message: string;
};

export async function getDemoClips() {
  return jsonRequest<DemoClipsResponse>("/api/v1/demo/clips");
}

export type DemoCampaignResponse = {
  success: boolean;
  campaign: {
    id: string;
    name: string;
    source_id: string;
    created_at: string;
    clips: DemoClip[];
    posting_schedule: {
      day: number;
      clip_id: string;
      platform: string;
      time: string;
    }[];
    bundle_contents: {
      hooks: string[];
      captions: string[];
      timestamps: {
        clip_id: string;
        start: number;
        end: number;
      }[];
      ctas: string[];
    };
    is_demo: boolean;
  };
  message: string;
};

export async function getDemoCampaign() {
  return jsonRequest<DemoCampaignResponse>("/api/v1/demo/campaign");
}

export type DemoSaveProofResponse = {
  success: boolean;
  user_id: string;
  saved_assets: {
    asset_id: string;
    asset_type: string;
    clip_id: string;
    hook_text: string;
    caption_text: string;
    ai_score: number;
    campaign_role: string;
    is_demo: boolean;
    saved_at: string;
  }[];
  count: number;
  message: string;
};

export async function saveDemoProof() {
  return jsonRequest<DemoSaveProofResponse>("/api/v1/demo/save-proof", {
    method: "POST",
  });
}

export type DemoStatusResponse = {
  success: boolean;
  demo_mode_enabled: boolean;
  sample_source_available: boolean;
  sample_clips_count: number;
  features: string[];
  limitations: string[];
};

export async function getDemoStatus() {
  return jsonRequest<DemoStatusResponse>("/api/v1/demo/status");
}

// =========================
// ADMIN / OPS API
// =========================

export type RecentEvent = {
  event_id: string;
  event_type: string;
  timestamp: string;
  clip_id?: string | null;
  source_id?: string | null;
  user_id?: string | null;
  metadata: Record<string, unknown>;
};

export type RecentEventsResponse = {
  success: boolean;
  events: RecentEvent[];
  count: number;
  time_range_minutes: number;
};

export async function getRecentLwaEvents(
  minutes: number = 60,
  event_type?: string | null,
  limit: number = 100
) {
  const params = new URLSearchParams();
  params.append("minutes", minutes.toString());
  params.append("limit", limit.toString());
  if (event_type) params.append("event_type", event_type);
  
  return jsonRequest<RecentEventsResponse>(`/api/v1/admin/events/recent?${params.toString()}`);
}

export type SystemMetric = {
  metric_name: string;
  value: number;
  unit: string;
  timestamp: string;
};

export type SystemMetricsResponse = {
  success: boolean;
  metrics: SystemMetric[];
  generated_at: string;
};

export async function getAdminMetrics() {
  return jsonRequest<SystemMetricsResponse>("/api/v1/admin/metrics");
}

export type OperatorStatusResponse = {
  success: boolean;
  system_healthy: boolean;
  event_tracking_enabled: boolean;
  recent_event_count: number;
  api_status: string;
  last_error?: string | null;
  checked_at: string;
};

export async function getAdminOpsStatus() {
  return jsonRequest<OperatorStatusResponse>("/api/v1/admin/status");
}

// =========================
// COMMAND CENTER API
// =========================

export type WorldProfileSummary = {
  display_name: string;
  class_name: string;
  faction: string;
  level: number;
  xp: number;
  next_level_xp: number;
  badges: string[];
  relics: string[];
};

export type CommandCenterCampaignSummary = {
  total_count: number;
  open_count: number;
  review_ready_count: number;
};

export type CommandCenterEarningsSummary = {
  approved_cents: number;
  pending_review_cents: number;
  available_cents: number;
  eligible_payout_cents: number;
};

export type CommandCenterSummaryResponse = {
  success: boolean;
  world: WorldProfileSummary;
  campaigns: CommandCenterCampaignSummary;
  earnings: CommandCenterEarningsSummary;
  generated_at: string;
};

export async function getCommandCenterSummary() {
  return jsonRequest<CommandCenterSummaryResponse>("/api/v1/command-center/summary");
}

// =========================
// BULK OPERATIONS API
// =========================

export type BulkApproveRequest = {
  clip_ids: string[];
};

export type BulkApproveResponse = {
  success: boolean;
  approved_count: number;
  failed_count: number;
  approved_ids: string[];
  failed_ids: string[];
  message: string;
};

export async function bulkApproveClips(request: BulkApproveRequest) {
  return jsonRequest<BulkApproveResponse>("/api/v1/clips/bulk-approve", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export type BulkRejectRequest = {
  clip_ids: string[];
  reason?: string;
};

export type BulkRejectResponse = {
  success: boolean;
  rejected_count: number;
  failed_count: number;
  rejected_ids: string[];
  failed_ids: string[];
  message: string;
};

export async function bulkRejectClips(request: BulkRejectRequest) {
  return jsonRequest<BulkRejectResponse>("/api/v1/clips/bulk-reject", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export type BulkExportRequest = {
  clip_ids: string[];
  format?: "json" | "csv" | "txt";
};

export type BulkExportResponse = {
  success: boolean;
  export_url?: string;
  bundle?: {
    clips: Array<{
      clip_id: string;
      hook: string;
      caption: string;
      timestamp_start: number;
      timestamp_end: number;
      platform: string;
    }>;
    generated_at: string;
  };
  message: string;
};

export async function bulkExportClips(request: BulkExportRequest) {
  return jsonRequest<BulkExportResponse>("/api/v1/clips/bulk-export", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

// =========================
// CLIPS LIST API
// =========================

export type ClipItem = {
  clip_id: string;
  hook: string;
  caption: string;
  duration: number;
  ai_score: number;
  status: "pending" | "approved" | "rejected" | "edited";
  platform: string;
  source_url?: string | null;
  thumbnail_url?: string | null;
  created_at: string;
  updated_at: string;
};

export type ClipListResponse = {
  success: boolean;
  clips: ClipItem[];
  count: number;
  total_count: number;
};

export async function listClips(
  status?: string | null,
  platform?: string | null,
  limit: number = 50,
  offset: number = 0
) {
  const params = new URLSearchParams();
  if (status) params.append("status", status);
  if (platform) params.append("platform", platform);
  params.append("limit", limit.toString());
  params.append("offset", offset.toString());
  
  return jsonRequest<ClipListResponse>(`/api/v1/clips?${params.toString()}`);
}

// =========================
// VIDEO OS API
// =========================

export type VideoJob = {
  job_id: string;
  user_id: string;
  job_type: string;
  provider: string;
  status: string;
  prompt?: string | null;
  input_urls: string[];
  source_asset_ids: string[];
  aspect_ratio: string;
  duration_seconds: number;
  resolution: string;
  style_preset?: string | null;
  cost_estimate_usd: number;
  progress: number;
  preview_url?: string | null;
  output_url?: string | null;
  thumbnail_url?: string | null;
  error_message?: string | null;
  timeline_plan?: {
    id: string;
    title: string;
    aspect_ratio: string;
    duration_seconds: number;
    track_count: number;
  } | null;
  created_at: string;
  updated_at: string;
};

export type VideoJobListResponse = {
  jobs: VideoJob[];
};

export async function getVideoJobs() {
  return jsonRequest<VideoJobListResponse>("/api/v1/video-jobs");
}

export async function getSourceAssets() {
  return jsonRequest<SourceAssetListResponse>("/api/v1/source-assets");
}

