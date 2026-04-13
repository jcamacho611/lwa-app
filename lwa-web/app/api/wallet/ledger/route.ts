import { NextRequest, NextResponse } from "next/server";
import { authorizationHeader, backendUrl, bearerTokenFromRequest, parseBackendResponse } from "../../_lib/backend";

export async function GET(request: NextRequest) {
  const token = bearerTokenFromRequest(request);

  if (!token) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  try {
    const response = await fetch(backendUrl("/v1/wallet/ledger"), {
      headers: {
        ...authorizationHeader(token),
      },
      cache: "no-store",
    });
    const data = await parseBackendResponse(response);
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ detail: "Unable to load the wallet ledger right now." }, { status: 502 });
  }
}
