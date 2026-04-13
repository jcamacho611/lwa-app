import { NextRequest, NextResponse } from "next/server";

const backendProcessUrl =
  process.env.BACKEND_PROCESS_URL ??
  "https://lwa-backend-production-c9cc.up.railway.app/process";

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as {
      url?: string;
      platform?: string;
    };

    const url = body.url?.trim();
    const platform = body.platform?.trim();

    if (!url) {
      return NextResponse.json(
        { message: "Paste a video URL before generating clips." },
        { status: 400 }
      );
    }

    if (!platform) {
      return NextResponse.json(
        { message: "Choose a target platform first." },
        { status: 400 }
      );
    }

    const upstream = await fetch(backendProcessUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url,
        platform,
        video_url: url,
        target_platform: platform,
      }),
      cache: "no-store",
    });

    const text = await upstream.text();

    if (!upstream.ok) {
      let message = "The clip generation request failed.";
      try {
        const parsed = JSON.parse(text) as { detail?: string; message?: string };
        message = parsed.detail ?? parsed.message ?? message;
      } catch {
        if (text.trim()) {
          message = text;
        }
      }

      return NextResponse.json({ message }, { status: upstream.status });
    }

    return new NextResponse(text, {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        message:
          error instanceof Error
            ? error.message
            : "Something went wrong while contacting the backend.",
      },
      { status: 500 }
    );
  }
}
