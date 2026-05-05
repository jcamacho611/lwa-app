import { NextRequest, NextResponse } from "next/server";
import {
  GUEST_ID_COOKIE,
  authorizationHeader,
  backendUrl,
  guestHeaders,
  guestIdFromRequest,
  parseBackendResponse,
} from "../../_lib/backend";

export async function POST(request: NextRequest) {
  let payload: unknown;

  try {
    payload = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const authorization = request.headers.get("authorization");
  const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;
  const guestId = token ? null : guestIdFromRequest(request);

  try {
    const backendResponse = await fetch(backendUrl("/v1/generate-analysis"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(token),
        ...guestHeaders(guestId),
      },
      body: JSON.stringify(payload),
      cache: "no-store",
    });

    const parsed = await parseBackendResponse(backendResponse);
    const response = NextResponse.json(parsed, { status: backendResponse.status });
    if (guestId) {
      response.cookies.set(GUEST_ID_COOKIE, guestId, {
        httpOnly: true,
        sameSite: "lax",
        path: "/",
        maxAge: 60 * 60 * 24 * 30,
      });
    }
    return response;
  } catch {
    return NextResponse.json(
      { error: "Unable to reach the clipping backend right now. Try again in a moment." },
      { status: 502 },
    );
  }
}
