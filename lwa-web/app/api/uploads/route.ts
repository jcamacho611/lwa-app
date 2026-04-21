import { NextRequest, NextResponse } from "next/server";
import { GUEST_ID_COOKIE, authorizationHeader, backendUrl, guestHeaders, guestIdFromRequest, parseBackendResponse } from "../_lib/backend";

export async function GET(request: NextRequest) {
  const authorization = request.headers.get("authorization");
  const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;

  if (!token) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  try {
    const response = await fetch(backendUrl("/v1/uploads"), {
      headers: {
        ...authorizationHeader(token),
      },
      cache: "no-store",
    });
    const data = await parseBackendResponse(response);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to load uploads right now." }, { status: 502 });
  }
}

export async function POST(request: NextRequest) {
  const authorization = request.headers.get("authorization");
  const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;
  const guestId = token ? null : guestIdFromRequest(request);

  try {
    const formData = await request.formData();
    const backendResponse = await fetch(backendUrl("/v1/uploads"), {
      method: "POST",
      headers: {
        ...authorizationHeader(token),
        ...guestHeaders(guestId),
      },
      body: formData,
      cache: "no-store",
    });
    const data = await parseBackendResponse(backendResponse);
    const response = NextResponse.json(data, { status: backendResponse.status });
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
    return NextResponse.json({ detail: "Unable to upload file right now." }, { status: 502 });
  }
}
