import type { LeeWuhAnimationState } from "./leeWuhAnimationStates";

export type LeeWuhMoveId =
  | "generate_clips"
  | "explore_marketplace"
  | "post_paid_work"
  | "enter_realm"
  | "start_signal_sprint"
  | "open_company_os"
  | "explain_lwa"
  | "recover_render"
  | "export_package";

export type LeeWuhMove = {
  id: LeeWuhMoveId;
  label: string;
  href: string;
  detail: string;
  state: LeeWuhAnimationState;
  category: "create" | "earn" | "operate" | "realm" | "recover" | "explain";
};

export const leeWuhMoves: Record<LeeWuhMoveId, LeeWuhMove> = {
  generate_clips: {
    id: "generate_clips",
    label: "Generate clips",
    href: "/generate",
    detail: "Upload or paste one source and let LWA rank the strongest clip moments.",
    state: "analyzing",
    category: "create",
  },
  explore_marketplace: {
    id: "explore_marketplace",
    label: "Explore marketplace",
    href: "/marketplace",
    detail: "Find creator tasks, campaign work, and future offer lanes.",
    state: "marketplaceGuide",
    category: "earn",
  },
  post_paid_work: {
    id: "post_paid_work",
    label: "Draft paid task",
    href: "/marketplace/post-job",
    detail: "Draft a prepaid or partially paid creator task with clear work metadata.",
    state: "marketplaceGuide",
    category: "earn",
  },
  enter_realm: {
    id: "enter_realm",
    label: "Enter realm",
    href: "/realm",
    detail: "Open the Lee-Wuh world layer for quests, missions, and game routing.",
    state: "realmOpen",
    category: "realm",
  },
  start_signal_sprint: {
    id: "start_signal_sprint",
    label: "Start Signal Sprint",
    href: "/game",
    detail: "Play the demo game shell. Rewards are simulated and not withdrawable.",
    state: "realmOpen",
    category: "realm",
  },
  open_company_os: {
    id: "open_company_os",
    label: "Open Company OS",
    href: "/company-os",
    detail: "Review the operating system for product, brand, revenue, and release work.",
    state: "thinking",
    category: "operate",
  },
  explain_lwa: {
    id: "explain_lwa",
    label: "Explain LWA",
    href: "/brand-world",
    detail: "See how the product, company OS, and Lee-Wuh brand layer fit together.",
    state: "speak",
    category: "explain",
  },
  recover_render: {
    id: "recover_render",
    label: "Recover render",
    href: "/generate",
    detail: "If rendering fails, keep the ranked strategy pack and retry recovery when available.",
    state: "error",
    category: "recover",
  },
  export_package: {
    id: "export_package",
    label: "Export package",
    href: "/generate",
    detail: "Package clips, captions, hooks, timestamps, metadata, and strategy notes.",
    state: "victory",
    category: "create",
  },
};

export const defaultLeeWuhMoves: LeeWuhMove[] = [
  leeWuhMoves.generate_clips,
  leeWuhMoves.explore_marketplace,
  leeWuhMoves.post_paid_work,
  leeWuhMoves.enter_realm,
  leeWuhMoves.open_company_os,
];

export function getLeeWuhMoves(ids: LeeWuhMoveId[]) {
  return ids.map((id) => leeWuhMoves[id]);
}
