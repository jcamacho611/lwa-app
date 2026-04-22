import { NextRequest, NextResponse } from "next/server";
import {
  authorizationHeader,
  backendUrl,
  bearerTokenFromRequest,
  guestHeaders,
  guestIdFromRequest,
  parseBackendResponse,
} from "../_lib/backend";

export async function POST(request: NextRequest) {
  let payload: unknown;

  try {
    payload = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  try {
    const requestId =
      payload && typeof payload === "object" && "request_id" in payload && typeof payload.request_id === "string"
        ? payload.request_id.trim()
        : "";
    const token = bearerTokenFromRequest(request);
    const guestId = guestIdFromRequest(request);
    const backendPath = requestId ? `/v1/video-analysis/export/${encodeURIComponent(requestId)}` : "/export-bundle";

    const backendResponse = await fetch(backendUrl(backendPath), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(token),
        ...guestHeaders(guestId),
      },
      body: requestId ? undefined : JSON.stringify(payload),
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
