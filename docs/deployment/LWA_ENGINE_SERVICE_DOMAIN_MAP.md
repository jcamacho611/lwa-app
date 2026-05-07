# LWA Engine Service Domain Map

## Purpose

This document maps the optional dedicated Railway engine service URLs for LWA.

The important distinction:

```text
Backend engine module = Python code inside lwa-backend/app/engines
Railway engine service = separately deployed Railway box running one selected engine
Frontend domain map = optional public URL configuration for those boxes
```

The frontend must keep working even when no dedicated engine services are deployed. If a dedicated service URL is missing, the app should fall back to the main backend `/engines/{engine_id}` route when the main backend URL is configured.

## Required backend service architecture

Each dedicated Railway engine service uses the same start command:

```bash
cd lwa-backend && uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT
```

Each service selects its engine with:

```text
LWA_ENGINE_SERVICE_ID=<engine_id>
```

Health check path:

```text
/health
```

Dedicated service routes:

```text
GET  /health
GET  /engine
GET  /engine/health
POST /engine/demo
```

Main backend fallback routes:

```text
GET  /engines
GET  /engines/health
GET  /engines/{engine_id}
POST /engines/{engine_id}/demo
```

## Frontend domain env vars

These are public frontend URL env vars. They must contain only public Railway service URLs. Never put secrets, provider keys, tokens, or credentials in `NEXT_PUBLIC_*` variables.

| Engine | Railway service | Frontend URL env var | Promotion |
|---|---|---|---|
| `operator_admin` | `lwa-engine-operator-admin` | `NEXT_PUBLIC_LWA_ENGINE_OPERATOR_ADMIN_URL` | Deploy now |
| `safety` | `lwa-engine-safety` | `NEXT_PUBLIC_LWA_ENGINE_SAFETY_URL` | Deploy now |
| `proof_history` | `lwa-engine-proof-history` | `NEXT_PUBLIC_LWA_ENGINE_PROOF_HISTORY_URL` | Deploy now |
| `world_game` | `lwa-engine-world-game` | `NEXT_PUBLIC_LWA_ENGINE_WORLD_GAME_URL` | Deploy now |
| `brain` | `lwa-engine-brain` | `NEXT_PUBLIC_LWA_ENGINE_BRAIN_URL` | Deploy after smoke |
| `render` | `lwa-engine-render` | `NEXT_PUBLIC_LWA_ENGINE_RENDER_URL` | Deploy after smoke |
| `creator` | `lwa-engine-creator` | `NEXT_PUBLIC_LWA_ENGINE_CREATOR_URL` | Deploy after smoke |
| `wallet_entitlements` | `lwa-engine-wallet-entitlements` | `NEXT_PUBLIC_LWA_ENGINE_WALLET_ENTITLEMENTS_URL` | Hold until gated |
| `marketplace` | `lwa-engine-marketplace` | `NEXT_PUBLIC_LWA_ENGINE_MARKETPLACE_URL` | Hold until gated |
| `social_distribution` | `lwa-engine-social-distribution` | `NEXT_PUBLIC_LWA_ENGINE_SOCIAL_DISTRIBUTION_URL` | Hold until gated |

## Main backend fallback env vars

The frontend helper checks these for main backend fallback:

```text
NEXT_PUBLIC_API_BASE_URL
NEXT_PUBLIC_BACKEND_URL
```

If a dedicated engine URL is missing but the main backend URL exists, engine demo requests can fall back to:

```text
<NEXT_PUBLIC_API_BASE_URL>/engines/{engine_id}/demo
```

## Deploy now

Deploy these first because they are read-only or local-safe by design:

1. `lwa-engine-operator-admin`
2. `lwa-engine-safety`
3. `lwa-engine-proof-history`
4. `lwa-engine-world-game`

Then, after smoke tests:

5. `lwa-engine-brain` with providers disabled
6. `lwa-engine-render` with paid render disabled
7. `lwa-engine-creator`

## Hold until gated

Do not publicly wire these until legal/payment/API/safety gates exist:

```text
wallet_entitlements
marketplace
social_distribution
```

Reasons:

- wallet/entitlements can imply credits, payments, or payouts
- marketplace can imply real campaign/brand claims
- social distribution can imply external platform posting

Those services can exist as local-safe code, but should not become user-facing action services until the boundaries are real.

## Railway setup template

For each service:

```text
Service name:
lwa-engine-<engine-name>

Source:
GitHub repo jcamacho611/lwa-app

Branch:
main

Start command:
cd lwa-backend && uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT

Health check path:
/health

Environment:
LWA_ENGINE_SERVICE_ID=<engine_id>
```

After deploy, copy the Railway public domain into the matching frontend env var on the frontend service only if you want the web app to call that dedicated service directly.

## Smoke commands

Replace `SERVICE_DOMAIN` with the Railway public domain.

```bash
curl -fsS https://SERVICE_DOMAIN/health
curl -fsS https://SERVICE_DOMAIN/engine
curl -fsS https://SERVICE_DOMAIN/engine/health
curl -fsS -X POST https://SERVICE_DOMAIN/engine/demo \
  -H 'content-type: application/json' \
  -d '{}'
```

## Current Railway reality

It is normal if Railway currently shows only:

```text
lwa-web / frontend
lwa-backend / main API
function-bun / unknown legacy function
```

The 10 engine services are not created automatically. This repo now has the domain map and service-ready pattern, but the Railway boxes still must be created manually in Railway.

## `function-bun` handling

Do not delete `function-bun` blindly. First check:

1. Which repo/branch it uses.
2. What start command it runs.
3. Whether any frontend/backend env var references its URL.
4. Whether it has recent deployment traffic/logs.

If it is unused, rename it to `legacy-function-bun-unused`, pause it, then delete later after the new engine services are verified.
