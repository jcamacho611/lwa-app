export type LwaEngineServiceId =
  | "operator_admin"
  | "safety"
  | "proof_history"
  | "world_game"
  | "brain"
  | "render"
  | "creator"
  | "wallet_entitlements"
  | "marketplace"
  | "social_distribution";

export type LwaEngineServicePromotionStatus =
  | "deploy_now"
  | "deploy_after_smoke"
  | "hold_until_gated";

export type LwaEngineServiceDomainConfig = {
  engineId: LwaEngineServiceId;
  serviceName: string;
  envVar: string;
  promotionStatus: LwaEngineServicePromotionStatus;
  publicByDefault: boolean;
  description: string;
};

export type LwaEngineServiceStatus = {
  engineId: LwaEngineServiceId;
  serviceName: string;
  envVar: string;
  configured: boolean;
  url: string | null;
  fallback: "dedicated_railway_service" | "main_backend_engines_route";
  promotionStatus: LwaEngineServicePromotionStatus;
  publicByDefault: boolean;
};

export const LWA_ENGINE_SERVICE_DOMAIN_CONFIGS: LwaEngineServiceDomainConfig[] = [
  {
    engineId: "operator_admin",
    serviceName: "lwa-engine-operator-admin",
    envVar: "NEXT_PUBLIC_LWA_ENGINE_OPERATOR_ADMIN_URL",
    promotionStatus: "deploy_now",
    publicByDefault: true,
    description: "Read-only readiness, deployment, and operator snapshot engine.",
  },
  {
    engineId: "safety",
    serviceName: "lwa-engine-safety",
    envVar: "NEXT_PUBLIC_LWA_ENGINE_SAFETY_URL",
    promotionStatus: "deploy_now",
    publicByDefault: true,
    description: "Guardrails and local-safe risk checks before external actions exist.",
  },
  {
    engineId: "proof_history",
    serviceName: "lwa-engine-proof-history",
    envVar: "NEXT_PUBLIC_LWA_ENGINE_PROOF_HISTORY_URL",
    promotionStatus: "deploy_now",
    publicByDefault: true,
    description: "Proof previews, history foundation, and trust trail scaffolding.",
  },
  {
    engineId: "world_game",
    serviceName: "lwa-engine-world-game",
    envVar: "NEXT_PUBLIC_LWA_ENGINE_WORLD_GAME_URL",
    promotionStatus: "deploy_now",
    publicByDefault: true,
    description: "Lee-Wuh world, missions, XP, relic previews, and game-state foundation.",
  },
  {
    engineId: "brain",
    serviceName: "lwa-engine-brain",
    envVar: "NEXT_PUBLIC_LWA_ENGINE_BRAIN_URL",
    promotionStatus: "deploy_after_smoke",
    publicByDefault: true,
    description: "Intelligence routing and recommendations; providers must remain disabled until gated.",
  },
  {
    engineId: "render",
    serviceName: "lwa-engine-render",
    envVar: "NEXT_PUBLIC_LWA_ENGINE_RENDER_URL",
    promotionStatus: "deploy_after_smoke",
    publicByDefault: true,
    description: "Render planning and asset handoff; paid render providers and queues stay disabled.",
  },
  {
    engineId: "creator",
    serviceName: "lwa-engine-creator",
    envVar: "NEXT_PUBLIC_LWA_ENGINE_CREATOR_URL",
    promotionStatus: "deploy_after_smoke",
    publicByDefault: true,
    description: "Creator hook, caption, clip-package, and creator-workflow planning engine.",
  },
  {
    engineId: "wallet_entitlements",
    serviceName: "lwa-engine-wallet-entitlements",
    envVar: "NEXT_PUBLIC_LWA_ENGINE_WALLET_ENTITLEMENTS_URL",
    promotionStatus: "hold_until_gated",
    publicByDefault: false,
    description: "Credits and entitlement checks only; no real payment, payout, or wallet actions.",
  },
  {
    engineId: "marketplace",
    serviceName: "lwa-engine-marketplace",
    envVar: "NEXT_PUBLIC_LWA_ENGINE_MARKETPLACE_URL",
    promotionStatus: "hold_until_gated",
    publicByDefault: false,
    description: "Marketplace and campaign teaser engine; hold until verification/legal gates exist.",
  },
  {
    engineId: "social_distribution",
    serviceName: "lwa-engine-social-distribution",
    envVar: "NEXT_PUBLIC_LWA_ENGINE_SOCIAL_DISTRIBUTION_URL",
    promotionStatus: "hold_until_gated",
    publicByDefault: false,
    description: "Social packaging/scheduling preview only; no external posting by default.",
  },
];

