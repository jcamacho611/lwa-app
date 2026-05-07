# LWA Actual Backend Engine Foundation

## What this is

This package adds real backend-owned engine modules under `lwa-backend/app/engines/`.

These are Python modules, testable in the backend, and routable through FastAPI. They are not frontend-only TypeScript facades.

## Engine modules added

- `creator`
- `brain`
- `render`
- `marketplace`
- `wallet_entitlements`
- `proof_history`
- `world_game`
- `safety`
- `social_distribution`
- `operator_admin`

## Routes added

- `GET /engines`
- `GET /engines/health`
- `GET /engines/{engine_id}`
- `POST /engines/{engine_id}/demo`

## Status truth

- `scaffolded`
- `local_ready`
- `backend_ready`
- `provider_ready`
- `production_ready`

The foundation intentionally avoids claiming `production_ready` by default.

## Local/demo only

- `marketplace` remains teaser-only.
- `social_distribution` remains non-posting and scaffolded.
- `operator_admin` is read-only demo truth.
- `creator`, `brain`, `world_game`, and `safety` are deterministic backend previews.

## Missing integrations

- persistent engine telemetry
- worker/service splitting
- provider spend policy
- entitlement-backed gating
- proof persistence
- production social posting
- live marketplace contracts

## Why this matters

Railway only shows deployable services, not the engine modules inside a service.

This package gives the backend a real engine registry now, so the next step can split the heavy engines into separate Railway services only when contracts and tests are stable.
