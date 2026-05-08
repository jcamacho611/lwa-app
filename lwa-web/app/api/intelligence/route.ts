import { NextRequest, NextResponse } from "next/server";
import { backendUrl, parseBackendResponse } from "../_lib/backend";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const endpoint = searchParams.get("endpoint") || "";

  const allowed = ["viral-signals", "hook-formulas", "caption-styles", "platform-profiles", "thumbnail-rules", "campaign-readiness"];
  if (!allowed.includes(endpoint)) {
    return NextResponse.json({ error: "Unknown intelligence endpoint." }, { status: 400 });
  }

  const backendResponse = await fetch(backendUrl(`/v1/intelligence/${endpoint}`), {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });

  const data = await parseBackendResponse(backendResponse);

  if (!backendResponse.ok) {
    return NextResponse.json(data, { status: backendResponse.status });
  }

  return NextResponse.json(data, {
    headers: { "Cache-Control": "public, s-maxage=300, stale-while-revalidate=3600" },
  });
}
