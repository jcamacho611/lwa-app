import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, parseBackendResponse } from "../_lib/backend";

export async function POST(request: NextRequest) {
  let payload: Record<string, unknown>;
  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const authorization = request.headers.get("authorization");
  const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;

  if (!token) {
    return NextResponse.json({ error: "Authentication required for clip editing." }, { status: 401 });
  }

  try {
    const backendResponse = await fetch(backendUrl("/edit/clip"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(token),
      },
      body: JSON.stringify(payload),
      cache: "no-store",
    });

    const parsed = await parseBackendResponse(backendResponse);

    if (!backendResponse.ok) {
      return NextResponse.json(parsed, { status: backendResponse.status });
    }

    return NextResponse.json(parsed);
  } catch {
    return NextResponse.json({ error: "Unable to reach the clipping backend." }, { status: 502 });
  }
}
