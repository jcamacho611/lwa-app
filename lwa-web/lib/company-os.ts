export type CompanyOsStatus =
  | "live"
  | "ready"
  | "building"
  | "queued"
  | "blocked"
  | "needs-review";

export type CompanyOsNavItem = {
  title: string;
  href: string;
  description: string;
  status: CompanyOsStatus;
};

export type CompanyOsMetric = {
  label: string;
  value: string;
  detail: string;
  status: CompanyOsStatus;
};

export type CouncilRole = {
  title: string;
  codename: string;
  mission: string;
  owns: string[];
  metrics: string[];
  nextActions: string[];
  buildResponsibilities: string[];
};

export type CompanyOsCard = {
  title: string;
  eyebrow: string;
  description: string;
  status: CompanyOsStatus;
  href?: string;
  actions: string[];
};

export type RevenueTier = {
  name: string;
  price: string;
  target: string;
  promise: string;
  included: string[];
  nextAction: string;
};

export type PipelineItem = {
  title: string;
  owner: string;
  status: CompanyOsStatus;
  nextAction: string;
  value: string;
};

export type BrandAsset = {
  name: string;
  path: string;
  use: string;
  status: CompanyOsStatus;
};

export type CreativeEngine = {
  name: string;
  purpose: string;
  status: CompanyOsStatus;
  nextAction: string;
};

export const companyOsNav: CompanyOsNavItem[] = [
  {
    title: "Company OS",
    href: "/company-os",
    description: "Master operating surface for the full LWA company system.",
    status: "ready",
  },
  {
    title: "Command Center",
    href: "/command-center",
    description: "Creator/operator dashboard for generation, review, packaging, and action.",
    status: "building",
  },
  {
    title: "Council",
    href: "/council",
    description: "Senior expert operating council encoded as roles, missions, metrics, and actions.",
    status: "ready",
  },
  {
    title: "Brand World",
    href: "/brand-world",
    description: "Lee-Wuh mascot, visual system, 3D pipeline, lore rules, and usage surfaces.",
    status: "ready",
  },
  {
    title: "Revenue",
    href: "/revenue",
    description: "Whop, pricing, sales, investor, onboarding, and money movement system.",
    status: "ready",
  },
  {
    title: "Generate",
    href: "/generate",
    description: "Existing clipping/generation flow. Preserve and strengthen this route.",
    status: "live",
  },
  {
    title: "Campaigns",
    href: "/campaigns",
    description: "Campaign workflow, requirements, submissions, review states, and exports.",
    status: "building",
  },
];

export const companyMetrics: CompanyOsMetric[] = [
  {
    label: "Primary System",
    value: "LWA Company OS",
    detail: "One operating layer for product, revenue, brand, council, and execution.",
    status: "ready",
  },
  {
    label: "Mascot Layer",
    value: "Lee-Wuh",
    detail: "Brand/mascot universe, not a replacement for LWA.",
    status: "ready",
  },
  {
    label: "Current Product Spine",
    value: "Clip Generator",
    detail: "Preserve the existing generation flow while expanding the full company system.",
    status: "live",
  },
  {
    label: "Execution Gate",
    value: "Issue #146",
    detail: "No docs-only, no hero-only, no stalling.",
    status: "live",
  },
];

export const companyOsCards: CompanyOsCard[] = [
  {
    title: "LWA Command Center",
    eyebrow: "Main surface",
    description:
      "The operational home for source intake, active jobs, rendered clips, strategy-only outputs, packaging, exports, campaigns, and revenue shortcuts.",
    status: "building",
    href: "/command-center",
    actions: [
      "Wire source intake",
      "Show rendered-first review",
      "Add packaging/export rail",
      "Link revenue and campaign actions",
    ],
  },
  {
    title: "Company Council OS",
    eyebrow: "Senior team",
    description:
      "A structured expert council with owners for architecture, frontend, backend, AI, video, brand, revenue, growth, QA, security, data, marketplace, and release.",
    status: "ready",
    href: "/council",
    actions: [
      "Review role ownership",
      "Assign next actions",
      "Use as build decision map",
    ],
  },
  {
    title: "Lee-Wuh Brand World",
    eyebrow: "Mascot universe",
    description:
      "The mascot and brand layer that makes LWA memorable while staying out of the way of the actual creator workflow.",
    status: "ready",
    href: "/brand-world",
    actions: [
      "Place approved assets",
      "Create 3D roadmap",
      "Use in loading and empty states",
    ],
  },
  {
    title: "Revenue OS",
    eyebrow: "Money system",
    description:
      "Whop, pricing, checkout, lead pipeline, investor pipeline, sales scripts, demos, onboarding, and customer conversion tasks.",
    status: "ready",
    href: "/revenue",
    actions: [
      "Confirm Whop checkout",
      "Pick launch pricing",
      "Start sales outreach",
      "Book demos",
    ],
  },
  {
    title: "Creative Engine OS",
    eyebrow: "Creation stack",
    description:
      "Clipping, captioning, hooks, thumbnail text, music direction, character/world engine, export, and feedback learning.",
    status: "queued",
    actions: [
      "Expose engine status cards",
      "Add metadata endpoints later",
      "Connect to Command Center",
    ],
  },
  {
    title: "Operations / Release OS",
    eyebrow: "Ship control",
    description:
      "PRs, issues, deployments, verification gates, build health, release notes, and next-slice automation.",
    status: "queued",
    actions: [
      "Track open PRs",
      "Run builds",
      "Prevent blocked loops",
      "Merge coherent slices",
    ],
  },
];

