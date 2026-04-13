import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, parseBackendResponse } from "../../../_lib/backend";

type RouteContext = {
  params: Promise<{
    clipId: string;
  }>;
};

export async function PATCH(request: NextRequest, context: RouteContext) {
  const authorization = request.headers.get("authorization");
  const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;

  if (!token) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  const { clipId } = await context.params;

  try {
    const body = await request.json();
    const response = await fetch(backendUrl(`/v1/me/clips/${clipId}`), {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(token),
      },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    const data = await parseBackendResponse(response);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to update clip right now." }, { status: 502 });
  }
}
