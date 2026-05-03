type DirectorBrainContentType =
  | "hook"
  | "caption"
  | "title"
  | "offer"
  | "description"
  | "clip_summary"
  | "opportunity"
  | "campaign_angle";

type DirectorBrainGoal = "engagement" | "conversion" | "viral" | "personal" | "balanced";
type DirectorBrainLearningLabel = "winning" | "rejected" | "neutral";
type DirectorBrainSignalType = "save" | "share" | "click" | "export" | "purchase" | "manual_feedback";

export type DirectorBrainScoreRequest = {
  text: string;
  content_type?: DirectorBrainContentType;
  platform?: string;
  goal?: DirectorBrainGoal;
  style_memory?: Record<string, unknown>;
  proof_signals?: Record<string, unknown>;
};

export type DirectorBrainRankRequest = {
  candidates: string[];
  content_type?: DirectorBrainContentType;
  platform?: string;
  goal?: DirectorBrainGoal;
  style_memory?: Record<string, unknown>;
  proof_signals?: Record<string, unknown>;
};

export type DirectorBrainLearnRequest = {
  text: string;
  label?: DirectorBrainLearningLabel;
  signal_type?: DirectorBrainSignalType;
  weight?: number;
  metadata?: Record<string, unknown>;
};

export type DirectorBrainScoreResponse = {
  success: boolean;
  text: string;
  content_type: DirectorBrainContentType;
  platform: string;
  goal: DirectorBrainGoal;
  score: number;
  component_scores: Record<string, number>;
  reasons: string[];
  lee_wuh_recommendation: string;
  suggested_improvement: string;
  confidence: number;
  mode: string;
  algorithm_version: string;
  rank?: number;
  post_rank?: number;
};

export type DirectorBrainRankResponse = {
  success: boolean;
  ranked_candidates: DirectorBrainScoreResponse[];
  best_candidate: DirectorBrainScoreResponse | null;
  count: number;
  mode: string;
};

export type DirectorBrainStatusResponse = {
  success: boolean;
  mode: string;
  algorithm_version: string;
  learning_event_count: number;
  weights: Record<string, number>;
  supported_content_types: DirectorBrainContentType[];
  supported_goals: DirectorBrainGoal[];
  live_paid_providers_enabled: boolean;
  binary_model_required: boolean;
};

async function directorBrainRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : {};

  if (!response.ok) {
    const message = data?.detail || data?.message || "Director Brain request failed.";
    throw new Error(String(message));
  }

  return data as T;
}

export function scoreDirectorBrainText(payload: DirectorBrainScoreRequest) {
  return directorBrainRequest<DirectorBrainScoreResponse>("/api/v1/director-brain/score", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function rankDirectorBrainCandidates(payload: DirectorBrainRankRequest) {
  return directorBrainRequest<DirectorBrainRankResponse>("/api/v1/director-brain/rank", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function submitDirectorBrainLearningEvent(payload: DirectorBrainLearnRequest) {
  return directorBrainRequest<{ success: boolean; event: Record<string, unknown>; message: string }>(
    "/api/v1/director-brain/learn",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function getDirectorBrainStatus() {
  return directorBrainRequest<DirectorBrainStatusResponse>("/api/v1/director-brain/status");
}
