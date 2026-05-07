/**
 * lwa-engine-deploy-order
 *
 * Recommended Railway deploy order for the 10 backend engines.
 * Mirrors `docs/deployment/LWA_RAILWAY_ENGINE_SERVICES.md` Section 5.
 *
 * Pure typed data. Safe to import from any page. No fetches.
 */

import type { LwaBackendEngineId } from "./lwa-engine-stage-map";

export type LwaEngineDeployRisk = "low" | "medium" | "high";

export type LwaEngineDeployRecord = {
  engineId: LwaBackendEngineId;
  /** 1-based deploy order. 1 ships first. */
  order: number;
  serviceName: string;
  risk: LwaEngineDeployRisk;
  /** One-sentence reason for ordering. */
  rationale: string;
  /** Whether this engine is safe to enable for an investor demo today. */
  safeForDemo: boolean;
};

export const LWA_ENGINE_DEPLOY_ORDER: readonly LwaEngineDeployRecord[] = [
  {
    engineId: "operator_admin",
    order: 1,
    serviceName: "lwa-engine-operator-admin",
    risk: "low",
    rationale: "Read-only system snapshot. Safest first deploy.",
    safeForDemo: true,
  },
  {
    engineId: "safety",
    order: 2,
    serviceName: "lwa-engine-safety",
    risk: "low",
    rationale: "Local guard rails. No external call.",
    safeForDemo: true,
  },
  {
    engineId: "proof_history",
    order: 3,
    serviceName: "lwa-engine-proof-history",
    risk: "low",
    rationale: "Demo proof records; provider not required.",
    safeForDemo: true,
  },
  {
    engineId: "world_game",
    order: 4,
    serviceName: "lwa-engine-world-game",
    risk: "low",
    rationale: "Mission/XP/realm preview. No money.",
    safeForDemo: true,
  },
  {
    engineId: "brain",
    order: 5,
    serviceName: "lwa-engine-brain",
    risk: "medium",
    rationale: "Provider-routable; ship with provider OFF.",
    safeForDemo: true,
  },
  {
    engineId: "render",
    order: 6,
    serviceName: "lwa-engine-render",
    risk: "medium",
    rationale: "Strategy-only fallback active; render path needs queue + cost guard.",
    safeForDemo: true,
  },
  {
    engineId: "creator",
    order: 7,
    serviceName: "lwa-engine-creator",
    risk: "medium",
    rationale: "Mission seed. Backend persistence pending.",
    safeForDemo: true,
  },
  {
    engineId: "wallet_entitlements",
    order: 8,
    serviceName: "lwa-engine-wallet-entitlements",
    risk: "high",
    rationale: "Read-only credits/entitlements. Payouts permanently OFF.",
    safeForDemo: false,
  },
  {
    engineId: "marketplace",
    order: 9,
    serviceName: "lwa-engine-marketplace",
    risk: "high",
    rationale: "Teaser only. Full marketplace blocked behind legal review.",
    safeForDemo: false,
  },
  {
    engineId: "social_distribution",
    order: 10,
    serviceName: "lwa-engine-social-distribution",
    risk: "high",
    rationale: "Recommendations only. External posting must remain OFF.",
    safeForDemo: false,
  },
] as const;

const BY_ID: Record<string, LwaEngineDeployRecord> = Object.fromEntries(
  LWA_ENGINE_DEPLOY_ORDER.map((r) => [r.engineId, r]),
);

export function getDeployRecord(
  engineId: LwaBackendEngineId,
): LwaEngineDeployRecord | undefined {
  return BY_ID[engineId];
}

export function getDeployOrder(engineId: LwaBackendEngineId): number | undefined {
  return BY_ID[engineId]?.order;
}

export function getEnginesSafeForDemo(): LwaEngineDeployRecord[] {
  return LWA_ENGINE_DEPLOY_ORDER.filter((r) => r.safeForDemo);
}
