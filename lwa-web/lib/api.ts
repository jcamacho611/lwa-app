import {
  AuthResponse,
  BatchSummary,
  CampaignSummary,
  ClipPackDetail,
  ClipPackSummary,
  GenerateResponse,
  PlatformOption,
  UploadAsset,
  UserProfile,
  WalletSummary,
} from "./types";

type GeneratePayload = {
  url?: string;
  platform: PlatformOption;
  uploadFileId?: string;
};

async function jsonRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, init);
  const data = (await response.json()) as T & { detail?: string; error?: string };

  if (!response.ok) {
    throw new Error(data.detail || data.error || "Request failed.");
  }

  return data;
}

export async function generateClips(payload: GeneratePayload, token?: string | null): Promise<GenerateResponse> {
  return jsonRequest<GenerateResponse>("/api/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  });
}

export async function signUp(email: string, password: string) {
  return jsonRequest<AuthResponse>("/api/auth/signup", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });
}

export async function logIn(email: string, password: string) {
  return jsonRequest<AuthResponse>("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });
}

export async function loadMe(token: string) {
  return jsonRequest<UserProfile>("/api/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function logOut(token: string) {
  return jsonRequest<{ status: string; message: string }>("/api/auth/logout", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function loadClipPacks(token: string) {
  const payload = await jsonRequest<{ clip_packs: ClipPackSummary[] }>("/api/me/clip-packs", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return payload.clip_packs || [];
}

export async function loadClipPack(token: string, requestId: string) {
  return jsonRequest<ClipPackDetail>(`/api/me/clip-packs/${requestId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
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
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(updates),
  });
}

export async function loadWallet(token: string) {
  return jsonRequest<WalletSummary>("/api/wallet", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function loadUploads(token: string) {
  const payload = await jsonRequest<{ uploads: UploadAsset[] }>("/api/uploads", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return payload.uploads || [];
}

export async function loadBatches(token: string) {
  const payload = await jsonRequest<{ batches: BatchSummary[] }>("/api/batches", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return payload.batches || [];
}

export async function loadCampaigns(token: string) {
  const payload = await jsonRequest<{ campaigns: CampaignSummary[] }>("/api/campaigns", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return payload.campaigns || [];
}

export async function uploadSource(file: File, token: string) {
  const formData = new FormData();
  formData.append("file", file);
  return jsonRequest<UploadAsset>("/api/uploads", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });
}
