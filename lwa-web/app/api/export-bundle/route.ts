import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, bearerTokenFromRequest, parseBackendResponse } from "../_lib/backend";

export async function POST(request: NextRequest) {
  let payload: unknown;

  try {
    payload = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  try {
    const backendResponse = await fetch(backendUrl("/export-bundle"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(bearerTokenFromRequest(request)),
      },
      body: JSON.stringify(payload),
      cache: "no-store",
    });

    const parsed = await parseBackendResponse(backendResponse);

    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: parsed?.detail || parsed?.error || "Unable to export that clip bundle right now." },
        { status: backendResponse.status },
      );
    }

    return NextResponse.json(parsed, { status: 200 });
  } catch {
    return NextResponse.json({ error: "Unable to reach the clipping backend right now." }, { status: 502 });
  }
}
