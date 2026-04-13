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

export async function parseBackendResponse(response: Response) {
  const text = await response.text();
  return text ? JSON.parse(text) : null;
}
