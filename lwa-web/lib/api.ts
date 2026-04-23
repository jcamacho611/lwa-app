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

async function jsonRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, init);
  const data = (await response.json()) as T & { detail?: string; error?: string };

  if (!response.ok) {
    throw new ApiError(data.detail || data.error || "Request failed.", response.status);
  }

  return data;
}

function authHeaders(token?: string | null, contentType = true) {
  return {
    ...(contentType ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

function normalizeUrl(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return trimmed;
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  if (trimmed.startsWith("//")) return `https:${trimmed}`;
  return `https://${trimmed}`;
}

export async function generateClips(payload: GeneratePayload, token?: string | null): Promise<GenerateResponse> {
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
