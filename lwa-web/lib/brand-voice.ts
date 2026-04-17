export const BRAND_VOICE = {
  mustFeel: [
    "viral-native",
    "premium",
    "cinematic",
    "sharp",
    "creator-first",
    "high-status",
    "adult",
    "screen-grabbing",
  ],
  avoid: [
    "childish",
    "corny slang spam",
    "meme voice",
    "generic SaaS filler",
    "robotic AI copy",
    "kid TikTok energy",
  ],
  style: {
    headline: "short, punchy, scroll-stopping",
    subhead: "clear, sexy, cinematic, useful",
    cta: "direct, high-energy, confident",
    body: "clean, modern, premium, readable",
  },
} as const;

export const HERO_COPY = {
  kicker: "AI MEDIA OPERATING SYSTEM",
  headline: "Turn one source into the clips people actually replay.",
  subhead:
    "Hooks, packaging, post order, and previews built to move fast, hit harder, and look ready before the scroll is over.",
  primaryCta: "Forge Clips",
  secondaryCta: "Open Control Room",
} as const;

export const GENERATOR_COPY = {
  title: "Forge a ranked clip stack",
  subhead: "Source in. Ranked previews, sharper copy, and export-ready cuts back out.",
  loading: "LWA is cutting the stack live.",
  submit: "Forge Clips",
  submitting: "Forging stack...",
  outputReady: "Stack ready. Review first, queue next, export when it clears your plan.",
  outputIdle: "Drop a link or local file and let the stack build.",
} as const;

export const RESULTS_COPY = {
  kicker: "Clip stack live",
  title: "Post order, packaging, and previews are ready.",
  subhead: "Lead cut first. Ranked follow-ups after that.",
  sourceTruth: "Source intelligence",
  topClip: "Lead cut",
  gridTitle: "Next clips worth posting",
  outputTrust: "Output trust",
  executionGuide: "Move the stack fast",
} as const;

export function rewriteSurfaceLabel(label: string): string {
  const map: Record<string, string> = {
    Dashboard: "Control Room",
    Generate: "Forge Clips",
    Upload: "Drop Source",
    History: "Archive",
    Batches: "Stacks",
    Campaigns: "Missions",
    Wallet: "Vault",
    Settings: "Studio Settings",
  };

  return map[label] || label;
}
