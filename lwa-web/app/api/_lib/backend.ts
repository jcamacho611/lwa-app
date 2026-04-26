const BACKEND_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.LWA_BACKEND_URL ||
  "https://lwa-backend-production-c9cc.up.railway.app"
).replace(/\/$/, "");

export function backendUrl(path: string) {
  return `${BACKEND_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

export function authorizationHeader(token: string | null | undefined): Record<string, string> {
  if (!token) {
    return {};
  }
  return {
    Authorization: `Bearer ${token}`,
  };
}

export function bearerTokenFromRequest(request: Request): string | null {
  const authorization = request.headers.get("authorization");
  if (!authorization?.toLowerCase().startsWith("bearer ")) {
    return null;
  }
  return authorization.split(" ", 2)[1] || null;
}

export const GUEST_ID_COOKIE = "lwa_guest_id";

export function guestIdFromRequest(request: Request): string {
  const cookieHeader = request.headers.get("cookie") || "";
  const existing = cookieHeader
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${GUEST_ID_COOKIE}=`))
    ?.split("=")[1];

  return existing ? decodeURIComponent(existing) : crypto.randomUUID();
}

export function guestHeaders(guestId: string | null | undefined): Record<string, string> {
  if (!guestId) {
    return {};
  }
  return {
    "x-lwa-client-id": guestId,
  };
}

function normalizeBackendFallbackMessage(response: Response, text: string) {
  const trimmed = text.replace(/\s+/g, " ").trim();
  if (!trimmed) {
    return response.statusText || "Backend returned an empty response.";
  }

  if (/^<!doctype html/i.test(trimmed) || /^<html/i.test(trimmed)) {
    const titleMatch = trimmed.match(/<title>(.*?)<\/title>/i);
    const title = titleMatch?.[1]?.trim();
    return title ? `Backend returned HTML instead of JSON: ${title}` : "Backend returned HTML instead of JSON.";
  }

  return trimmed.slice(0, 4000);
}

export async function parseBackendResponse(response: Response) {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    const message = normalizeBackendFallbackMessage(response, text);
    return {
      detail: message,
      error: message,
    };
  }
}
