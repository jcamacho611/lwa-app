import { NextResponse } from "next/server";
import { backendUrl, parseBackendResponse } from "../_lib/backend";

export async function GET() {
  const response = await fetch(backendUrl("/v1/trends"), {
    cache: "no-store",
    headers: { Accept: "application/json" },
  });

  const data = await parseBackendResponse(response);

  if (!response.ok) {
    return NextResponse.json(data, { status: response.status });
  }

  return NextResponse.json(data, {
    headers: { "Cache-Control": "public, s-maxage=60, stale-while-revalidate=300" },
  });
}
