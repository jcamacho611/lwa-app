export type LeeWuhState =
  | "idle"
  | "watching"
  | "thinking"
  | "ingesting"
  | "composing"
  | "rendering"
  | "success"
  | "warning"
  | "error"
  | "overlord";

export type LeeWuhSize = "sm" | "md" | "lg" | "hero";

export const LEE_WUH_BRAND = {
  mascotName: "Lee-Wuh",
  pronunciation: "lee-wuh",
  productName: "LWA",
  role: "The Last Creator",
  tagline: "Create. Inspire. Takeover.",
  heroTagline: "The final boss of lazy content",
  assetPath: "/brand/lee-wuh-mascot.png",
  heroAssetPath: "/brand/lee-wuh-hero-16x9.png",
  colors: {
    black: "#050505",
    charcoal: "#111016",
    gold: "#F4C45D",
    deepGold: "#B88422",
    purple: "#8B3DFF",
    violet: "#B56CFF",
    red: "#C92A2A",
  },
} as const;

export const LEE_WUH_MESSAGES: Record<LeeWuhState, string> = {
  idle: "Drop the source. I'll find the first move.",
  watching: "I'm watching for the moment that matters.",
  thinking: "Let me separate the noise from the signal.",
  ingesting: "Loading the source into the realm.",
  composing: "Building the timeline before the blade drops.",
  rendering: "Turning strategy into something playable.",
  success: "Overlord status. This one is ready.",
  warning: "Careful. This needs one more check.",
  error: "The realm rejected that move. Try again clean.",
  overlord: "Create. Inspire. Takeover.",
};

export function getLeeWuhMessage(state: LeeWuhState) {
  return LEE_WUH_MESSAGES[state] ?? LEE_WUH_MESSAGES.idle;
}