export const LWA_MAIN_BACKEND_ENV_VARS = [
  "NEXT_PUBLIC_API_BASE_URL",
  "NEXT_PUBLIC_BACKEND_URL",
] as const;

export const LWA_ENGINE_SERVICE_START_COMMAND =
  "cd lwa-backend && uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT";

export const LWA_ENGINE_SERVICE_HEALTH_PATH = "/health";

export const LWA_ENGINE_SERVICE_ROUTE_PATHS = [
  "/health",
  "/engine",
  "/engine/health",
  "/engine/demo",
] as const;

function normalizeUrl(url: string | undefined): string | null {
  if (!url) return null;
  const trimmed = url.trim();
  if (!trimmed) return null;
  return trimmed.replace(/\/+$/, "");
}

function envValue(envVar: string): string | null {
  const value = process.env[envVar];
  return normalizeUrl(value);
}

export function getEngineDomainConfig(
  engineId: LwaEngineServiceId,
): LwaEngineServiceDomainConfig | undefined {
  return LWA_ENGINE_SERVICE_DOMAIN_CONFIGS.find((config) => config.engineId === engineId);
}

export function getEngineServiceUrl(engineId: LwaEngineServiceId): string | null {
  const config = getEngineDomainConfig(engineId);
  if (!config) return null;
  return envValue(config.envVar);
}

export function getMainBackendUrl(): string | null {
  for (const envVar of LWA_MAIN_BACKEND_ENV_VARS) {
    const value = envValue(envVar);
    if (value) return value;
  }
  return null;
}

export function getEngineServiceStatus(engineId: LwaEngineServiceId): LwaEngineServiceStatus {
  const config = getEngineDomainConfig(engineId);

  if (!config) {
    return {
      engineId,
      serviceName: `lwa-engine-${engineId.replace(/_/g, "-")}`,
      envVar: "UNKNOWN_ENGINE_ENV_VAR",
      configured: false,
      url: null,
      fallback: "main_backend_engines_route",
      promotionStatus: "hold_until_gated",
      publicByDefault: false,
    };
  }

  const url = getEngineServiceUrl(engineId);

  return {
    engineId: config.engineId,
    serviceName: config.serviceName,
    envVar: config.envVar,
    configured: Boolean(url),
    url,
    fallback: url ? "dedicated_railway_service" : "main_backend_engines_route",
    promotionStatus: config.promotionStatus,
    publicByDefault: config.publicByDefault,
  };
}

export function getAllEngineServiceStatuses(): LwaEngineServiceStatus[] {
  return LWA_ENGINE_SERVICE_DOMAIN_CONFIGS.map((config) => getEngineServiceStatus(config.engineId));
}

export function getEngineApiBaseUrl(engineId: LwaEngineServiceId): string | null {
  return getEngineServiceUrl(engineId) ?? getMainBackendUrl();
}

export function getEngineDemoEndpoint(engineId: LwaEngineServiceId): string | null {
  const dedicatedServiceUrl = getEngineServiceUrl(engineId);
  if (dedicatedServiceUrl) return `${dedicatedServiceUrl}/engine/demo`;

  const mainBackendUrl = getMainBackendUrl();
  if (!mainBackendUrl) return null;
  return `${mainBackendUrl}/engines/${engineId}/demo`;
}

export function getEngineHealthEndpoint(engineId: LwaEngineServiceId): string | null {
  const dedicatedServiceUrl = getEngineServiceUrl(engineId);
  if (dedicatedServiceUrl) return `${dedicatedServiceUrl}/engine/health`;

  const mainBackendUrl = getMainBackendUrl();
  if (!mainBackendUrl) return null;
  return `${mainBackendUrl}/engines/${engineId}`;
}

export function getDeployNowEngineServices(): LwaEngineServiceDomainConfig[] {
  return LWA_ENGINE_SERVICE_DOMAIN_CONFIGS.filter(
    (config) => config.promotionStatus === "deploy_now",
  );
}

export function getHeldEngineServices(): LwaEngineServiceDomainConfig[] {
  return LWA_ENGINE_SERVICE_DOMAIN_CONFIGS.filter(
    (config) => config.promotionStatus === "hold_until_gated",
  );
}
