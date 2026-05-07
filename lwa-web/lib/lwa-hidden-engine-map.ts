export type LwaHiddenEngineStatus =
  | "documented"
  | "frontend-foundation"
  | "partial-backend"
  | "planned";

export type LwaHiddenEngine = {
  id: string;
  name: string;
  category: string;
  purpose: string;
  whyItMatters: string;
  frontendResponsibility: string;
  backendResponsibility: string;
  firstSafeSlice: string;
  launchRiskIfIgnored: string;
  status: LwaHiddenEngineStatus;
};

export const priorityHiddenEngineIds = [
  "experience-state",
  "mission-orchestration",
  "asset-registry",
  "recovery",
] as const;

export const lwaHiddenEngineMap: LwaHiddenEngine[] = [
  {
    id: "experience-state",
    name: "Experience State Engine",
    category: "state",
    purpose: "Controls the current product state across Lee-Wuh, UI, missions, rewards, and realm surfaces.",
    whyItMatters: "It makes LWA feel like one living workflow instead of disconnected pages.",
    frontendResponsibility: "Apply local events, show guidance, update Lee-Wuh reactions, and expose next actions.",
    backendResponsibility: "Emit durable job, render, proof, entitlement, and recovery events later.",
    firstSafeSlice: "Typed local state/event reducer and demo wiring on the Lee-Wuh asset page.",
    launchRiskIfIgnored: "Lee-Wuh stays decorative and users lose the path after generation or fallback.",
    status: "frontend-foundation",
  },
  {
    id: "mission-orchestration",
    name: "Mission Orchestration Engine",
    category: "missions",
    purpose: "Chooses the next best user action and turns creator work into missions.",
    whyItMatters: "It bridges clipping, proof, marketplace, rewards, and realm progression.",
    frontendResponsibility: "Show active missions, complete demo missions from events, and display safe non-monetary rewards.",
    backendResponsibility: "Persist mission completion, enforce anti-abuse rules, and connect to account history later.",
    firstSafeSlice: "Starter local missions for clips rendered, proof, marketplace, realm, and recovery.",
    launchRiskIfIgnored: "The game layer becomes separate from actual creator work.",
    status: "frontend-foundation",
  },
  {
    id: "asset-registry",
    name: "Asset Registry Engine",
    category: "assets",
    purpose: "Tracks Lee-Wuh character, sword, background, aura, GLB, Blender, Spine, and runtime assets.",
    whyItMatters: "Separated assets are required for real animation, composition, and future rigging.",
    frontendResponsibility: "Display asset status, runtime safety, source-only files, fallbacks, and production candidates.",
    backendResponsibility: "Validate generated asset metadata, store versions, expose asset health, and enforce safe usage later.",
    firstSafeSlice: "Use the existing Lee-Wuh visual registry and expose the discipline in the engine map.",
    launchRiskIfIgnored: "The team ships baked screenshots or duplicate assets that cannot animate cleanly.",
    status: "frontend-foundation",
  },
  {
    id: "recovery",
    name: "Recovery Engine",
    category: "reliability",
    purpose: "Turns failures, strategy-only results, missing renders, provider errors, and export issues into recoverable paths.",
    whyItMatters: "LWA must preserve useful strategy output when rendering or providers fail.",
    frontendResponsibility: "Guide users to retry render, export strategy, use fallback, or save proof ideas.",
    backendResponsibility: "Return recovery codes, retry options, provider downgrade hints, and recovery artifacts later.",
    firstSafeSlice: "Local `RECOVERY_AVAILABLE` event and recovery mission without backend changes.",
    launchRiskIfIgnored: "Errors feel final even when useful output exists.",
    status: "frontend-foundation",
  },
  {
    id: "reward-ledger",
    name: "Reward Ledger Engine",
    category: "progression",
    purpose: "Tracks XP, badges, relics, completed missions, unlocks, and creator progression.",
    whyItMatters: "Progression needs a ledger before users believe rewards matter.",
    frontendResponsibility: "Show safe local/demo rewards without implying cash, crypto, or payout value.",
    backendResponsibility: "Persist idempotent reward records and prevent farming later.",
    firstSafeSlice: "Return local reward payloads from experience and mission events.",
    launchRiskIfIgnored: "Users experience rewards as fake or reset-prone.",
    status: "documented",
  },
  {
    id: "proof-trust",
    name: "Proof / Trust Engine",
    category: "trust",
    purpose: "Records what was generated, copied, exported, saved, submitted, or recovered.",
    whyItMatters: "Marketplace, campaigns, reputation, disputes, and confidence need a history of product actions.",
    frontendResponsibility: "Label proof actions honestly and avoid claiming verified submissions without backend confirmation.",
    backendResponsibility: "Persist proof events, source references, manifests, timestamps, and audit trails later.",
    firstSafeSlice: "Use proof as a mission trigger only.",
    launchRiskIfIgnored: "Campaign and marketplace trust will break when users need evidence.",
    status: "partial-backend",
  },
  {
    id: "cost-governance",
    name: "Cost Governance Engine",
    category: "business",
    purpose: "Controls provider cost, credits, free fallbacks, render limits, and plan gates.",
    whyItMatters: "AI, render, video, and storage calls can burn money quickly.",
    frontendResponsibility: "Reflect plan limits and downgrade paths without promising unsupported output.",
    backendResponsibility: "Make cost decisions server-side, enforce quotas, route to fallback, and log spend.",
    firstSafeSlice: "Document ownership and keep UI language compatible with future credit gates.",
    launchRiskIfIgnored: "Users can trigger expensive work without business controls.",
    status: "partial-backend",
  },
  {
    id: "provider-routing",
    name: "Provider Routing Engine",
    category: "providers",
    purpose: "Chooses mock, free, premium, render, video, image, text, or local deterministic providers.",
    whyItMatters: "Provider routing executes decisions while Director Brain decides what should happen.",
    frontendResponsibility: "Display provider-neutral statuses like strategy-only, rendering, rendered, and fallback.",
    backendResponsibility: "Route calls by plan, cost, health, reliability, latency, and output type.",
    firstSafeSlice: "Document the engine without moving provider decisions into the frontend.",
    launchRiskIfIgnored: "Provider failures leak into UX and operating cost becomes hard to control.",
    status: "partial-backend",
  },
  {
    id: "quality-scoring",
    name: "Quality Scoring Engine",
    category: "intelligence",
    purpose: "Scores hook strength, platform fit, retention, caption quality, render readiness, marketplace fit, and confidence.",
    whyItMatters: "LWA must decide what to post first, recover later, export, block, or send to marketplace.",
    frontendResponsibility: "Show score transparency and next-action logic without inventing guarantees.",
    backendResponsibility: "Use Attention Compiler, feedback, proof, and performance logs to calibrate decisions.",
    firstSafeSlice: "Document the engine and keep score language aligned with existing score breakdowns.",
    launchRiskIfIgnored: "Clip rank and next actions become hard to justify.",
    status: "partial-backend",
  },
  {
    id: "rights-safety",
    name: "Rights / Safety Engine",
    category: "safety",
    purpose: "Checks source rights, posting safety, campaign eligibility, claims, marketplace risk, and payout safety.",
    whyItMatters: "Money and marketplace workflows need rights safety before scale.",
    frontendResponsibility: "Avoid unsupported claims about bypassing private sources, direct posting, or payout automation.",
    backendResponsibility: "Classify source risk, enforce allowed flows, attach warnings, and block unsafe marketplace proof.",
    firstSafeSlice: "Document the engine and keep claim-safe copy.",
    launchRiskIfIgnored: "LWA takes avoidable legal, platform, and marketplace trust risk.",
    status: "planned",
  },
  {
    id: "game-economy",
    name: "Game Economy Balancing Engine",
    category: "realm",
    purpose: "Balances XP, missions, relic rarity, realm progression, streaks, anti-spam, and unlock pacing.",
    whyItMatters: "Credits and wallet are business systems. Realm progression needs separate pacing.",
    frontendResponsibility: "Display non-monetary progression and keep reward language claim-safe.",
    backendResponsibility: "Persist progression, tune XP, prevent farming, and balance unlocks later.",
    firstSafeSlice: "Keep starter reward values local and non-monetary.",
    launchRiskIfIgnored: "Users progress too fast, get bored, or exploit rewards.",
    status: "documented",
  },
  {
    id: "personalization-memory",
    name: "Personalization / Memory Engine",
    category: "memory",
    purpose: "Learns user style, niche, platform preferences, successful outputs, and Lee-Wuh guidance behavior.",
    whyItMatters: "LWA should become more relevant after repeated use.",
    frontendResponsibility: "Use only safe local preferences until account-backed memory exists.",
    backendResponsibility: "Store user preferences, performance patterns, saved styles, and successful hooks under account controls later.",
    firstSafeSlice: "Document the engine and leave persistence for a later backend-backed slice.",
    launchRiskIfIgnored: "Every user receives the same generic guidance.",
    status: "planned",
  },
];
