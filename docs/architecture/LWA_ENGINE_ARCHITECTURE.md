# LWA Engine Architecture

A single page that explains how LWA's backend engines, the unified
`/engines` API, the per-engine Railway services, the `/engines` engine
room UI, and the public `/demo` proof links fit together. Read this
before adding a new engine or wiring a new surface.

---

## 1. The three layers

```
                  ┌────────────────────────────────────────────┐
                  │  USER-FACING ROUTES (lwa-web, Next.js)     │
                  │                                            │
                  │   /demo               public demo journey  │
                  │   /engines            engine room          │
                  │   /engines/[id]       deep-link per engine │
                  └────────────────────────────────────────────┘
                                    │ Next.js <Link>
                                    │ + read-only fetch
                                    ▼
                  ┌────────────────────────────────────────────┐
                  │  UNIFIED API (lwa-backend, FastAPI)        │
                  │                                            │
                  │   GET   /engines                           │
                  │   GET   /engines/health                    │
                  │   GET   /engines/{engine_id}               │
                  │   POST  /engines/{engine_id}/demo          │
                  │   (registered in app/main.py)              │
                  └────────────────────────────────────────────┘
                                    │ imports
                                    ▼
                  ┌────────────────────────────────────────────┐
                  │  BACKEND ENGINES (lwa-backend/app/engines) │
                  │                                            │
                  │   creator           operator_admin         │
                  │   brain             safety                 │
                  │   render            wallet_entitlements    │
                  │   marketplace       proof_history          │
                  │   world_game        social_distribution    │
                  │                                            │
                  │   each module: BackendEngine + _demo()     │
                  └────────────────────────────────────────────┘
                                    │ same registry
                                    ▼
                  ┌────────────────────────────────────────────┐
                  │  PER-ENGINE RAILWAY SERVICES (optional)    │
                  │                                            │
                  │   lwa-engine-operator-admin                │
                  │   lwa-engine-safety                        │
                  │   lwa-engine-proof-history                 │
                  │   lwa-engine-world-game                    │
                  │   lwa-engine-brain                         │
                  │   lwa-engine-render                        │
                  │   lwa-engine-creator                       │
                  │   lwa-engine-wallet-entitlements           │
                  │   lwa-engine-marketplace                   │
                  │   lwa-engine-social-distribution           │
                  │                                            │
                  │   one codebase: app.services.engine_service_app │
                  │   selected by env: LWA_ENGINE_SERVICE_ID   │
                  └────────────────────────────────────────────┘
```

There is **one** engine module per concern. The unified API, the engine
room UI, and the per-engine Railway services all read from the same
registry. New engines are declared once and become available everywhere.

## 2. The readiness ladder

Every engine reports a `status` from this five-step ladder. The status
is honest — promotion to a higher rung requires the integrations listed
in `next_required_integrations_list` to actually exist.

| Status | What it means | Examples |
|---|---|---|
| `scaffolded` | Module exists, no real logic. Demo path returns placeholder data. | `marketplace`, `social_distribution` |
| `local_ready` | Deterministic local logic; safe for demo + tests. | `creator`, `brain`, `world_game`, `safety`, `operator_admin` |
| `backend_ready` | Persistence/IO wired (DB, queue) but no external providers. | `render`, `wallet_entitlements`, `proof_history` |
| `provider_ready` | Paid provider integrations available, kept off by default. | (none yet) |
| `production_ready` | End-to-end live, with monitoring + on-call. | (none yet) |

Promotion rule: **never claim `production_ready` without on-call
documented in `docs/architecture/`.** Lower rungs are honest descriptions
of what's currently true; they are not failures.

## 3. Hard rules every engine honors

Encoded in `BackendEngine` and verified by
`lwa-backend/scripts/lint_engine_contract.py`:

- No paid provider call in the `_demo()` path.
- No payouts, no money mutation, ever.
- No external posting (TikTok / IG / X / YouTube / LinkedIn / Whop).
- No reads of secrets — secrets stay in `app/core/config.py` and
  `app/services/`.
- No writes to a real datastore from `_demo()`. Use input echo or
  in-memory return values.

## 4. Demo proof loop (the user-visible bridge)

```
   /demo stage
      │
      │  click "Open engine proof"
      ▼
   /engines/{engine_id}
      │
      │  click "Run safe demo"
      ▼
   POST /engines/{engine_id}/demo   ← unified API
      │
      ▼
   live JSON response with engine_id, summary, output, warnings
```

