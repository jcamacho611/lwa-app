export type LwaExperienceState =
  | "idle"
  | "source_added"
  | "analyzing"
  | "rendering"
  | "clips_ready"
  | "strategy_only"
  | "export_ready"
  | "proof_saved"
  | "mission_complete"
  | "reward_unlocked"
  | "marketplace_ready"
  | "realm_open"
  | "error";

export type LwaExperienceEvent =
  | "SOURCE_ADDED"
  | "GENERATION_STARTED"
  | "RENDERING_STARTED"
  | "CLIPS_RENDERED"
  | "STRATEGY_ONLY_RETURNED"
  | "EXPORT_READY"
  | "EXPORT_PACKAGE_COPIED"
  | "PROOF_SAVED"
  | "MARKETPLACE_OPENED"
  | "REALM_ENTERED"
  | "MISSION_COMPLETED"
  | "REWARD_UNLOCKED"
  | "ERROR_OCCURRED"
  | "RECOVERY_AVAILABLE"
  | "RESET";

export type LwaExperienceReward = {
  xp: number;
  label: string;
};

export type LwaExperienceTransition = {
  previousState: LwaExperienceState;
  state: LwaExperienceState;
  event: LwaExperienceEvent;
  timestamp: string;
  guidance: string;
  nextAction: string;
  leeWuhReaction: string;
  reward?: LwaExperienceReward;
};

const stateByEvent: Record<LwaExperienceEvent, LwaExperienceState> = {
  SOURCE_ADDED: "source_added",
  GENERATION_STARTED: "analyzing",
  RENDERING_STARTED: "rendering",
  CLIPS_RENDERED: "clips_ready",
  STRATEGY_ONLY_RETURNED: "strategy_only",
  EXPORT_READY: "export_ready",
  EXPORT_PACKAGE_COPIED: "export_ready",
  PROOF_SAVED: "proof_saved",
  MARKETPLACE_OPENED: "marketplace_ready",
  REALM_ENTERED: "realm_open",
  MISSION_COMPLETED: "mission_complete",
  REWARD_UNLOCKED: "reward_unlocked",
  ERROR_OCCURRED: "error",
  RECOVERY_AVAILABLE: "strategy_only",
  RESET: "idle",
};

const transitionCopy: Record<
  LwaExperienceEvent,
  Pick<LwaExperienceTransition, "guidance" | "nextAction" | "leeWuhReaction"> & {
    reward?: LwaExperienceReward;
  }
> = {
  SOURCE_ADDED: {
    guidance: "Source is attached. The next move is to analyze for retention-weighted clip candidates.",
    nextAction: "Start generation",
    leeWuhReaction: "Lee-Wuh locks onto the source and waits for the first signal.",
  },
  GENERATION_STARTED: {
    guidance: "LWA is reading the source for hooks, tension, payoff, and standalone moments.",
    nextAction: "Wait for analysis",
    leeWuhReaction: "Lee-Wuh studies the source like a council operator.",
  },
  RENDERING_STARTED: {
    guidance: "Rendering has started. Strategy should remain available even if media rendering fails.",
    nextAction: "Monitor render output",
    leeWuhReaction: "Lee-Wuh raises the Realm Blade and tracks the render path.",
  },
  CLIPS_RENDERED: {
    guidance: "Rendered clips are ready. Review the first ranked clip before exporting.",
    nextAction: "Inspect best clip",
    leeWuhReaction: "Lee-Wuh marks the strongest clip as the first signal.",
    reward: { xp: 100, label: "Signal Spark relic" },
  },
  STRATEGY_ONLY_RETURNED: {
    guidance: "Strategy-only output is ready. The package is still useful without rendered media.",
    nextAction: "Export strategy package",
    leeWuhReaction: "Lee-Wuh preserves the plan and keeps the path alive.",
  },
  EXPORT_READY: {
    guidance: "The package is export-ready. Copy the hook, caption, timestamps, and score notes.",
    nextAction: "Copy export package",
    leeWuhReaction: "Lee-Wuh sharpens the package for posting or proof.",
  },
  EXPORT_PACKAGE_COPIED: {
    guidance: "Export package copied. Save proof or move the package into the next workflow.",
    nextAction: "Save proof",
    leeWuhReaction: "Lee-Wuh records the package handoff.",
    reward: { xp: 75, label: "Proof Mark badge" },
  },
  PROOF_SAVED: {
    guidance: "Proof is saved as a local product milestone. Durable proof persistence comes later.",
    nextAction: "Open marketplace or realm",
    leeWuhReaction: "Lee-Wuh stamps the action as proof-ready.",
    reward: { xp: 75, label: "Proof Mark badge" },
  },
  MARKETPLACE_OPENED: {
    guidance: "Marketplace path opened. Use generated strategy as campaign-ready preparation, not automated submission.",
    nextAction: "Review marketplace fit",
    leeWuhReaction: "Lee-Wuh opens the money gate without making payout claims.",
    reward: { xp: 50, label: "Money Gate unlocked" },
  },
  REALM_ENTERED: {
    guidance: "Realm layer opened. The user can now see progression around real creator work.",
    nextAction: "Continue realm mission",
    leeWuhReaction: "Lee-Wuh opens the realm around the current work state.",
    reward: { xp: 50, label: "Realm access pulse" },
  },
  MISSION_COMPLETED: {
    guidance: "Mission complete. The next best action should build on the completed creator workflow.",
    nextAction: "Claim reward",
    leeWuhReaction: "Lee-Wuh marks the mission as complete.",
  },
  REWARD_UNLOCKED: {
    guidance: "Reward unlocked. This is a safe progression reward, not money or payout automation.",
    nextAction: "Choose next mission",
    leeWuhReaction: "Lee-Wuh lights up the reward ledger path.",
  },
  ERROR_OCCURRED: {
    guidance: "Something failed. Preserve useful output and offer recovery before asking the user to start over.",
    nextAction: "Check recovery options",
    leeWuhReaction: "Lee-Wuh moves into operator recovery mode.",
  },
  RECOVERY_AVAILABLE: {
    guidance: "Recovery is available. Continue with strategy, retry render, or save a proof idea.",
    nextAction: "Choose recovery path",
    leeWuhReaction: "Lee-Wuh keeps the mission alive through fallback.",
    reward: { xp: 40, label: "Operator Focus badge" },
  },
  RESET: {
    guidance: "Experience reset to idle. Add a source to start the next signal path.",
    nextAction: "Add source",
    leeWuhReaction: "Lee-Wuh returns to watch mode.",
  },
};

export function applyLwaExperienceEvent(
  currentState: LwaExperienceState,
  event: LwaExperienceEvent,
): LwaExperienceTransition {
  const copy = transitionCopy[event];
  return {
    previousState: currentState,
    state: stateByEvent[event],
    event,
    timestamp: new Date().toISOString(),
    guidance: copy.guidance,
    nextAction: copy.nextAction,
    leeWuhReaction: copy.leeWuhReaction,
    reward: copy.reward,
  };
}
