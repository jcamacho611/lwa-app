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
