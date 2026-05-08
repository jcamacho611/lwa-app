import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, guestHeaders, guestIdFromRequest, parseBackendResponse } from "../../_lib/backend";

export async function GET(
  request: NextRequest,
  { params }: { params: { jobId: string } },
) {
  const { jobId } = params;
  const authorization = request.headers.get("authorization");
  const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;
  const guestId = token ? null : guestIdFromRequest(request);

  try {
    const backendResponse = await fetch(backendUrl(`/v1/jobs/${encodeURIComponent(jobId)}`), {
      headers: {
        ...authorizationHeader(token),
        ...guestHeaders(guestId),
      },
      cache: "no-store",
    });

    const parsed = await parseBackendResponse(backendResponse);

    if (!backendResponse.ok) {
      return NextResponse.json(parsed, { status: backendResponse.status });
    }

    return NextResponse.json(parsed);
  } catch {
    return NextResponse.json({ error: "Unable to reach the clipping backend." }, { status: 502 });
  }
}
