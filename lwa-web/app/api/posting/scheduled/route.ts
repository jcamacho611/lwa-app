import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, bearerTokenFromRequest, parseBackendResponse } from "../../_lib/backend";

export async function GET(request: NextRequest) {
  const token = bearerTokenFromRequest(request);

  if (!token) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  try {
    const response = await fetch(backendUrl("/v1/posting/scheduled"), {
      headers: {
        ...authorizationHeader(token),
      },
      cache: "no-store",
    });
    const data = await parseBackendResponse(response);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to load scheduled posts right now." }, { status: 502 });
  }
}

export async function POST(request: NextRequest) {
  const token = bearerTokenFromRequest(request);

  if (!token) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  try {
    const payload = await request.json();
    const response = await fetch(backendUrl("/v1/posting/scheduled"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(token),
      },
      body: JSON.stringify(payload),
      cache: "no-store",
    });
    const data = await parseBackendResponse(response);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to create a scheduled post right now." }, { status: 502 });
  }
}
