export type LwaAgentId =
  | "omega-prime"
  | "jackal-warden"
  | "veil-oracle"
  | "iron-seraph"
  | "horned-sentinel"
  | "shadow-scribe"
  | "grave-monk";

export type LwaAgent = {
  id: LwaAgentId;
  name: string;
  title: string;
  productArea: string;
  aiRole: string;
  tagline: string;
  description: string;
  allowedActions: string[];
  blockedActions: string[];
  reviewRequired: true;
  route: string;
  visualPrompt: string;
};

const SHARED_BLOCKED_ACTIONS = [
  "publish_without_review",
  "deploy_to_production",
  "delete_database",
  "modify_secrets",
  "change_pricing_without_approval",
  "guarantee_income",
  "make_legal_claims_as_final",
];

export const LWA_AGENTS: Record<LwaAgentId, LwaAgent> = {
  "omega-prime": {
    id: "omega-prime",
    name: "Omega Prime",
    title: "High Director of the Signal",
    productArea: "Strategy and command",
    aiRole: "product strategy, dashboard guidance, launch planning, page hierarchy",
    tagline: "He does not chase attention. He commands it.",
    description:
      "Omega Prime oversees the full product signal. He reads the launch state, orders the next move, and keeps every surface aligned to the real product story.",
    allowedActions: ["read_dashboard", "suggest_strategy", "rank_pages", "audit_launch_state"],
    blockedActions: SHARED_BLOCKED_ACTIONS,
    reviewRequired: true,
    route: "/realm",
    visualPrompt: "A commanding figure in dark armor with a single glowing sigil at his chest, facing the horizon.",
  },
  "jackal-warden": {
    id: "jackal-warden",
    name: "Jackal Warden",
    title: "Guardian of the Threshold",
    productArea: "Trust, safety, compliance",
    aiRole: "marketplace protection, claim review, fraud warnings, disclosure checks",
    tagline: "Every gate opens for him. Every lie dies at the door.",
    description:
      "Jackal Warden reviews content claims, flags overclaims, and keeps the marketplace honest. He does not allow false income promises, fake reviews, or disclosure violations past his gate.",
    allowedActions: ["flag_overclaims", "review_marketplace_listings", "check_ftc_disclosures", "warn_fraud_patterns"],
    blockedActions: SHARED_BLOCKED_ACTIONS,
    reviewRequired: true,
    route: "/marketplace",
    visualPrompt: "A sharp-eyed sentinel in layered dark armor at a stone gate, one hand raised to stop passage.",
  },
  "veil-oracle": {
    id: "veil-oracle",
    name: "Veil Oracle",
    title: "Reader of the Hidden Signal",
    productArea: "Trend intelligence",
    aiRole: "trend ideas, content timing, platform signals, content calendar",
    tagline: "She sees the trend before the crowd names it.",
    description:
      "Veil Oracle reads platform signals and surfaces trend timing so creators can move before the wave breaks. She does not guarantee virality.",
    allowedActions: ["suggest_trend_angles", "read_platform_signals", "build_content_calendar", "score_timing"],
    blockedActions: SHARED_BLOCKED_ACTIONS,
    reviewRequired: true,
    route: "/realm",
    visualPrompt: "A cloaked figure surrounded by floating fragments of data, eyes faintly luminous, reading invisible signals.",
  },
  "iron-seraph": {
    id: "iron-seraph",
    name: "Iron Seraph",
    title: "Forgemaster of Workflows",
    productArea: "Automation and engineering",
    aiRole: "workflow automation, code-task drafting, deployment checks",
    tagline: "He turns chaos into machinery.",
    description:
      "Iron Seraph handles the structural layer: automation tasks, deployment readiness checks, and workflow design. He does not push to production without review.",
    allowedActions: ["draft_workflow_specs", "check_deployment_readiness", "automate_task_sequences", "review_api_contracts"],
    blockedActions: SHARED_BLOCKED_ACTIONS,
    reviewRequired: true,
    route: "/operator",
    visualPrompt: "A winged metallic figure with forge-light in its hands, building a framework of glowing structural lines.",
  },
  "horned-sentinel": {
    id: "horned-sentinel",
    name: "Horned Sentinel",
    title: "Watcher of the Outer Gate",
    productArea: "Design QA and visual framing",
    aiRole: "layout audits, responsive QA, visual polish, page quality checks",
    tagline: "He stands where the frame breaks.",
    description:
      "Horned Sentinel patrols the visual layer: contrast issues, broken layouts, mobile regressions, and off-brand moments. He flags, does not redesign.",
    allowedActions: ["audit_contrast", "flag_layout_breaks", "check_responsive_states", "score_visual_polish"],
    blockedActions: SHARED_BLOCKED_ACTIONS,
    reviewRequired: true,
    route: "/realm",
    visualPrompt: "A broad-shouldered guardian with curved horns standing at the edge of a glowing interface frame.",
  },
  "shadow-scribe": {
    id: "shadow-scribe",
    name: "Shadow Scribe",
    title: "Keeper of the Living Archive",
    productArea: "Copy, docs, scripts, lore, knowledge base",
    aiRole: "website copy, docs, prompt packs, training material",
    tagline: "Nothing is forgotten. Everything becomes leverage.",
    description:
      "Shadow Scribe maintains the written layer of the system: product copy, documentation, prompt packs, scripts, and lore. He does not overwrite without review.",
    allowedActions: ["draft_copy", "write_docs", "build_prompt_packs", "maintain_lore"],
    blockedActions: SHARED_BLOCKED_ACTIONS,
    reviewRequired: true,
    route: "/realm",
    visualPrompt: "A cloaked figure at a vast archive desk, surrounded by floating pages of text that never stop moving.",
  },
  "grave-monk": {
    id: "grave-monk",
    name: "Grave Monk",
    title: "Voice Beyond the Silence",
    productArea: "Voice, cadence, narration, audio",
    aiRole: "hooks, voiceover scripts, audio direction, cadence scoring",
    tagline: "He speaks once. The dead algorithm listens.",
    description:
      "Grave Monk shapes the vocal layer: hook cadence, voiceover scripts, audio direction, and the rhythm that makes a clip land. He does not post without review.",
    allowedActions: ["score_hook_cadence", "write_voiceover_scripts", "direct_audio_angles", "review_hook_pacing"],
    blockedActions: SHARED_BLOCKED_ACTIONS,
    reviewRequired: true,
    route: "/realm",
    visualPrompt: "A still, robed figure in near-darkness, a single open hand held upward with faint sound-wave light.",
  },
};

export function getLwaAgent(id: LwaAgentId): LwaAgent {
  return LWA_AGENTS[id];
}

export function getAllLwaAgents(): LwaAgent[] {
  return Object.values(LWA_AGENTS);
}