This is the bridge investors and creators can click through in three
clicks to verify that the demo journey is grounded in a real backend
module, not a story.

## 5. Frontend → backend connect

| Frontend file | Backend route | Purpose |
|---|---|---|
| `lib/backend-engines-api.ts` | `GET /engines` | Registry pull (typed client) |
| `components/engines/EngineHealthBadge.tsx` | `GET /engines/health` | Roll-up pill on `/engines` |
| `components/engines/BackendEngineRoomPanel.tsx` | `GET /engines`, `POST /engines/{id}/demo` | Engine room main grid |
| `components/engines/EngineDeepLinkPanel.tsx` | `GET /engines`, `POST /engines/{id}/demo` | Per-engine deep page |
| `components/engines/OperatorSnapshot.tsx` | `POST /engines/operator_admin/demo` | Live operator widget |
| `components/demo/LwaPublicDemoLoopPanel.tsx` | (none — Next.js Link only) | Demo → engine deep link |

Env var: `NEXT_PUBLIC_API_BASE_URL` (or alias `NEXT_PUBLIC_BACKEND_URL`).
If unset, all engine surfaces render an honest "backend not configured"
fallback. See `docs/deployment/LWA_FRONTEND_BACKEND_CONNECT.md`.

## 6. Per-engine Railway service (optional)

Same Python codebase, selected at boot by env var:

```
LWA_ENGINE_SERVICE_ID=<engine_id>
uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT
```

Each Railway service exposes:

```
GET  /                   service banner + selected engine id
GET  /health             liveness; never raises
GET  /engine             selected engine record
GET  /engine/health      selected engine health
POST /engine/demo        deterministic demo run
```

Deploy order is documented in
`docs/deployment/LWA_RAILWAY_ENGINE_SERVICES.md`. JSON templates per
engine live in `docs/deployment/railway-templates/`.

## 7. Cross-references

Read these when relevant:

- `docs/deployment/LWA_RAILWAY_ENGINE_SERVICES.md` — full Railway deploy doc, deploy order, founder UI steps.
- `docs/deployment/railway-engine-service-template.md` — single-service template values.
- `docs/deployment/LWA_FRONTEND_BACKEND_CONNECT.md` — env var guide for frontend.
- `docs/deployment/engines.http` — VS Code REST Client request collection.
- `lwa-backend/docs/HOW_TO_ADD_AN_ENGINE.md` — recipe to add a new engine in ~30 minutes.
- `docs/architecture/LWA_ACTUAL_BACKEND_ENGINE_FOUNDATION.md` — original foundation slice (kept for history).

## 8. Local dev quick reference

| Task | Command |
|---|---|
| List engine status from CLI | `make engine-cli ENGINE=operator_admin` (or `--list`) |
| Run engine demo locally (no server) | `cd lwa-backend && python3 scripts/engine_demo.py brain '{}'` |
| Boot main backend | `cd lwa-backend && uvicorn app.main:app --port 8000 --reload` |
| Boot single-engine service | `make engine-service ENGINE=brain PORT=8001` |
| Smoke test all engines via HTTP | `make smoke-engines` |
| Lint engine contract | `cd lwa-backend && python3 scripts/lint_engine_contract.py` |
| Engine tests only | `make backend-test` |
| Full dev (backend + frontend) | `./scripts/dev.sh` |

## 9. Forbidden areas (engine lane never touches)

- `lwa-ios/`
- `.env*` files
- `lwa-backend/app/api/routes/generate.py` (the `/generate` contract is owned by the clip-studio lane)
- `lwa-web/components/brain/LwaBrainEnginePanel.tsx` (Brain Panel lane)
- `lwa-web/lib/lwa-brain-engine.ts` (Brain Panel lane)
- `lwa-web/app/command-center/` (command-center lane)
- Any payment, payout, crypto, or external-posting code path

These are enforced by:

- `BackendEngine` contract (no provider/payout/posting allowed in `_demo`),
- `lint_engine_contract.py` (every engine module conforms),
- `.github/workflows/lwa-engine-tests.yml` (forbidden-area diff check on PRs).

## 10. When in doubt

Default to **add a new engine** rather than expanding an existing one,
and default to **demo-safe local logic** rather than a paid provider
call. The codebase is structured so that "more engines, narrower scope,
honest status" is always cheaper than "fewer engines, wider scope,
optimistic status".
