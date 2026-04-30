export type CouncilRoleId =
  | "founder"
  | "product-architect"
  | "engineer"
  | "ai-media"
  | "game-systems"
  | "design"
  | "marketplace-ops"
  | "blockchain"
  | "legal";

export type CouncilRole = {
  id: CouncilRoleId;
  realTitle: string;
  mythicTitle: string;
  owns: string;
};

export const PRODUCTION_COUNCIL: Record<CouncilRoleId, CouncilRole> = {
  founder: {
    id: "founder",
    realTitle: "Founder",
    mythicTitle: "High Director",
    owns: "vision, brand, capital, partnerships, final product direction",
  },
  "product-architect": {
    id: "product-architect",
    realTitle: "Product Architect",
    mythicTitle: "Architect of Realms",
    owns: "product structure, roadmap, user flows, system architecture",
  },
  engineer: {
    id: "engineer",
    realTitle: "Principal Full-Stack Engineer",
    mythicTitle: "Hand of the Director",
    owns: "website, backend, dashboard, APIs, database, deployment",
  },
  "ai-media": {
    id: "ai-media",
    realTitle: "AI Media Pipeline Engineer",
    mythicTitle: "Forgemaster of Signals",
    owns: "clipping, transcription, captions, hooks, scoring, rendering",
  },
  "game-systems": {
    id: "game-systems",
    realTitle: "Game Systems Designer",
    mythicTitle: "Loremaster of the Realms",
    owns: "classes, factions, XP, quests, progression, world logic",
  },
  design: {
    id: "design",
    realTitle: "UI/UX Designer",
    mythicTitle: "Veilwright",
    owns: "premium dark design, clarity, ease of use",
  },
  "marketplace-ops": {
    id: "marketplace-ops",
    realTitle: "Marketplace Ops",
    mythicTitle: "Auditor",
    owns: "sellers, payouts, disputes, trust, fraud prevention, marketplace rules",
  },
  blockchain: {
    id: "blockchain",
    realTitle: "Blockchain Engineer",
    mythicTitle: "Sigilbearer",
    owns: "optional proof systems, badges, relics, wallets, provenance",
  },
  legal: {
    id: "legal",
    realTitle: "Legal Compliance",
    mythicTitle: "Keeper of the Charter",
    owns: "terms, privacy, creator rules, FTC language, compliance",
  },
};

export const COUNCIL_BRAND_LINE = "The Council builds the system. The characters guide the world.";

export function getAllCouncilRoles(): CouncilRole[] {
  return Object.values(PRODUCTION_COUNCIL);
}
