export type LeeWuhAnimationState =
  | "idle"
  | "breathe"
  | "hover"
  | "click"
  | "speak"
  | "thinking"
  | "analyzing"
  | "rendering"
  | "judgment"
  | "victory"
  | "error"
  | "realmOpen"
  | "marketplaceGuide";

export type LeeWuhAnimationStateConfig = {
  id: LeeWuhAnimationState;
  label: string;
  line: string;
  aura: "gold" | "purple" | "blue" | "red";
  intensity: "calm" | "active" | "high";
};

export const leeWuhAnimationStates: Record<LeeWuhAnimationState, LeeWuhAnimationStateConfig> = {
  idle: {
    id: "idle",
    label: "Idle",
    line: "Lee-Wuh is watching the route and waiting for the next move.",
    aura: "gold",
    intensity: "calm",
  },
  breathe: {
    id: "breathe",
    label: "Breathe",
    line: "The living agent breathes over the world layer.",
    aura: "purple",
    intensity: "calm",
  },
  hover: {
    id: "hover",
    label: "Hover",
    line: "Lee-Wuh reacts when the creator gets close.",
    aura: "gold",
    intensity: "active",
  },
  click: {
    id: "click",
    label: "Click",
    line: "The agent opens a local guide panel and routes the next action.",
    aura: "purple",
    intensity: "high",
  },
  speak: {
    id: "speak",
    label: "Speak",
    line: "Local rule-based replies answer first. Provider AI can enhance later.",
    aura: "blue",
    intensity: "active",
  },
  thinking: {
    id: "thinking",
    label: "Thinking",
    line: "Choose the lane and Lee-Wuh will guide the sequence.",
    aura: "blue",
    intensity: "active",
  },
  analyzing: {
    id: "analyzing",
    label: "Analyzing",
    line: "Lee-Wuh is scanning hooks, source quality, and route intent.",
    aura: "purple",
    intensity: "high",
  },
  rendering: {
    id: "rendering",
    label: "Rendering",
    line: "Rendered clips are preferred, but strategy output must remain safe.",
    aura: "blue",
    intensity: "high",
  },
  judgment: {
    id: "judgment",
    label: "Judgment",
    line: "The best clip must win by retention behavior, not topic alone.",
    aura: "gold",
    intensity: "high",
  },
  victory: {
    id: "victory",
    label: "Victory",
    line: "The package is ready to review, export, or route into a campaign.",
    aura: "gold",
    intensity: "high",
  },
  error: {
    id: "error",
    label: "Error",
    line: "A blocker hit. Keep fallback output alive and guide recovery.",
    aura: "red",
    intensity: "active",
  },
  realmOpen: {
    id: "realmOpen",
    label: "Realm Open",
    line: "The world layer connects creation, missions, and transparent rewards.",
    aura: "purple",
    intensity: "high",
  },
  marketplaceGuide: {
    id: "marketplaceGuide",
    label: "Marketplace Guide",
    line: "The money lane starts with clear work, task state, and safe payment metadata.",
    aura: "gold",
    intensity: "active",
  },
};

export function getLeeWuhAnimationState(state: LeeWuhAnimationState) {
  return leeWuhAnimationStates[state] || leeWuhAnimationStates.idle;
}
