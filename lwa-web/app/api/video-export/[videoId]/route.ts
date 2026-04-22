import { NextRequest, NextResponse } from "next/server";
import {
  authorizationHeader,
  backendUrl,
  bearerTokenFromRequest,
  guestHeaders,
  guestIdFromRequest,
  parseBackendResponse,
} from "../../_lib/backend";

// NOTE:
// The active first-use ClipStudio export flow currently uses /api/export-bundle
// with req_* generate-pack identifiers.
// This route proxies backend video-analysis export by request/video identifier
// and is kept aligned for compatibility, but it is not the canonical first-use
// export path unless the active generate-flow identifier contract is updated.
export async function POST(
  request: NextRequest,
  { params }: { params: { videoId: string } }
) {
  try {
    const videoId = params.videoId;
    const token = bearerTokenFromRequest(request);
    const guestId = guestIdFromRequest(request);

    const response = await fetch(backendUrl(`/v1/video-analysis/export/${videoId}`), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(token),
        ...guestHeaders(guestId),
      },
      cache: "no-store",
    });

    const data = await parseBackendResponse(response);

    if (!response.ok) {
      return NextResponse.json(
        { error: data?.detail || data?.error || "Failed to export video bundle" },
        { status: response.status },
      );
    }

    return NextResponse.json(data, {
      status: 200,
      headers: {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  } catch {
    return NextResponse.json(
      { error: "Unable to reach the clipping backend right now." },
      { status: 502 },
    );
  }
}