export const lwaCouncil: CouncilRole[] = [
  {
    title: "Founder / Operator-in-Chief",
    codename: "Owner Command",
    mission:
      "Set the direction, approve priorities, and keep LWA moving toward money, product power, culture, and shipping.",
    owns: ["Final decisions", "Priority order", "Brand taste", "Revenue urgency"],
    metrics: ["Daily shipped slices", "Open PRs", "Revenue opportunities", "Customer demos"],
    nextActions: ["Review PR #144", "Approve Company OS v0", "Push Whop/demo readiness"],
    buildResponsibilities: ["Protect the vision", "Stop stalling", "Choose the next money move"],
  },
  {
    title: "CEO Execution Strategist",
    codename: "Company Spine",
    mission:
      "Translate the vision into daily execution across product, sales, hiring, funding, and launch.",
    owns: ["Roadmap", "Business model", "Weekly operating cadence"],
    metrics: ["Launch readiness", "Sales pipeline", "Investor pipeline"],
    nextActions: ["Define launch gate", "Prioritize revenue blockers", "Package demo story"],
    buildResponsibilities: ["Company OS dashboard", "operating checklist", "cross-team sequencing"],
  },
  {
    title: "CTO / Principal Architect",
    codename: "Repo Guardian",
    mission:
      "Keep the repo coherent, scalable, and shippable while preventing rewrites and broken integrations.",
    owns: ["Architecture", "Repo boundaries", "Technical debt", "Integration sequence"],
    metrics: ["Build health", "Route coverage", "API stability"],
    nextActions: ["Map missing routes", "Protect clipping flow", "Add metadata v0 endpoints only when needed"],
    buildResponsibilities: ["Route map", "service boundaries", "safe backend expansion"],
  },
  {
    title: "Frontend Creative Director",
    codename: "Premium Surface",
    mission:
      "Make the app feel premium, creator-native, mythic, fast, and obvious to use.",
    owns: ["Web UI", "Layout hierarchy", "Mobile experience", "Visual polish"],
    metrics: ["Homepage clarity", "Command Center usability", "Mobile readiness"],
    nextActions: ["Build Company OS shell", "Upgrade Command Center", "Reduce clutter"],
    buildResponsibilities: ["Next.js pages", "dashboard components", "responsive visual system"],
  },
  {
    title: "Backend Systems Lead",
    codename: "Route Builder",
    mission:
      "Expose engines through stable routes and metadata v0 endpoints without unnecessary rewrites.",
    owns: ["API routes", "Service wiring", "Fallback responses"],
    metrics: ["Route coverage", "Test pass rate", "Error rate"],
    nextActions: ["Wait for frontend route gaps", "Add typed metadata routes", "Preserve existing clipping APIs"],
    buildResponsibilities: ["FastAPI routes", "schemas", "tests"],
  },
  {
    title: "AI/ML Clipping Intelligence Lead",
    codename: "Moment Brain",
    mission:
      "Improve hook detection, moment ranking, caption intelligence, silence removal, and viral scoring.",
    owns: ["Clip ranking", "Recommendation logic", "Retention scoring"],
    metrics: ["Clip quality", "Render count", "Hook strength", "Confidence score"],
    nextActions: ["Define visible intelligence fields", "Improve result reasoning", "Support auto-destination"],
    buildResponsibilities: ["clip scoring metadata", "recommendation objects", "ranking explanations"],
  },
  {
    title: "Video Systems Engineer",
    codename: "Render Forge",
    mission:
      "Make raw clips, edited clips, vertical exports, captions, and render jobs reliable.",
    owns: ["Render pipeline", "Asset URLs", "Video output quality"],
    metrics: ["Successful renders", "Export readiness", "Caption burn-in status"],
    nextActions: ["Surface render job states", "Expose asset readiness", "Connect export actions"],
    buildResponsibilities: ["render metadata", "asset status cards", "video preview handling"],
  },
  {
    title: "3D / Blender / Rive Creative Technologist",
    codename: "Mascot Engineer",
    mission:
      "Turn Lee-Wuh into a web-ready mascot system with Blender, GLB, Rive, and lightweight app integration.",
    owns: ["3D pipeline", "GLB exports", "Rive states", "Performance"],
    metrics: ["Asset readiness", "File size", "Web load performance"],
    nextActions: ["Create GLB roadmap", "Define idle/loading/victory states", "Keep static fallback"],
    buildResponsibilities: ["Blender script", "GLB viewer later", "Rive animation spec"],
  },
  {
    title: "Brand Universe Director",
    codename: "World Keeper",
    mission:
      "Keep Lee-Wuh, the LWA world, visual language, lore, and product clarity aligned.",
    owns: ["Brand world", "Mascot rules", "Tone", "Visual mythology"],
    metrics: ["Brand consistency", "Asset coverage", "Landing page strength"],
    nextActions: ["Build Brand World route", "Document mascot usage rules", "Protect product clarity"],
    buildResponsibilities: ["Brand route", "asset table", "voice/tone rules"],
  },
  {
    title: "Afro-Futurist / Japanese Fusion Art Director",
    codename: "Style Alchemist",
    mission:
      "Ensure the cultural fusion feels premium, original, respectful, and visually unforgettable.",
    owns: ["Character design", "Palette", "Symbol system", "Style guardrails"],
    metrics: ["Visual distinctiveness", "Cultural quality", "Asset consistency"],
    nextActions: ["Define Lee-Wuh design bible", "Guide 3D model style", "Avoid generic fantasy"],
    buildResponsibilities: ["art direction notes", "visual guardrails", "palette rules"],
  },
  {
    title: "Growth Lead",
    codename: "Signal Hunter",
    mission:
      "Turn the app, mascot, and results into customer acquisition across social, Whop, and demos.",
    owns: ["Growth loops", "Content plan", "Launch campaigns"],
    metrics: ["Leads", "Traffic", "Conversion", "Demo requests"],
    nextActions: ["Prepare launch posts", "Create demo sequence", "Track creator targets"],
    buildResponsibilities: ["growth cards", "launch checklist", "social copy bank"],
  },
  {
    title: "Whop / Revenue Lead",
    codename: "Checkout Commander",
    mission:
      "Make LWA sellable now through Whop, pricing, checkout, offers, and customer conversion.",
    owns: ["Whop page", "Pricing", "Checkout flow", "Offer packaging"],
    metrics: ["Checkout clicks", "Paid users", "Conversion rate"],
    nextActions: ["Build Revenue OS route", "Add pricing cards", "Confirm checkout link"],
    buildResponsibilities: ["pricing data", "Whop status card", "offer packaging"],
  },
  {
    title: "Investor Relations Lead",
    codename: "Capital Bridge",
    mission:
      "Package LWA as a fundable company with traction, vision, demo, roadmap, and investor narrative.",
    owns: ["Investor pipeline", "Pitch materials", "Traction story"],
    metrics: ["Investor contacts", "Meetings booked", "Follow-ups"],
    nextActions: ["Create investor dashboard cards", "Prepare demo narrative", "Track warm intros"],
    buildResponsibilities: ["investor pipeline config", "pitch action cards", "follow-up scripts"],
  },
  {
    title: "Sales Operations Lead",
    codename: "Deal Engine",
    mission:
      "Create repeatable outreach scripts, demo flows, lead lists, and follow-up systems.",
    owns: ["Sales scripts", "CRM pipeline", "Demo script"],
    metrics: ["Outreach volume", "Reply rate", "Demo conversion"],
    nextActions: ["Add sales scripts to Revenue OS", "Write short demo flow", "Create follow-up sequence"],
    buildResponsibilities: ["sales script cards", "lead states", "demo checklist"],
  },
  {
    title: "Customer Success Lead",
    codename: "Activation Guide",
    mission:
      "Help users understand what LWA does, what to paste, how to use outputs, and how to succeed.",
    owns: ["Onboarding", "Help copy", "Customer workflow"],
    metrics: ["Activation", "Support issues", "Repeat usage"],
    nextActions: ["Build onboarding checklist", "Create empty-state copy", "Clarify what users get"],
    buildResponsibilities: ["onboarding cards", "help copy", "activation flow"],
  },
  {
    title: "QA / Release Lead",
    codename: "Gatekeeper",
    mission:
      "Prevent broken builds, broken routes, bad mobile layouts, and failed deploys.",
    owns: ["Verification", "Release gates", "Manual test scripts"],
    metrics: ["Build pass rate", "Route health", "Deploy success"],
    nextActions: ["Add release checklist", "Run frontend build", "Track known limitations"],
    buildResponsibilities: ["verification cards", "route test list", "release notes"],
  },
  {
    title: "Security / Privacy Lead",
    codename: "Trust Shield",
    mission:
      "Protect user data, API keys, uploads, private sources, and external integrations.",
    owns: ["Privacy", "Security posture", "Key handling"],
    metrics: ["Secret leaks", "Policy coverage", "Safe defaults"],
    nextActions: ["Audit env assumptions", "Avoid exposing secrets", "Document upload/private-source limits"],
    buildResponsibilities: ["privacy checklist", "safe fallback copy", "risk cards"],
  },
  {
    title: "Data / Analytics Lead",
    codename: "Signal Ledger",
    mission:
      "Track product usage, conversion, clip quality, revenue events, and workflow bottlenecks.",
    owns: ["Analytics schema", "Event naming", "Dashboards"],
    metrics: ["Generation events", "Export events", "Checkout events"],
    nextActions: ["Define event map", "Add metrics placeholders", "Track conversion tasks"],
    buildResponsibilities: ["analytics config", "metric cards", "event names"],
  },
  {
    title: "Marketplace Lead",
    codename: "Creator Exchange",
    mission:
      "Build the marketplace system for offers, creators, campaigns, submissions, and monetization.",
    owns: ["Marketplace v0", "Campaign briefs", "Submission review"],
    metrics: ["Active campaigns", "Creator submissions", "Approved clips"],
    nextActions: ["Surface marketplace metadata", "Define offer cards", "Connect campaign review"],
    buildResponsibilities: ["marketplace cards", "offer states", "creator submission placeholders"],
  },
  {
    title: "Campaign Operations Lead",
    codename: "Brief Runner",
    mission:
      "Make campaigns executable with requirements, allowed platforms, submission tracking, and review flow.",
    owns: ["Campaign workflow", "Requirements", "Review states"],
    metrics: ["Campaign readiness", "Approved clips", "Exports"],
    nextActions: ["Upgrade Campaign OS", "Add brief cards", "Define approve/reject states"],
    buildResponsibilities: ["campaign config", "review workflow", "export requirements"],
  },
  {
    title: "Automation / Windsurf Release Operator",
    codename: "No-Stall Engine",
    mission:
      "Keep Windsurf/Codex moving through issues, code, validation, commits, PRs, and next slices without stalling.",
    owns: ["Automation prompts", "PR discipline", "Anti-stall rules"],
    metrics: ["PRs shipped", "Failed loops prevented", "Time to merge"],
    nextActions: ["Enforce Issue #146", "Commit coherent slices", "Open PRs with verification"],
    buildResponsibilities: ["execution prompts", "PR templates", "release handoff"],
  },
];

