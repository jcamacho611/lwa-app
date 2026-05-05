import type { LeeWuhAnimationState } from "./leeWuhAnimationStates";
import { defaultLeeWuhMoves, getLeeWuhMoves, type LeeWuhMove } from "./leeWuhMoves";

export type LeeWuhRouteIntelligence = {
  route: string;
  title: string;
  intro: string;
  state: LeeWuhAnimationState;
  moves: LeeWuhMove[];
  suggestions: string[];
};

export type LeeWuhChatResponse = {
  message: string;
  state: LeeWuhAnimationState;
  moves: LeeWuhMove[];
};

function includesAny(value: string, terms: string[]) {
  const normalized = value.toLowerCase();
  return terms.some((term) => normalized.includes(term));
}

export function getLeeWuhRouteIntelligence(pathname: string): LeeWuhRouteIntelligence {
  if (pathname.startsWith("/generate")) {
    return {
      route: pathname,
      title: "Source guide",
      intro: "Feed me one source. I will help LWA find what deserves to move.",
      state: "analyzing",
      moves: getLeeWuhMoves(["export_package", "recover_render", "open_company_os", "explore_marketplace"]),
      suggestions: ["What should I upload?", "Why strategy-only?", "How do I export?"],
    };
  }

  if (pathname.startsWith("/marketplace")) {
    return {
      route: pathname,
      title: "Money lane",
      intro: "You want to earn or post work. Pick the lane and make the task clear.",
      state: "marketplaceGuide",
      moves: getLeeWuhMoves(["post_paid_work", "generate_clips", "open_company_os", "enter_realm"]),
      suggestions: ["How do payments work?", "What can I post?", "How does LWA take a cut?"],
    };
  }

  if (pathname.startsWith("/realm") || pathname.startsWith("/game")) {
    return {
      route: pathname,
      title: "Realm guide",
      intro: "This is the world layer. Creation, quests, marketplace, and transparent rewards connect here.",
      state: "realmOpen",
      moves: getLeeWuhMoves(["start_signal_sprint", "generate_clips", "explore_marketplace", "explain_lwa"]),
      suggestions: ["Is this real Bitcoin?", "What is Signal Sprint?", "Where do missions go next?"],
    };
  }

  if (pathname.startsWith("/company-os") || pathname.startsWith("/command-center")) {
    return {
      route: pathname,
      title: "Operator guide",
      intro: "This is the operating layer. Keep generation, revenue, campaigns, and release work connected.",
      state: "thinking",
      moves: getLeeWuhMoves(["generate_clips", "explore_marketplace", "post_paid_work", "explain_lwa"]),
      suggestions: ["What should ship next?", "How does Company OS connect?", "What is incomplete?"],
    };
  }

  if (pathname.startsWith("/lee-wuh") || pathname.startsWith("/brand-world")) {
    return {
      route: pathname,
      title: "Brand world",
      intro: "Lee-Wuh is the living interface layer, not decoration. Keep the character, world, and sword separated.",
      state: "speak",
      moves: getLeeWuhMoves(["generate_clips", "enter_realm", "explore_marketplace", "open_company_os"]),
      suggestions: ["What assets are missing?", "How does Blender fit?", "How should Lee-Wuh move?"],
    };
  }

  if (pathname.startsWith("/revenue")) {
    return {
      route: pathname,
      title: "Revenue guide",
      intro: "Revenue work needs honest claims, clear checkout paths, and no payout promises before implementation.",
      state: "marketplaceGuide",
      moves: getLeeWuhMoves(["post_paid_work", "explore_marketplace", "open_company_os", "generate_clips"]),
      suggestions: ["What can we claim?", "What is payment-ready?", "Where is Whop later?"],
    };
  }

  return {
    route: pathname || "/",
    title: "Living guide",
    intro: "Wussup. Are we creating, earning, entering the realm, or explaining LWA?",
    state: "idle",
    moves: defaultLeeWuhMoves,
    suggestions: ["Create", "Earn", "Enter the realm", "Explain LWA"],
  };
}

export function resolveLeeWuhChatResponse(message: string, pathname: string): LeeWuhChatResponse {
  const route = getLeeWuhRouteIntelligence(pathname);
  const text = message.trim().toLowerCase();

  if (!text) {
    return {
      message: route.intro,
      state: route.state,
      moves: route.moves,
    };
  }

  if (includesAny(text, ["clip", "generate", "upload", "source", "video", "podcast"])) {
    return {
      message:
        "Start with one source. LWA should rank clips by hook strength, coherence, emotional spike, information density, tension payoff, and shareability. Render when possible; keep strategy-only output alive when rendering fails.",
      state: "analyzing",
      moves: getLeeWuhMoves(["generate_clips", "export_package", "recover_render"]),
    };
  }

  if (includesAny(text, ["money", "market", "job", "paid", "work", "earn", "payout"])) {
    return {
      message:
        "The marketplace starts as metadata: task type, payment state, platform fee, LWA cut, creator payout, refund/dispute placeholder. No real escrow or payout automation should be claimed until it exists.",
      state: "marketplaceGuide",
      moves: getLeeWuhMoves(["explore_marketplace", "post_paid_work", "open_company_os"]),
    };
  }

  if (includesAny(text, ["game", "realm", "quest", "signal", "bitcoin", "reward", "mining"])) {
    return {
      message:
        "The realm is opt-in and transparent. Signal Sprint is demo mode: rewards are simulated, no hidden mining, no device-use tricks, and no withdrawable payout until compliance and fraud controls are real.",
      state: "realmOpen",
      moves: getLeeWuhMoves(["enter_realm", "start_signal_sprint", "explain_lwa"]),
    };
  }

  if (includesAny(text, ["blender", "3d", "glb", "asset", "sword", "background", "character"])) {
    return {
      message:
        "Keep the layers separate: character transparent cutout, world background with no character, and Realm Blade prop. Those feed the frontend stage now and Blender/GLB later.",
      state: "speak",
      moves: getLeeWuhMoves(["explain_lwa", "enter_realm", "generate_clips"]),
    };
  }

  if (includesAny(text, ["error", "fail", "fallback", "render", "recover", "broken"])) {
    return {
      message:
        "Fallback is a product rule. FFmpeg or rendering can fail, but ranked strategy output, hooks, captions, timestamps, and recovery guidance should still be useful.",
      state: "error",
      moves: getLeeWuhMoves(["recover_render", "export_package", "generate_clips"]),
    };
  }

  return {
    message:
      "LWA is the upload-first creator engine plus Company OS. Lee-Wuh routes the experience: create clips, earn through marketplace tasks, enter the realm, or inspect the operating system.",
    state: "thinking",
    moves: route.moves,
  };
}
