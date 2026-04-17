import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, bearerTokenFromRequest, parseBackendResponse } from "../../_lib/backend";

type RouteContext = {
  params: Promise<{
    jobId: string;
  }>;
};

export async function GET(request: NextRequest, context: RouteContext) {
  const { jobId } = await context.params;
  const token = bearerTokenFromRequest(request);

  if (!jobId) {
    return NextResponse.json({ error: "Job id is required." }, { status: 400 });
  }

  try {
    const backendResponse = await fetch(backendUrl(`/v1/jobs/${jobId}`), {
      headers: {
        ...authorizationHeader(token),
      },
      cache: "no-store",
    });
    const parsed = await parseBackendResponse(backendResponse);

    if (!backendResponse.ok) {
      const detail = parsed?.detail || parsed?.error || "Unable to load generation status right now.";
      return NextResponse.json({ error: detail }, { status: backendResponse.status });
    }

    return NextResponse.json(parsed, { status: 200 });
  } catch {
    return NextResponse.json(
      { error: "Unable to reach the clipping backend right now. Try again in a moment." },
      { status: 502 },
    );
  }
}
