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
  kicker: "LWA",
  headline: "Drop in. Get clips.",
  subhead: "One source. Ranked short-form. Ready to post.",
  primaryCta: "Generate clips",
  secondaryCta: "Open queue",
} as const;

export const GENERATOR_COPY = {
  title: "Paste your source URL",
  subhead: "Hooks, previews, post order.",
  loading: "Finding your best moments...",
  submit: "Generate clips",
  submitting: "Finding clips...",
  outputReady: "Ready. Review, queue, export.",
  outputIdle: "Drop one link or file.",
} as const;

export const RESULTS_COPY = {
  kicker: "Outputs ready",
  title: "Post this first. Move the rest next.",
  subhead: "Lead cut first. Follow-ups after.",
  sourceTruth: "Source intelligence",
  topClip: "Lead cut",
  gridTitle: "Next clips",
  outputTrust: "Output trust",
  executionGuide: "Move fast",
} as const;

export function rewriteSurfaceLabel(label: string): string {
  const map: Record<string, string> = {
    Dashboard: "Control Room",
    Generate: "Generate",
    Upload: "Upload",
    History: "Archive",
    Batches: "Batches",
    Campaigns: "Campaigns",
    Wallet: "Wallet",
    Settings: "Settings",
  };

  return map[label] || label;
}
