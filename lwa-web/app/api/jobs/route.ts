import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, guestHeaders, guestIdFromRequest, parseBackendResponse, GUEST_ID_COOKIE } from "../_lib/backend";

export async function POST(request: NextRequest) {
  let payload: Record<string, unknown>;
  try {
    payload = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const authorization = request.headers.get("authorization");
  const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;
  const guestId = token ? null : guestIdFromRequest(request);

  try {
    const backendResponse = await fetch(backendUrl("/v1/jobs"), {
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

    if (!backendResponse.ok) {
      return NextResponse.json(parsed, { status: backendResponse.status });
    }

    const response = NextResponse.json(parsed, { status: 202 });
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
    return NextResponse.json({ error: "Unable to reach the clipping backend." }, { status: 502 });
  }
}
