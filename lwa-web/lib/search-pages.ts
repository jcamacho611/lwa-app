export type SearchLandingSection = {
  title: string;
  body: string;
  bullets: string[];
};

export type SearchLandingLink = {
  href: string;
  label: string;
};

export type SearchLandingData = {
  slug: string;
  path: string;
  type: "comparison" | "use_case";
  kicker: string;
  title: string;
  description: string;
  metaTitle: string;
  metaDescription: string;
  keywords: string[];
  proofPoints: string[];
  sections: SearchLandingSection[];
  related: SearchLandingLink[];
};

export const comparisonPages: SearchLandingData[] = [
  {
    slug: "opus-clip-alternative",
    path: "/compare/opus-clip-alternative",
    type: "comparison",
    kicker: "Comparison",
    title: "The sharper Opus Clip alternative for structured output and operator trust.",
    description:
      "LWA is built for creators, clippers, and teams that need clips worth posting, packaging intelligence, post order, and workflow depth in one control room.",
    metaTitle: "Best Opus Clip Alternative",
    metaDescription:
      "Compare LWA vs Opus Clip for viral-ready clip stacks, hooks, captions, timestamps, packaging, queue flow, and creator workflow depth.",
    keywords: ["opus clip alternative", "best opus clip alternative", "opus clip vs lwa", "viral-ready clip stack"],
    proofPoints: ["Best clip first", "Packaging + CTA", "Queue + campaign flow"],
    sections: [
      {
        title: "Why teams switch",
        body: "Opus is useful for quick clipping. LWA pushes harder on structured output, post order, packaging signals, and operator flow after the first cut.",
        bullets: [
          "Best clip first instead of flat output dumps",
          "Why-this-matters, confidence, CTA, and thumbnail text in the same review layer",
          "Queue, campaign, and wallet surfaces already built into the workspace",
        ],
      },
      {
        title: "Where LWA wins",
        body: "LWA is built like a source-to-post decision system, not just a clip puller.",
        bullets: [
          "Viral-ready clip stack built for actual posting order",
          "Hooks, captions, timestamps, and packaging angles returned together",
          "Operator-ready review flow for creators, clippers, and teams",
        ],
      },
    ],
    related: [
      { href: "/compare/capcut-alternative", label: "CapCut alternative" },
      { href: "/use-cases/podcast-clipping", label: "Podcast clipping" },
      { href: "/generate", label: "Generate clips" },
    ],
  },
  {
    slug: "capcut-alternative",
    path: "/compare/capcut-alternative",
    type: "comparison",
    kicker: "Comparison",
    title: "The AI-first CapCut alternative for speed, ranking, and clip packaging.",
    description:
      "CapCut is still stronger for manual editing depth. LWA wins when the job is to turn one long-form source into review-ready short-form outputs faster.",
    metaTitle: "Best CapCut Alternative for Clipping",
    metaDescription:
      "Compare LWA vs CapCut for AI clipping speed, structured outputs, hooks, captions, timestamps, packaging, and creator workflow leverage.",
    keywords: ["capcut alternative for clipping", "best capcut alternative", "capcut vs lwa", "ai clipping tool"],
    proofPoints: ["AI-first speed", "Hooks that hit", "Operator workflow"],
    sections: [
      {
        title: "Different job, different winner",
        body: "CapCut is an editor. LWA is an AI clipping engine. If the goal is source-to-post speed, ranking, and packaging, the right benchmark shifts.",
        bullets: [
          "Less timeline time, more structured output",
          "Copy, packaging, and previews returned together",
          "Built for creators, clippers, and operator workflows",
        ],
      },
      {
        title: "What LWA is for",
        body: "LWA is strongest when you want more clips worth posting from the content you already make.",
        bullets: [
          "Podcast, stream, interview, and webinar repurposing",
          "Fast review of the best clip first",
          "Upgrade path into campaigns, queue, and payout-readiness",
        ],
      },
    ],
    related: [
      { href: "/compare/opus-clip-alternative", label: "Opus Clip alternative" },
      { href: "/use-cases/creator-repurposing", label: "Creator repurposing" },
      { href: "/generate", label: "Generate clips" },
    ],
  },
];

