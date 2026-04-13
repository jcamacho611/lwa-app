import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, parseBackendResponse } from "../../../_lib/backend";

type RouteContext = {
  params: Promise<{
    requestId: string;
  }>;
};

export async function GET(request: NextRequest, context: RouteContext) {
  const authorization = request.headers.get("authorization");
  const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;

  if (!token) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  const { requestId } = await context.params;

  try {
    const response = await fetch(backendUrl(`/v1/me/clip-packs/${requestId}`), {
      headers: {
        ...authorizationHeader(token),
      },
      cache: "no-store",
    });
    const data = await parseBackendResponse(response);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to load clip pack right now." }, { status: 502 });
  }
}
