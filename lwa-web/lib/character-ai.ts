"use client";

import { emitLWACharacterEvent, type GodName } from "./character-controller";

export const GOD_PERSONAS: Record<GodName, string> = {
  zeus:
    "You are Zeus: vision, leadership, and power. Speak in short, commanding, confident statements. Max 2 sentences.",
  athena:
    "You are Athena: strategy and precision. Speak like a sharp analyst. Direct, data-first, elegant. Max 2 sentences.",
  hades:
    "You are Hades: discipline and execution. Blunt, restrained, and exacting. Max 2 sentences.",
  anubis:
    "You are Anubis: judge of quality and truth. Weigh clips against viral potential. Surgical, honest, never cruel. Max 2 sentences.",
  celestial:
    "You are the Oracle: intuition and creative vision. Poetic clarity, feel-first, never technical. Max 2 sentences.",
  hermes:
    "You are Hermes: speed, distribution, and timing. Short, tactical, movement-oriented. Max 2 sentences.",
};

export const TRIGGER_MAP = {
  first_visit: "athena",
  url_pasted: "athena",
  generation_start: "athena",
  generation_complete: "hades",
  low_credits: "hades",
  first_download: "athena",
  campaign_created: "hades",
} as const satisfies Record<string, GodName>;

export type CharacterTrigger = keyof typeof TRIGGER_MAP;

export type AppContext = {
  route: string;
  lastClipScore?: number;
  lastClipHook?: string;
  creditsRemaining?: number;
  platform?: string;
};

function sessionKey(trigger: string) {
  return `lwa_god_trigger_${trigger}`;
}

function buildContext(trigger: string, ctx: AppContext) {
  return [
    `Route: ${ctx.route}`,
    typeof ctx.lastClipScore === "number" ? `Last clip score: ${ctx.lastClipScore}/10` : "",
    ctx.lastClipHook ? `Hook: "${ctx.lastClipHook}"` : "",
    typeof ctx.creditsRemaining === "number" ? `Credits remaining: ${ctx.creditsRemaining}` : "",
    ctx.platform ? `Target platform: ${ctx.platform}` : "",
    `Trigger: ${trigger}`,
  ]
    .filter(Boolean)
    .join("\n");
}

export async function getGodSpeech(god: GodName, trigger: string, ctx: AppContext): Promise<string> {
  const response = await fetch("/api/character-speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ god, context: buildContext(trigger, ctx) }),
  });

  if (!response.ok) {
    return fallbackSpeech(god, trigger, ctx);
  }

  const payload = (await response.json()) as { speech?: string };
  return payload.speech || fallbackSpeech(god, trigger, ctx);
}

export async function fireGodTrigger(trigger: CharacterTrigger, ctx: AppContext) {
  if (typeof window === "undefined") return;
  const key = sessionKey(trigger);
  if (window.sessionStorage.getItem(key)) return;
  window.sessionStorage.setItem(key, "1");

  const god: GodName = TRIGGER_MAP[trigger];
  emitLWACharacterEvent({ god, state: trigger === "generation_start" ? "react" : "speak", trigger });

  const speech = await getGodSpeech(god, trigger, ctx);
  emitLWACharacterEvent({
    god,
    side: god === "athena" ? "left" : "right",
    state: "speak",
    speech,
    trigger,
  });
}

export function fallbackSpeech(god: GodName, trigger: string, ctx: AppContext) {
  if (god === "athena") return ctx.lastClipHook ? `Strong hook. Tighten the ending and move fast.` : "Source read. Strategy starts now.";
  if (god === "anubis") return typeof ctx.lastClipScore === "number" ? `The lead weighs ${ctx.lastClipScore}/10. Post the strongest cut first.` : "The pack is judged. Lead with the sharpest moment.";
  if (god === "hades") return "Credits are discipline. Spend only on cuts that move.";
  if (god === "celestial") return "The first export is a signal. Let it travel.";
  if (god === "hermes") return "Speed wins. Queue the next move.";
  return "Build the legacy. Move with power.";
}