export const useCasePages: SearchLandingData[] = [
  {
    slug: "podcast-clipping",
    path: "/use-cases/podcast-clipping",
    type: "use_case",
    kicker: "Use case",
    title: "Turn one podcast episode into a short-form stack.",
    description:
      "LWA helps podcasters turn long episodes into clips worth posting with hooks, captions, timestamps, packaging signals, and playable previews.",
    metaTitle: "Podcast Clip Generator",
    metaDescription:
      "Turn podcast episodes into clips worth posting with hooks, captions, timestamps, packaging angles, and short-form-ready previews.",
    keywords: ["podcast clip generator", "ai podcast clipper", "podcast to shorts", "best podcast clipping tool"],
    proofPoints: ["Podcast to shorts", "Hooks + captions", "Lead clip first"],
    sections: [
      {
        title: "Why podcast teams use it",
        body: "Every long-form episode has multiple moments worth posting. The problem is picking them fast and packaging them well.",
        bullets: [
          "Find moments worth cutting",
          "Return hooks, captions, and timestamps together",
          "Keep the strongest clip in the lead slot",
        ],
      },
      {
        title: "What the stack gives you",
        body: "LWA returns a pack you can review, queue, and export without guessing what should go out first.",
        bullets: [
          "Playable previews",
          "Post-order signals",
          "Packaging copy for faster review",
        ],
      },
    ],
    related: [
      { href: "/use-cases/creator-repurposing", label: "Creator repurposing" },
      { href: "/compare/opus-clip-alternative", label: "Opus Clip alternative" },
      { href: "/generate", label: "Generate clips" },
    ],
  },
  {
    slug: "whop-clipping",
    path: "/use-cases/whop-clipping",
    type: "use_case",
    kicker: "Use case",
    title: "Built for clipping workflows, content rewards, and fast submission stacks.",
    description:
      "LWA fits Whop-style clipping work by helping operators move from source to clips worth posting, queue, campaigns, and payout-readiness faster.",
    metaTitle: "Best Tool for Whop Clipping",
    metaDescription:
      "Use LWA for viral-ready clip stacks, packaging, queue flow, and creator/operator workflows built for clipping campaigns and content rewards.",
    keywords: ["best tool for whop clipping", "how to make money clipping on whop", "content rewards clipping software", "clipping campaign workflow"],
    proofPoints: ["Campaign-ready", "Queue control", "Payout-ready flow"],
    sections: [
      {
        title: "Why it maps to clipping campaigns",
        body: "Clipping work is not just about cutting a moment. It is about ranking output, packaging it fast, and moving submissions without losing quality.",
        bullets: [
          "Best clip first review flow",
          "Queue and campaign surfaces already in the product",
          "Wallet and payout-readiness scaffolding for operator trust",
        ],
      },
      {
        title: "What to keep compliant",
        body: "Use disclosures where required and keep platform/payment policy differences explicit. LWA improves speed and workflow, not guaranteed income.",
        bullets: [
          "FTC-compliant disclosures where needed",
          "No fake earnings claims",
          "Use the tool for leverage, speed, and more output from real source material",
        ],
      },
    ],
    related: [
      { href: "/use-cases/podcast-clipping", label: "Podcast clipping" },
      { href: "/compare/capcut-alternative", label: "CapCut alternative" },
      { href: "/campaigns", label: "Open campaigns" },
    ],
  },
  {
    slug: "creator-repurposing",
    path: "/use-cases/creator-repurposing",
    type: "use_case",
    kicker: "Use case",
    title: "Turn one source into more clips worth posting without filming more.",
    description:
      "LWA is built for creators who already have long-form content and want a faster path from source to short-form output, queue, and review.",
    metaTitle: "AI Content Repurposing for Creators",
    metaDescription:
      "Turn one long-form source into a viral-ready clip stack with hooks, captions, timestamps, packaging angles, and operator-ready review flow.",
    keywords: ["creator repurposing tool", "ai content repurposing", "turn one video into multiple clips", "short form workflow for creators"],
    proofPoints: ["Source to post faster", "Review-ready stack", "Premium creator workflow"],
    sections: [
      {
        title: "What creators actually want",
        body: "More short-form output from the content they already make, without drowning in timeline work or random clip guesses.",
        bullets: [
          "One source becomes a post-ready stack",
          "Hooks, captions, and packaging stay attached",
          "Review flow stays clean and best-clip-first",
        ],
      },
      {
        title: "Why the workflow matters",
        body: "A clip tool is not enough if the result still feels random. LWA pushes toward faster decisions and a more credible posting workflow.",
        bullets: [
          "Lead cut authority",
          "Export trust",
          "Queue and archive continuity",
        ],
      },
    ],
    related: [
      { href: "/use-cases/podcast-clipping", label: "Podcast clipping" },
      { href: "/compare/opus-clip-alternative", label: "Opus Clip alternative" },
      { href: "/generate", label: "Generate clips" },
    ],
  },
];

export function getComparisonPage(slug: string) {
  return comparisonPages.find((page) => page.slug === slug) || null;
}

export function getUseCasePage(slug: string) {
  return useCasePages.find((page) => page.slug === slug) || null;
}
