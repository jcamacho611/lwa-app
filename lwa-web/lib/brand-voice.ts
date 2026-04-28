export const BRAND_VOICE = {
  mustFeel: [
    "retention-native",
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
  title: "Any source in. Creator-ready content out.",
  subhead: "Paste a URL, upload a file, or describe an idea.",
  loading: "Finding your best moments...",
  submit: "Generate clips",
  submitting: "Finding clips...",
  outputReady: "Your best clips. Ranked. Ready to post.",
  outputIdle: "Drop one source.",
  sourceModesHint: "Video · Audio · Music · Prompt · Stream · Campaign · Upload",
} as const;

export const RESULTS_COPY = {
  kicker: "Clips ready",
  title: "Best clip first. Post the rest in order.",
  subhead: "Rendered clips first. Strategy-only clips second.",
  sourceTruth: "Source intelligence",
  topClip: "Best clip",
  gridTitle: "Post next",
  outputTrust: "Output confidence",
  executionGuide: "Post in order",
  renderedLabel: "Rendered",
  strategyOnlyLabel: "Strategy only",
  exportRail: "Export-ready",
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