export const brandAssets: BrandAsset[] = [
  {
    name: "Lee-Wuh 16:9 hero",
    path: "/brand/lee-wuh-hero-16x9.png",
    use: "Homepage hero, Whop cover draft, social banner.",
    status: "ready",
  },
  {
    name: "Lee-Wuh avatar",
    path: "/brand/lee-wuh/lee-wuh-avatar.png",
    use: "Loading states, empty states, small dashboard moments.",
    status: "queued",
  },
  {
    name: "Lee-Wuh GLB model",
    path: "/brand/lee-wuh/lee-wuh-mascot.glb",
    use: "Future lightweight 3D mascot viewer.",
    status: "queued",
  },
  {
    name: "Lee-Wuh Rive states",
    path: "/brand/lee-wuh/lee-wuh-states.riv",
    use: "Idle, analyzing, rendering, complete, victory states.",
    status: "queued",
  },
];

export const revenueTiers: RevenueTier[] = [
  {
    name: "Starter Creator",
    price: "$19-$29/mo",
    target: "Solo creators testing clip automation.",
    promise: "Turn long videos into usable clip packs without learning editing software.",
    included: ["Public URL clipping", "Hooks/captions", "Basic clip packaging", "Creator-ready outputs"],
    nextAction: "Confirm launch price and Whop checkout copy.",
  },
  {
    name: "Pro Creator",
    price: "$49-$99/mo",
    target: "Creators posting consistently across TikTok, Instagram, YouTube, and Facebook.",
    promise: "More clips, stronger packaging, and faster review workflow.",
    included: ["More generations", "Priority packaging", "Batch review v0", "Export bundle"],
    nextAction: "Add plan/credit state to frontend surfaces.",
  },
  {
    name: "Agency / Operator",
    price: "$199+/mo",
    target: "Editors, agencies, media teams, and campaign operators.",
    promise: "Run multiple sources, review batches, package campaigns, and manage deliverables.",
    included: ["Campaign OS", "Batch workflows", "Team-style review", "Marketplace/campaign metadata"],
    nextAction: "Build campaign and marketplace surfaces.",
  },
];

