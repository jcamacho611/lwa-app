import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, bearerTokenFromRequest, parseBackendResponse } from "../../../_lib/backend";

type RouteContext = {
  params: Promise<{ postId: string }>;
};

export async function PATCH(request: NextRequest, context: RouteContext) {
  const token = bearerTokenFromRequest(request);

  if (!token) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  try {
    const { postId } = await context.params;
    const payload = await request.json();
    const response = await fetch(backendUrl(`/v1/posting/scheduled/${postId}`), {
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
    return NextResponse.json({ detail: "Unable to update the scheduled post right now." }, { status: 502 });
  }
}
