import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, bearerTokenFromRequest, parseBackendResponse } from "../../_lib/backend";

type RouteContext = {
  params: Promise<{ campaignId: string }>;
};

export async function GET(request: NextRequest, context: RouteContext) {
  const token = bearerTokenFromRequest(request);

  if (!token) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  try {
    const { campaignId } = await context.params;
    const response = await fetch(backendUrl(`/v1/campaigns/${campaignId}`), {
      headers: {
        ...authorizationHeader(token),
      },
      cache: "no-store",
    });
    const data = await parseBackendResponse(response);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to load campaign detail right now." }, { status: 502 });
  }
}

export async function PATCH(request: NextRequest, context: RouteContext) {
  const token = bearerTokenFromRequest(request);

  if (!token) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  try {
    const { campaignId } = await context.params;
    const payload = await request.json();
    const response = await fetch(backendUrl(`/v1/campaigns/${campaignId}`), {
      method: "PATCH",
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
    return NextResponse.json({ detail: "Unable to update campaign right now." }, { status: 502 });
  }
}
