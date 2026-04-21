import { NextRequest, NextResponse } from "next/server";
import { GUEST_ID_COOKIE, authorizationHeader, backendUrl, guestHeaders, guestIdFromRequest, parseBackendResponse } from "../_lib/backend";

type GenerateRequestBody = {
  mode?: "video" | "image" | "idea";
  url?: string;
  platform?: string;
  uploadFileId?: string;
  contentAngle?: string;
  ideaPrompt?: string;
};

export async function POST(request: NextRequest) {
  let payload: GenerateRequestBody;

  try {
    payload = (await request.json()) as GenerateRequestBody;
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const url = payload.url?.trim();
  const platform = payload.platform?.trim();
  const uploadFileId = payload.uploadFileId?.trim();
  const contentAngle = payload.contentAngle?.trim();
  const mode = payload.mode || "video";
  const ideaPrompt = payload.ideaPrompt?.trim();
  const authorization = request.headers.get("authorization");
  const token = authorization?.toLowerCase().startsWith("bearer ") ? authorization.split(" ", 2)[1] : null;
  const guestId = token ? null : guestIdFromRequest(request);

  if (mode === "video" && !url && !uploadFileId) {
    return NextResponse.json({ error: "Paste a public source URL or upload a file to continue." }, { status: 400 });
  }
  if (mode === "image" && !uploadFileId) {
    return NextResponse.json({ error: "Upload an image before running Image mode." }, { status: 400 });
  }
  if (mode === "idea" && !ideaPrompt) {
    return NextResponse.json({ error: "Describe the idea you want LWA to generate." }, { status: 400 });
  }

  try {
    const backendPath = mode === "video" ? "/process" : "/v1/generation/multimodal";
    const body =
      mode === "video"
        ? {
            video_url: url || undefined,
            upload_file_id: uploadFileId || undefined,
            target_platform: platform || undefined,
            content_angle: contentAngle || undefined,
          }
        : {
            mode,
            upload_file_id: uploadFileId || undefined,
            prompt: mode === "image" ? ideaPrompt || contentAngle || undefined : undefined,
            text_prompt: mode === "idea" ? ideaPrompt : undefined,
            target_platform: platform || undefined,
          };

    const backendResponse = await fetch(backendUrl(backendPath), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authorizationHeader(token),
        ...guestHeaders(guestId),
      },
      body: JSON.stringify(body),
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

    const response = NextResponse.json(parsed, { status: 200 });
    if (guestId) {
      response.cookies.set(GUEST_ID_COOKIE, guestId, {
        httpOnly: true,
        sameSite: "lax",
        path: "/",
        maxAge: 60 * 60 * 24 * 30,
      });
    }
    return response;
  } catch {
    return NextResponse.json(
      { error: "Unable to reach the clipping backend right now. Try again in a moment." },
      { status: 502 },
    );
  }
}
