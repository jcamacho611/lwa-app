import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, parseBackendResponse } from "../../_lib/backend";

type RouteContext = {
  params: Promise<{
    clipId: string;
  }>;
};

function bearerTokenFromRequest(request: NextRequest) {
  const authorization = request.headers.get("authorization");
  return authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;
}

export async function GET(request: NextRequest, context: RouteContext) {
  const { clipId } = await context.params;
  const requestId = request.nextUrl.searchParams.get("request_id");
  const query = requestId ? `?request_id=${encodeURIComponent(requestId)}` : "";
  const token = bearerTokenFromRequest(request);

  try {
    const response = await fetch(backendUrl(`/v1/clip-status/${encodeURIComponent(clipId)}${query}`), {
      method: "GET",
      headers: authorizationHeader(token),
      cache: "no-store",
    });
    const data = await parseBackendResponse(response);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to load clip status right now." }, { status: 502 });
  }
}

export async function POST(request: NextRequest, context: RouteContext) {
  const { clipId } = await context.params;
  const requestId = request.nextUrl.searchParams.get("request_id");
  const query = requestId ? `?request_id=${encodeURIComponent(requestId)}` : "";
  const token = bearerTokenFromRequest(request);

  try {
    const response = await fetch(backendUrl(`/v1/clip-status/${encodeURIComponent(clipId)}/render${query}`), {
      method: "POST",
      headers: authorizationHeader(token),
      cache: "no-store",
    });
    const data = await parseBackendResponse(response);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to retry clip render right now." }, { status: 502 });
  }
}
