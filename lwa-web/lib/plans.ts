import type { FeatureFlags } from "./types";

export type KnownPlanCode = "free" | "pro" | "scale";

type PlanSurface = {
  code: KnownPlanCode;
  name: string;
  watermark: boolean;
  featureFlags: FeatureFlags;
};

const PLAN_SURFACES: Record<KnownPlanCode, PlanSurface> = {
  free: {
    code: "free",
    name: "Guest access",
    watermark: true,
    featureFlags: {
      clip_limit: 3,
      alt_hooks: false,
      campaign_mode: false,
      packaging_profiles: false,
      history_limit: 10,
      caption_editor: false,
      timeline_editor: false,
      wallet_view: false,
      posting_queue: false,
      max_uploads_per_day: 2,
      max_generations_per_day: 2,
      premium_exports: false,
      priority_processing: false,
    },
  },
  pro: {
    code: "pro",
    name: "Pro",
    watermark: false,
    featureFlags: {
      clip_limit: 20,
      alt_hooks: true,
      campaign_mode: false,
      packaging_profiles: true,
      history_limit: 25,
      caption_editor: true,
      timeline_editor: true,
      wallet_view: true,
      posting_queue: false,
      max_uploads_per_day: 25,
      max_generations_per_day: 25,
      premium_exports: true,
      priority_processing: true,
    },
  },
  scale: {
    code: "scale",
    name: "Scale",
    watermark: false,
    featureFlags: {
      clip_limit: 40,
      alt_hooks: true,
      campaign_mode: true,
      packaging_profiles: true,
      history_limit: 100,
      caption_editor: true,
      timeline_editor: true,
      wallet_view: true,
      posting_queue: true,
      max_uploads_per_day: 100,
      max_generations_per_day: 100,
      premium_exports: true,
      priority_processing: true,
    },
  },
};

export function normalizePlanCode(planCode?: string | null): KnownPlanCode {
  const normalized = (planCode || "free").trim().toLowerCase();
  if (normalized === "scale") {
    return "scale";
  }
  if (normalized === "pro") {
    return "pro";
  }
  return "free";
}

export function getPlanSurface(planCode?: string | null, overrides?: FeatureFlags): PlanSurface {
  const code = normalizePlanCode(planCode);
  const base = PLAN_SURFACES[code];

  return {
    ...base,
    featureFlags: {
      ...base.featureFlags,
      ...(overrides || {}),
    },
  };
}
