import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, parseBackendResponse } from "../_lib/backend";

type GenerateRequestBody = {
  url?: string;
  platform?: string;
  uploadFileId?: string;
  contentAngle?: string;
};

export async function POST(request: NextRequest) {
  let payload: GenerateRequestBody;

  try {
    payload = (await request.json()) as GenerateRequestBody;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const url = payload.url?.trim();
  const platform = payload.platform?.trim() || "TikTok";
  const uploadFileId = payload.uploadFileId?.trim();
  const contentAngle = payload.contentAngle?.trim();
  const authorization = request.headers.get("authorization");
  const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;

  if (!url && !uploadFileId) {
    return NextResponse.json({ error: "Paste a video URL or upload a file to continue." }, { status: 400 });
  }

  try {
    const backendResponse = await fetch(backendUrl("/process"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(token),
      },
      body: JSON.stringify({
        video_url: url || undefined,
        upload_file_id: uploadFileId || undefined,
        target_platform: platform,
        content_angle: contentAngle || undefined,
      }),
      cache: "no-store",
    });

    const parsed = await parseBackendResponse(backendResponse);

    if (!backendResponse.ok) {
      const detail =
        parsed?.detail ||
        parsed?.error ||
        "The backend could not generate clips for that source right now.";

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
