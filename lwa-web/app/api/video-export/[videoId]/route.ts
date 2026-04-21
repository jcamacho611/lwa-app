import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, parseBackendResponse } from "../../_lib/backend";

export async function POST(
  request: NextRequest,
  { params }: { params: { videoId: string } }
) {
  try {
    const videoId = params.videoId;
    
    const authorization = request.headers.get("authorization");
    const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;

    // Call backend to get video export bundle
    const response = await fetch(backendUrl(`/v1/video-analysis/export/${videoId}`), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(token),
      },
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to export video bundle" },
        { status: 500 }
      );
    }

    const data = await parseBackendResponse(response);
    
    return NextResponse.json(data, {
      status: 200,
      headers: {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  } catch (error) {
    console.error("Video export error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
