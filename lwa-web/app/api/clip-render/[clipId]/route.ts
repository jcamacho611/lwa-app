import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, parseBackendResponse } from "../../_lib/backend";

export async function GET(
  request: NextRequest,
  { params }: { params: { clipId: string } }
) {
  try {
    const clipId = params.clipId;
    const requestId = request.nextUrl.searchParams.get("request_id");
    const query = requestId ? `?request_id=${encodeURIComponent(requestId)}` : "";
    
    const authorization = request.headers.get("authorization");
    const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;

    // Call backend to get clip render status
    const response = await fetch(backendUrl(`/v1/clip-status/${clipId}${query}`), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(token),
      },
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to fetch clip render status" },
        { status: 500 }
      );
    }

    const data = await parseBackendResponse(response);
    
    return NextResponse.json(data, {
      status: 200,
      headers: {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
      },
    });
  } catch (error) {
    console.error("Clip render status error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
