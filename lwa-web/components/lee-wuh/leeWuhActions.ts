import { defaultLeeWuhMoves, leeWuhMoves, type LeeWuhMove } from "./leeWuhMoves";
import { getLeeWuhRouteIntelligence } from "./leeWuhIntelligence";
import type { LeeWuhAnimationState } from "./leeWuhAnimationStates";

export type LeeWuhMood = LeeWuhAnimationState;

export type LeeWuhAction = LeeWuhMove;

export type LeeWuhRouteMode = {
  route: string;
  intro: string;
  actions: LeeWuhAction[];
};

export const defaultLeeWuhActions: LeeWuhAction[] = defaultLeeWuhMoves;

export const leeWuhRouteModes: LeeWuhRouteMode[] = [
  {
    route: "/",
    intro: "Wussup. You trying to create, earn, or enter the world?",
    actions: defaultLeeWuhActions,
  },
  {
    route: "/generate",
    intro: "Feed me one source. I will help LWA find what deserves to move.",
    actions: [leeWuhMoves.generate_clips, leeWuhMoves.export_package, leeWuhMoves.recover_render],
  },
  {
    route: "/marketplace",
    intro: "You want to earn or post work? Pick the money lane.",
    actions: [leeWuhMoves.post_paid_work, leeWuhMoves.explore_marketplace, leeWuhMoves.generate_clips],
  },
  {
    route: "/realm",
    intro: "Step through the gate. This is where the world starts breathing.",
    actions: [leeWuhMoves.start_signal_sprint, leeWuhMoves.generate_clips, leeWuhMoves.explore_marketplace],
  },
];

export function getLeeWuhMode(pathname: string): LeeWuhRouteMode {
  const route = getLeeWuhRouteIntelligence(pathname);
  return {
    route: route.route,
    intro: route.intro,
    actions: route.moves,
  };
}

export function leeWuhMoodLine(mood: LeeWuhMood) {
  switch (mood) {
    case "analyzing":
      return "One source. Best moments first. Let us move.";
    case "marketplaceGuide":
      return "The marketplace is where work turns into money.";
    case "realmOpen":
      return "The gate is open. The world starts here.";
    case "victory":
      return "The package is ready for review or export.";
    case "error":
      return "Recover what can render and keep strategy output useful.";
    case "thinking":
      return "Choose the lane and I will guide the next step.";
    default:
      return "Wussup. Where we starting?";
  }
}
