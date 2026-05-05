"use client";

// API client for LWA backend
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface IngestRequest {
  source_url: string;
  description?: string;
}

interface IngestResponse {
  request_id: string;
  status: string;
  message: string;
}

interface ProcessingStatus {
  request_id: string;
  stage: "ingest" | "cutting" | "analyzing" | "complete";
  progress: number;
  clips_ready: number;
  total_clips: number;
}

interface Segment {
  start: number;
  end: number;
  type: "kept" | "removed" | "suggested";
}

interface Clip {
  clip_id: string;
  preview_url?: string;
  segments: Segment[];
  hook: string;
  caption: string;
  cta: string;
  virality_score: number;
  thumbnail_text: string;
  platform_tags: string[];
  render_status: "strategy_only" | "rendered";
}

interface ClipPack {
  pack_id: string;
  request_id: string;
  clips: Clip[];
  best_clip_id?: string;
  total_duration: number;
  created_at: string;
}

interface VariantRequest {
  request_id: string;
  variant_type: "reorder" | "new_hook" | "length";
  count: number;
}

interface ExportRequest {
  request_id: string;
  pack_id: string;
  format: "mp4" | "json" | "markdown";
}

interface ExportResponse {
  download_url?: string;
  markdown_content?: string;
}

// Error handling wrapper
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

// Ingest video
export async function ingestVideo(data: IngestRequest): Promise<IngestResponse> {
  return fetchApi<IngestResponse>("/api/ingest", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// Get processing status
export async function getProcessingStatus(requestId: string): Promise<ProcessingStatus> {
  return fetchApi<ProcessingStatus>(`/api/status/${requestId}`);
}

// Process video (start cutting/analysis)
export async function processVideo(
  requestId: string,
  useAi: boolean = false
): Promise<{ request_id: string; status: string; clips: Clip[]; strategy_only: boolean }> {
  return fetchApi(`/api/process/${requestId}?use_ai=${useAi}`, {
    method: "POST",
  });
}

// Get clips for a request
export async function getClips(requestId: string): Promise<Clip[]> {
  return fetchApi<Clip[]>(`/api/clips/${requestId}`);
}

// Generate variants
export async function generateVariants(
  requestId: string,
  data: Omit<VariantRequest, "request_id">
): Promise<{ variants: ClipPack[] }> {
  return fetchApi(`/api/variants/${requestId}`, {
    method: "POST",
    body: JSON.stringify({ ...data, request_id: requestId }),
  });
}

// Export clips
export async function exportClips(
  requestId: string,
  data: Omit<ExportRequest, "request_id">
): Promise<ExportResponse> {
  return fetchApi(`/api/export/${requestId}`, {
    method: "POST",
    body: JSON.stringify({ ...data, request_id: requestId }),
  });
}

// Polling helper for status
export function pollStatus(
  requestId: string,
  onUpdate: (_status: ProcessingStatus) => void,
  onComplete?: (_status: ProcessingStatus) => void,
  intervalMs: number = 2000
): () => void {
  let isActive = true;
  
  const poll = async () => {
    if (!isActive) return;
    
    try {
      const _status = await getProcessingStatus(requestId);
      onUpdate(_status);
      
      if (_status.stage === "complete") {
        onComplete?.(_status);
        return;
      }
      
      setTimeout(poll, intervalMs);
    } catch (error) {
      console.error("Polling error:", error);
      setTimeout(poll, intervalMs * 2); // Back off on error
    }
  };
  
  poll();
  
  // Return cleanup function
  return () => {
    isActive = false;
  };
}

export type {
  IngestRequest,
  IngestResponse,
  ProcessingStatus,
  Segment,
  Clip,
  ClipPack,
  VariantRequest,
  ExportRequest,
  ExportResponse,
};
