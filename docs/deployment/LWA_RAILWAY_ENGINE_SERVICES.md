# LWA Railway Engine Services

**Branch:** `claude/railway-engine-services`
**Status:** Foundation slice — additive, no `/generate` change, no payment surfaces.

This document explains how to turn the 10 backend engines under
`lwa-backend/app/engines/` into separate Railway services *intentionally*
— not all at once. One generic FastAPI service codebase serves any single
engine; deployment is controlled per-Railway-service by an environment
variable.

---

## 1. Why one generic service, not ten apps

There is one engine service codebase: `lwa-backend/app/services/engine_service_app.py`.
At boot it reads `LWA_ENGINE_SERVICE_ID` and serves exactly that engine.
This means:

- Zero duplicated code across ten Railway services.
- One image, ten deployments.
- Adding a new engine to the registry automatically makes it deployable
  without writing a new service.
- Deploys can be staged: turn on operator_admin first, observe, then
  bring up the next engine when ready.

The full engine registry remains accessible inside the main backend at
`/engines` (see `lwa-backend/app/api/routes/engines.py`). The Railway
services are *isolated views* of that same registry.

## 2. Routes exposed by every engine service

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Banner + currently selected engine id |
| `GET` | `/health` | Liveness; never raises (reports config errors as fields) |
| `GET` | `/engine` | Full record for the selected engine (id, name, status, capabilities, health) |
| `GET` | `/engine/health` | Health snapshot for the selected engine |
| `POST` | `/engine/demo` | Run the selected engine's deterministic demo with a JSON payload |

All routes are unauthenticated by default — the engine service makes no
provider calls, no payouts, no external posting, and mutates no real
money. The deployer is expected to add standard auth/rate-limit
middleware in front of these services if exposed publicly.

## 3. Required environment variable

```
LWA_ENGINE_SERVICE_ID=<engine_id>
```

If unset or empty, the service falls back to `operator_admin` (the
safest read-only roll-up engine).
If set to an unknown id, `/health` returns 200 with a `selection_error`
field; `/engine`, `/engine/health`, and `/engine/demo` return `503` with
the same message.

## 4. Railway start command

Same start command for every engine service. The engine identity comes
from the env var, not the command.

```bash
cd lwa-backend && uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT
```

Health check path: `/health`.

## 5. Deploy order (staged)

Do **not** bring up all 10 services at once. Recommended order:

| # | Engine | Service name | Risk | Why first/why later |
|---|---|---|---|---|
| 1 | `operator_admin` | `lwa-engine-operator-admin` | Low | Read-only system snapshot. Safest first deploy. |
| 2 | `safety` | `lwa-engine-safety` | Low | Local lexicon + payout/post guards. No external call. |
| 3 | `proof_history` | `lwa-engine-proof-history` | Low | Demo proof records; provider not required. |
| 4 | `world_game` | `lwa-engine-world-game` | Low | Mission/XP/realm preview. No money. |
| 5 | `brain` | `lwa-engine-brain` | Medium | Provider-routable; ship with provider toggled OFF. |
| 6 | `render` | `lwa-engine-render` | Medium | Strategy-only fallback active; full render path requires queue + cost guard. |
| 7 | `creator` | `lwa-engine-creator` | Medium | Mission seed + signal preview. Backend persistence pending. |
| 8 | `wallet_entitlements` | `lwa-engine-wallet-entitlements` | High | Read-only credits/entitlements. Payouts permanently off in this engine. |
| 9 | `marketplace` | `lwa-engine-marketplace` | High | Teaser only. Full marketplace blocked behind legal review. |
| 10 | `social_distribution` | `lwa-engine-social-distribution` | High | Recommendations only. External posting must remain off until a separate posting worker exists. |

Engines 8–10 stay on the registry but should not be promoted to
production_ready until legal/payment/API gates exist.

## 6. Why Railway currently shows web/backend/(function) only

Today the LWA Railway project shows:

- the **frontend web** service (Next.js, `lwa-web`),
- the **main backend** service (`lwa-backend`, the existing API),
- optionally a **function** service.

There are no per-engine services yet because no per-engine entrypoint
existed. With this slice merged, the founder can create new Railway
services in the same project that all point at this repo with different
`LWA_ENGINE_SERVICE_ID` values. The main backend service does not change.

## 7. Founder UI steps to add the first engine service (operator_admin)

1. Open the LWA Railway project.
2. Click **+ New** → **GitHub Repo** → select `jcamacho611/lwa-app`.
3. Choose branch `claude/railway-engine-services` (after merge: `main`).
4. In the new service **Settings**:
   - **Service name:** `lwa-engine-operator-admin`
   - **Root directory:** *(repo root, default)*
   - **Start command:** `cd lwa-backend && uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT`
   - **Healthcheck path:** `/health`
5. In **Variables** add:
   - `LWA_ENGINE_SERVICE_ID = operator_admin`
6. Deploy.
7. Open the deployed URL and call `/health` and `/engine`. Both must
   return 200. `/engine` should report `engine_id: "operator_admin"`.

Repeat steps 2–7 with a different `LWA_ENGINE_SERVICE_ID` for each
engine you choose to deploy. Stick to the order in Section 5.

## 8. What is intentionally not enabled in this lane

- No paid provider calls (OpenAI, Anthropic, Seedance, etc.).
- No payouts, withdrawals, or wallet mutations.
- No social posting or scheduling — recommendations only.
- No `/generate` behavior change. The unified `/engines` route in the
  main backend and the per-engine Railway services are additive.

## 9. Files added by this slice

```
lwa-backend/app/services/engine_runtime.py
lwa-backend/app/services/engine_service_app.py
lwa-backend/tests/test_engine_service_runtime.py
lwa-backend/tests/test_engine_service_app.py
docs/deployment/LWA_RAILWAY_ENGINE_SERVICES.md           (this file)
docs/deployment/railway-engine-service-template.md
docs/deployment/railway-templates/*.json                 (10 service templates)
```

The engine modules under `lwa-backend/app/engines/` and the unified
`/engines` route already shipped in commit `feat(backend): add actual
LWA engine foundation`. This slice only adds the deployable service
layer on top of that foundation.

## 10. Next safe slices

1. **Add provider toggle for `brain`** — an env var (e.g.
   `LWA_BRAIN_PROVIDER=openai|disabled`) that, when set on the
   `lwa-engine-brain` Railway service only, opts that single deployment
   into provider routing without affecting the main backend.
2. **Cost guard + per-request budget cap** for `brain` and `render`
   before either advances past `local_ready`.
3. **Persist proof_history and wallet_entitlements** behind a real
   datastore so they can move from `backend_ready` to `production_ready`.
4. **Posting worker** as a *separate* engine (`social_distribution`
   stays advisory; the posting worker is a new engine with its own
   safety contract and its own Railway service).
5. **Admin auth** in front of `/engines` and the operator_admin Railway
   service before either is exposed publicly.
