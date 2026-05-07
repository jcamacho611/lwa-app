# Railway Engine Service Template

Use this template when creating a new Railway service for an LWA engine.
One template, ten possible services — they only differ by
`LWA_ENGINE_SERVICE_ID`.

---

## Service settings (Railway UI)

| Field | Value |
|---|---|
| **Service name** | `lwa-engine-<engine_id>` (e.g. `lwa-engine-operator-admin`) |
| **GitHub repo** | `jcamacho611/lwa-app` |
| **Branch** | `main` after merge (or `claude/railway-engine-services` while reviewing this slice) |
| **Root directory** | repo root (default) |
| **Start command** | `cd lwa-backend && uvicorn app.services.engine_service_app:app --host 0.0.0.0 --port $PORT` |
| **Healthcheck path** | `/health` |
| **Healthcheck timeout** | 30s |
| **Restart policy** | On failure (default) |

## Required environment variable

| Variable | Allowed values |
|---|---|
| `LWA_ENGINE_SERVICE_ID` | `creator`, `brain`, `render`, `marketplace`, `wallet_entitlements`, `proof_history`, `world_game`, `safety`, `social_distribution`, `operator_admin` |

If unset, the service falls back to `operator_admin`.

## Smoke test after deploy

```bash
curl -fsS https://<service-domain>/health | jq
curl -fsS https://<service-domain>/engine | jq '.engine_id, .status'
curl -fsS https://<service-domain>/engine/health | jq '.healthy, .warnings'
curl -fsS -X POST https://<service-domain>/engine/demo \
  -H 'content-type: application/json' \
  -d '{}' | jq '.engine_id, .summary'
```

All four calls must return `200`. The `engine_id` returned by `/engine`
must match the value of `LWA_ENGINE_SERVICE_ID` set in the Railway
service variables.

## Safety rules per service

Every engine service must continue to honor:

- no paid provider calls,
- no payouts or money mutation,
- no external posting,
- no `/generate` change,
- no `.env`-managed secret consumption beyond what the main backend
  already requires,
- no admin / destructive routes.

If a future engine breaks any of these, it must move to a *new* service
with its own safety contract, not be slipped into this template.

## Deploy order reminder

Do not deploy all 10 at once. Stage in this order:

1. `operator_admin` — safest read-only roll-up.
2. `safety` — local guard rails.
3. `proof_history` — demo proofs.
4. `world_game` — missions/XP preview.
5. `brain` — keep provider routing OFF.
6. `render` — strategy-only fallback only.
7. `creator` — mission seed.
8. `wallet_entitlements` — read-only.
9. `marketplace` — teaser only.
10. `social_distribution` — recommendations only.

See `LWA_RAILWAY_ENGINE_SERVICES.md` for the full rationale.
