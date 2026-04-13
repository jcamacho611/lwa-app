import type { ClipBatchResponse, GenerateRequest } from './types';

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') ??
  'https://lwa-production-c9cc.up.railway.app';

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * POST /generate — synchronous clip generation.
 * Returns a ClipBatchResponse on success, throws ApiError on failure.
 */
export async function generateClips(
  payload: GenerateRequest,
  signal?: AbortSignal,
): Promise<ClipBatchResponse> {
  const url = `${API_BASE}/generate`;

  let response: Response;
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw err;
    }
    throw new ApiError(
      0,
      'Could not reach the backend. Check your connection and try again.',
    );
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}.`;
    try {
      const body = await response.json();
      if (typeof body?.detail === 'string') detail = body.detail;
      else if (typeof body?.message === 'string') detail = body.message;
    } catch {
      // ignore JSON parse errors
    }
    throw new ApiError(response.status, detail);
  }

  return response.json() as Promise<ClipBatchResponse>;
}

/**
 * GET /health — lightweight liveness check.
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { method: 'GET' });
    return res.ok;
  } catch {
    return false;
  }
}