export const revenuePipeline: PipelineItem[] = [
  {
    title: "Whop product page",
    owner: "Whop / Revenue Lead",
    status: "building",
    nextAction: "Add Lee-Wuh cover and clear clipping promise.",
    value: "Checkout readiness",
  },
  {
    title: "Demo flow",
    owner: "Sales Operations Lead",
    status: "ready",
    nextAction: "Use one public URL, show clip pack, copy hooks/captions.",
    value: "Sales conversion",
  },
  {
    title: "Investor pipeline",
    owner: "Investor Relations Lead",
    status: "queued",
    nextAction: "Track 25 warm targets and demo follow-ups.",
    value: "Funding opportunities",
  },
  {
    title: "Customer onboarding",
    owner: "Customer Success Lead",
    status: "queued",
    nextAction: "Create first-run checklist and sample source guidance.",
    value: "Activation",
  },
];

export const creativeEngines: CreativeEngine[] = [
  {
    name: "Clipping Engine",
    purpose: "Find and package the strongest short-form moments from long-form sources.",
    status: "live",
    nextAction: "Surface rendered vs strategy-only truth in Command Center.",
  },
  {
    name: "Hook Engine",
    purpose: "Generate interruption-led, curiosity-led, story-led, and controversy-led hooks.",
    status: "building",
    nextAction: "Show hook variants on every clip card.",
  },
  {
    name: "Caption Engine",
    purpose: "Generate caption variants by platform and style.",
    status: "building",
    nextAction: "Expose caption style and copy actions.",
  },
  {
    name: "Thumbnail Text Engine",
    purpose: "Create readable thumbnail/cover text for short-form packages.",
    status: "building",
    nextAction: "Add thumbnail text to lead/result cards.",
  },
  {
    name: "Campaign Export Engine",
    purpose: "Bundle clips, captions, CTAs, requirements, and platform instructions.",
    status: "queued",
    nextAction: "Create metadata-only export rail.",
  },
  {
    name: "Lee-Wuh World Engine",
    purpose: "Power brand-world surfaces, mascot states, character assets, and future 3D layers.",
    status: "queued",
    nextAction: "Build Brand World route and asset table.",
  },
];

