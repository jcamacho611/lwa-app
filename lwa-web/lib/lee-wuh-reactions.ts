import type { LeeWuhAnimationState } from "../components/lee-wuh/leeWuhAnimationStates";
import type { LwaExperienceState } from "./lwa-experience-state";

export type LeeWuhReactionAnimation =
  | LeeWuhAnimationState
  | "point_right";

export type LeeWuhReactionMood =
  | "calm"
  | "focused"
  | "powered"
  | "confident"
  | "tactical"
  | "proud"
  | "excited"
  | "mystical"
  | "concerned";

export type LeeWuhExperienceReaction = {
  animation: LeeWuhReactionAnimation;
  mood: LeeWuhReactionMood;
  line: string;
  recommendedActionLabel: string;
  recommendedHref?: string;
};

export const leeWuhExperienceReactions: Record<
  LwaExperienceState,
  LeeWuhExperienceReaction
> = {
  idle: {
    animation: "hover",
    mood: "calm",
    line: "Drop in a source and I'll find the strongest move.",
    recommendedActionLabel: "Open generate",
    recommendedHref: "/generate",
  },
  source_added: {
    animation: "point_right",
    mood: "focused",
    line: "Good. Now generate the clip pack.",
    recommendedActionLabel: "Generate clip pack",
    recommendedHref: "/generate",
  },
  analyzing: {
    animation: "thinking",
    mood: "focused",
    line: "I'm reading the signal.",
    recommendedActionLabel: "Wait for analysis",
  },
  rendering: {
    animation: "rendering",
    mood: "powered",
    line: "The realm is cutting this into proof.",
    recommendedActionLabel: "Monitor render",
  },
  clips_ready: {
    animation: "victory",
    mood: "confident",
    line: "Best clip is ready. Post this one first.",
    recommendedActionLabel: "Review best clip",
    recommendedHref: "/generate",
  },
  strategy_only: {
    animation: "judgment",
    mood: "tactical",
    line: "This is strategy only. Useful, but not export-ready yet.",
    recommendedActionLabel: "Choose recovery path",
  },
  export_ready: {
    animation: "point_right",
    mood: "confident",
    line: "Package is ready. Copy it, export it, or save proof.",
    recommendedActionLabel: "Copy package",
  },
  proof_saved: {
    animation: "victory",
    mood: "proud",
    line: "Proof saved. That strengthens your creator record.",
    recommendedActionLabel: "Open proof",
    recommendedHref: "/proof",
  },
  mission_complete: {
    animation: "victory",
    mood: "excited",
    line: "Mission complete. You moved the realm forward.",
    recommendedActionLabel: "Claim reward",
  },
  reward_unlocked: {
    animation: "realmOpen",
    mood: "powered",
    line: "Reward unlocked.",
    recommendedActionLabel: "Choose next mission",
  },
  marketplace_ready: {
    animation: "marketplaceGuide",
    mood: "focused",
    line: "Money lane is open. Choose the right opportunity.",
    recommendedActionLabel: "Open marketplace",
    recommendedHref: "/marketplace",
  },
  realm_open: {
    animation: "realmOpen",
    mood: "mystical",
    line: "The realm is open.",
    recommendedActionLabel: "Enter realm",
    recommendedHref: "/realm",
  },
  error: {
    animation: "error",
    mood: "concerned",
    line: "Something failed, but we can recover the run.",
    recommendedActionLabel: "Review recovery",
  },
};

export function getLeeWuhExperienceReaction(
  state: LwaExperienceState,
): LeeWuhExperienceReaction {
  return leeWuhExperienceReactions[state] ?? leeWuhExperienceReactions.idle;
}

