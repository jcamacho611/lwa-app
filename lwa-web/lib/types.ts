export type PlatformCode = "TikTok" | "Instagram" | "YouTube";

export type ClipResult = {
  id: string;
  title: string;
  hook: string;
  caption: string;
  score: number;
  confidence?: number | null;
  reason?: string | null;
  start_time: string;
  end_time: string;
  cta_suggestion?: string | null;
  platform_fit?: string | null;
  packaging_angle?: string | null;
  thumbnail_text?: string | null;
  clip_url?: string | null;
  edited_clip_url?: string | null;
  preview_image_url?: string | null;
};

export type ClipResponse = {
  request_id: string;
  video_url: string;
  status: string;
  source_platform: string;
  clips: ClipResult[];
  processing_summary?: {
    plan_name: string;
    ai_provider: string;
    target_platform: string;
    estimated_turnaround: string;
    recommended_next_step: string;
    edited_assets_created: number;
  };
};

export type GenerateState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: ClipResponse }
  | { status: "error"; message: string };
