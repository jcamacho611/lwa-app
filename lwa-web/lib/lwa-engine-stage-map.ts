/**
 * lwa-engine-stage-map
 *
 * Maps each Public Demo Loop stage to the backend engine that will
 * eventually own that stage. Used by the /demo and /engines pages to
 * prove that the demo flow is grounded in real backend modules — not
 * frontend storytelling.
 *
 * No fetches here. Pure typed data. Safe to import from any page.
 */

import type { LwaPublicDemoStageId } from "./lwa-public-demo-loop";

export type LwaBackendEngineId =
  | "creator"
  | "brain"
  | "render"
  | "marketplace"
  | "wallet_entitlements"
  | "proof_history"
  | "world_game"
  | "safety"
  | "social_distribution"
  | "operator_admin";

export type LwaEngineStageBinding = {
  stageId: LwaPublicDemoStageId;
  engineId: LwaBackendEngineId;
  /** Why this engine is the right backend for this stage. */
  rationale: string;
  /** A safe, deterministic payload to send to /engines/{id}/demo. */
  demoPayload: Record<string, unknown>;
};

export const LWA_ENGINE_STAGE_BINDINGS: readonly LwaEngineStageBinding[] = [
  {
    stageId: "landing",
    engineId: "operator_admin",
    rationale: "First-touch surface reads a safe operator snapshot.",
    demoPayload: { focus: "first_touch" },
  },
  {
    stageId: "first_mission",
    engineId: "creator",
    rationale: "Creator engine seeds the first mission from a source.",
    demoPayload: { source: "demo source" },
  },
  {
    stageId: "source_added",
    engineId: "creator",
    rationale: "Creator engine acknowledges the source and primes signals.",
    demoPayload: { source: "demo source", title: "Demo upload" },
  },
  {
    stageId: "clips_ready",
    engineId: "brain",
    rationale: "Brain engine ranks clip opportunities and explains the choice.",
    demoPayload: { recommended_action: "Lead with the strongest hook" },
  },
  {
    stageId: "recovery_available",
    engineId: "render",
    rationale: "Render engine exposes the strategy-only fallback path.",
    demoPayload: { render_requested: false },
  },
  {
    stageId: "proof_saved",
    engineId: "proof_history",
    rationale: "Proof history records what was created and saved.",
    demoPayload: { proof_id: "proof_demo_001" },
  },
  {
    stageId: "signal_sprint",
    engineId: "world_game",
    rationale: "World game engine drives missions, XP, and realm progression.",
    demoPayload: { current_realm: "signal_realm" },
  },
  {
    stageId: "marketplace_teaser",
    engineId: "marketplace",
    rationale: "Marketplace engine surfaces a teaser lane only — no transactions.",
    demoPayload: { preview_offer: "Creator growth lane" },
  },
  {
    stageId: "return_loop",
    engineId: "social_distribution",
    rationale: "Social distribution recommends platforms but never posts.",
    demoPayload: { destination: "manual_review" },
  },
] as const;

export function getEngineForStage(
  stageId: LwaPublicDemoStageId,
): LwaEngineStageBinding | undefined {
  return LWA_ENGINE_STAGE_BINDINGS.find((b) => b.stageId === stageId);
}

export function getStagesForEngine(
  engineId: LwaBackendEngineId,
): LwaEngineStageBinding[] {
  return LWA_ENGINE_STAGE_BINDINGS.filter((b) => b.engineId === engineId);
}
