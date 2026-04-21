import { NextRequest, NextResponse } from "next/server";

export async function POST(
  request: NextRequest,
  { params }: { params: { videoId: string } }
) {
  try {
    const videoId = params.videoId;
    
    // Call backend to get video export bundle
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/video-analysis/export/${videoId}`, {
      method: "POST",
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
        { error: "Failed to export video bundle" },
        { status: 500 }
      );
    }

    const data = await response.json();
    
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
