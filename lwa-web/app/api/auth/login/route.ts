import { NextRequest, NextResponse } from "next/server";
import { backendUrl, parseBackendResponse } from "../../_lib/backend";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const response = await fetch(backendUrl("/v1/auth/login"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    const data = await parseBackendResponse(response);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to complete login right now." }, { status: 502 });
  }
}
