import { NextRequest, NextResponse } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: { clipId: string } }
) {
  try {
    const clipId = params.clipId;
    
    // Call backend to get clip render status
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/clip-status/${clipId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        // Add auth header if available
        ...(request.headers.get("authorization") && {
          "Authorization": request.headers.get("authorization")
        })
      },
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to fetch clip render status" },
        { status: 500 }
      );
    }

    const data = await response.json();
    
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
