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
  kicker: "CLIP DECISION ENGINE",
  headline: "Clips worth posting. Decided fast.",
  subhead: "Paste one source. LWA picks the lead cut, packages the stack, and gets you closer to posting.",
  primaryCta: "Generate clips",
  secondaryCta: "Open workspace",
} as const;

export const GENERATOR_COPY = {
  title: "Build clips worth posting",
  subhead: "Source in. Previews, hooks, and post order back.",
  loading: "LWA is cutting.",
  submit: "Generate clips",
  submitting: "Generating...",
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
