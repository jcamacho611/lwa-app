import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, bearerTokenFromRequest, parseBackendResponse } from "../../../_lib/backend";

type RouteContext = {
  params: Promise<{ campaignId: string }>;
};

export async function POST(request: NextRequest, context: RouteContext) {
  const token = bearerTokenFromRequest(request);

  if (!token) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  try {
    const { campaignId } = await context.params;
    const payload = await request.json();
    const response = await fetch(backendUrl(`/v1/campaigns/${campaignId}/assignments`), {
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
    return NextResponse.json({ detail: "Unable to create campaign assignments right now." }, { status: 502 });
  }
}
