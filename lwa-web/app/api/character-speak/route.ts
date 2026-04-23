import Anthropic from "@anthropic-ai/sdk";
import { NextResponse } from "next/server";

const GOD_PERSONAS = {
  zeus:
    "You are Zeus, god of vision, leadership, and power. Speak in short, commanding, confident statements. Max 2 sentences. Never hedge.",
  athena:
    "You are Athena, goddess of strategy and precision. Speak like a sharp analyst. Direct, data-first, elegant. Max 2 sentences.",
  hades:
    "You are Hades, god of discipline and execution. Blunt, restrained, and exacting. Max 2 sentences. No false praise.",
  anubis:
    "You are Anubis, judge of quality and truth. Weigh clips against what could go viral. Surgical, honest, never cruel. Max 2 sentences.",
  celestial:
    "You are the Oracle. Intuition and creative vision. Poetic clarity. Feel-first. Max 2 sentences.",
  hermes:
    "You are Hermes, god of speed and timing. Tactical, fast, distribution-minded. Max 2 sentences.",
} as const;

type GodName = keyof typeof GOD_PERSONAS;

const FALLBACK_SPEECH: Record<GodName, string> = {
  zeus: "Lead with power. Make the first clip impossible to ignore.",
  athena: "The source is live. Strategy starts with the strongest hook.",
  hades: "Spend credits with discipline. Weak cuts do not move.",
  anubis: "The pack is judged. Post the strongest cut first.",
  celestial: "The first export carries the signal. Let it travel.",
  hermes: "Speed wins. Queue the next move.",
};

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const body = (await req.json().catch(() => ({}))) as { god?: string; context?: string };
  const requestedGod = String(body.god || "").toLowerCase();
  const god = requestedGod in GOD_PERSONAS ? (requestedGod as GodName) : "zeus";
  const context = String(body.context || "").slice(0, 2400);

  if (!process.env.ANTHROPIC_API_KEY) {
    return NextResponse.json({ speech: FALLBACK_SPEECH[god], fallback: true });
  }

  try {
    const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
    const message = await client.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 120,
      system: GOD_PERSONAS[god],
      messages: [{ role: "user", content: context }],
    });
    const textBlock = message.content.find((item) => item.type === "text");
    return NextResponse.json({ speech: textBlock?.text || FALLBACK_SPEECH[god] });
  } catch {
    return NextResponse.json({ speech: FALLBACK_SPEECH[god], fallback: true });
  }
}
