import { NextRequest, NextResponse } from "next/server";
import { AI_COPY_SYSTEM_PROMPT } from "../../../lib/ai-copy-config";

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => null);

  if (!body?.prompt) {
    return NextResponse.json({ error: "Missing prompt" }, { status: 400 });
  }

  return NextResponse.json({
    system: AI_COPY_SYSTEM_PROMPT,
    received: body,
    note: "Wire this route to your preferred server-side model call or existing backend AI layer. Do not expose secrets in the client.",
  });
}
