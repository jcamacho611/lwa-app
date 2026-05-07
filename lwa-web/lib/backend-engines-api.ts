export type BackendEngineStatus =
  | "scaffolded"
  | "local_ready"
  | "backend_ready"
  | "provider_ready"
  | "production_ready";

export type BackendEngineCapability = {
  id: string;
  label: string;
  description: string;
  local_only: boolean;
  requires_provider: boolean;
  requires_persistence: boolean;
};

export type BackendEngineHealth = {
  engine_id: string;
  name: string;
  status: BackendEngineStatus;
  healthy: boolean;
  checked_at: string;
  warnings: string[];
  blocked_integrations: string[];
};

export type BackendEngineMetadata = {
  engine_id: string;
  name: string;
  status: BackendEngineStatus;
  capabilities: BackendEngineCapability[];
  next_required_integrations: string[];
  health: BackendEngineHealth;
};

export type BackendEngineRegistryResponse = {
  count: number;
  engines: Record<string, BackendEngineMetadata>;
  status_summary: Record<BackendEngineStatus, number>;
  note?: string;
};

export type BackendEngineDemoResult = {
  engine_id: string;
  name: string;
  status: string;
  summary: string;
  input_echo: Record<string, unknown>;
  output: Record<string, unknown>;
  warnings: string[];
  next_required_integrations: string[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "";

function buildFallbackRegistry(): BackendEngineRegistryResponse {
  const ids = [
    "creator",
    "brain",
    "render",
    "marketplace",
    "wallet_entitlements",
    "proof_history",
    "world_game",
    "safety",
    "social_distribution",
    "operator_admin",
  ];

  const engines = Object.fromEntries(
    ids.map((id) => [
      id,
      {
        engine_id: id,
        name: id.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase()),
        status: "scaffolded" as BackendEngineStatus,
        capabilities: [],
        next_required_integrations: ["backend /engines route", "environment URL", "route validation"],
        health: {
          engine_id: id,
          name: id,
          status: "scaffolded" as BackendEngineStatus,
          healthy: false,
          checked_at: new Date().toISOString(),
          warnings: ["Frontend fallback; backend engine registry not connected."],
          blocked_integrations: ["backend API URL"],
        },
      },
    ]),
  );

  return {
    count: ids.length,
    engines,
    status_summary: {
      scaffolded: ids.length,
      local_ready: 0,
      backend_ready: 0,
      provider_ready: 0,
      production_ready: 0,
    },
    note: "Local fallback shown because backend engine API is not configured or unreachable.",
  };
}

export async function fetchBackendEngines(): Promise<BackendEngineRegistryResponse> {
  if (!API_BASE) {
    return buildFallbackRegistry();
  }

  try {
    const response = await fetch(`${API_BASE}/engines`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Engine registry request failed: ${response.status}`);
    }
    return (await response.json()) as BackendEngineRegistryResponse;
  } catch {
    return buildFallbackRegistry();
  }
}

export async function runBackendEngineDemo(
  engineId: string,
  payload: Record<string, unknown> = {},
): Promise<BackendEngineDemoResult> {
  if (!API_BASE) {
    return {
      engine_id: engineId,
      name: engineId,
      status: "fallback_only",
      summary: "Backend URL is not configured; showing local frontend fallback.",
      input_echo: payload,
      output: { backend_connected: false },
      warnings: ["Set NEXT_PUBLIC_API_BASE_URL to call the backend /engines route."],
      next_required_integrations: ["backend env configuration"],
    };
  }

  const response = await fetch(`${API_BASE}/engines/${engineId}/demo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Engine demo failed: ${response.status}`);
  }

  return (await response.json()) as BackendEngineDemoResult;
}

export function getLocalBackendEngineFallback(): BackendEngineRegistryResponse {
  return buildFallbackRegistry();
}