export const operationsChecklist: PipelineItem[] = [
  {
    title: "PR #144 mascot hero",
    owner: "QA / Release Lead",
    status: "needs-review",
    nextAction: "Copy local asset and run web build.",
    value: "Brand hero readiness",
  },
  {
    title: "Issue #146 Company OS",
    owner: "Automation / Windsurf Release Operator",
    status: "live",
    nextAction: "Use as master execution gate.",
    value: "No-stall execution",
  },
  {
    title: "Company OS v0",
    owner: "Frontend Creative Director",
    status: "building",
    nextAction: "Create routes and typed config.",
    value: "Unified business/product command surface",
  },
  {
    title: "Command Center v0",
    owner: "CTO / Principal Architect",
    status: "queued",
    nextAction: "Wire source intake, rendered lane, strategy lane, and export rail.",
    value: "Core app operations",
  },
];

export function statusLabel(status: CompanyOsStatus) {
  switch (status) {
    case "live":
      return "Live";
    case "ready":
      return "Ready";
    case "building":
      return "Building";
    case "queued":
      return "Queued";
    case "blocked":
      return "Blocked";
    case "needs-review":
      return "Needs review";
    default:
      return "Unknown";
  }
}

export function statusClasses(status: CompanyOsStatus) {
  switch (status) {
    case "live":
      return "border-emerald-400/30 bg-emerald-400/10 text-emerald-200";
    case "ready":
      return "border-[#C9A24A]/35 bg-[#C9A24A]/10 text-[#E9C77B]";
    case "building":
      return "border-purple-400/30 bg-purple-400/10 text-purple-200";
    case "needs-review":
      return "border-sky-400/30 bg-sky-400/10 text-sky-200";
    case "blocked":
      return "border-red-400/30 bg-red-400/10 text-red-200";
    case "queued":
    default:
      return "border-white/15 bg-white/5 text-white/65";
  }
}
