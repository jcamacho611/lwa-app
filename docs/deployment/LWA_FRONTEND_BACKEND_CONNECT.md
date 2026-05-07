# LWA Frontend ↔ Backend Connect

How the LWA frontend (`lwa-web`) talks to the backend `/engines` API and
the per-engine Railway services. Audit this doc when:

- a Railway service is deployed and its URL needs to reach the frontend,
- engine cards on `/engines` or `/engines/[engineId]` show "backend not
  configured",
- the `EngineHealthBadge` widget reads "engines · backend not configured".

---

## 1. Required env vars (frontend, `lwa-web`)

| Variable | Where | What it does |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Vercel / Railway frontend service | Base URL of the **main backend** (e.g. `https://api.lwa.example.com`). Read by `lib/backend-engines-api.ts` and `components/engines/EngineHealthBadge.tsx`. Falls back to `NEXT_PUBLIC_BACKEND_URL`. |
| `NEXT_PUBLIC_BACKEND_URL` | Vercel / Railway frontend service | Backwards-compatible alias used by some older lib files. |

If neither is set, the frontend renders honest fallback content: each
engine card shows "Local fallback shown because backend engine API is
not configured or unreachable", and the health badge shows
"engines · backend not configured". The page never throws.

## 2. Backend routes the frontend uses

| Route | Purpose | Used by |
|---|---|---|
| `GET /engines` | Full engine registry (10 engine records) | `/engines` page, `/engines/[engineId]` page |
| `GET /engines/health` | Per-engine + roll-up health snapshot | `EngineHealthBadge` |
| `GET /engines/{engine_id}` | Single engine record | available via the registry; deep page filters in client |
| `POST /engines/{engine_id}/demo` | Deterministic demo run | "Run safe demo" buttons on `/engines` and `/engines/[engineId]` |

These routes already exist in the **main backend** at
`lwa-backend/app/api/routes/engines.py`. No new backend route is added by
the connect layer.

## 3. Optional: per-engine Railway services

Once an engine is deployed as its own Railway service (see
`LWA_RAILWAY_ENGINE_SERVICES.md`), the per-engine URL is **separate**
from the main backend URL. The frontend currently calls the **main
backend**'s `/engines` route only. That's intentional — one URL, one
typed client.

If you ever want a frontend to call a single per-engine service
directly (e.g. an internal operator dashboard), point a separate
client at:

```
GET  https://lwa-engine-<id>.example.com/health
GET  https://lwa-engine-<id>.example.com/engine
GET  https://lwa-engine-<id>.example.com/engine/health
POST https://lwa-engine-<id>.example.com/engine/demo
```

Do not add a `NEXT_PUBLIC_*` variable per engine in the consumer-facing
frontend. Keep per-engine URLs server-side, behind admin auth.

## 4. Local development

```bash
# terminal 1 — backend
cd /Users/bdm/LWA/lwa-app/lwa-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# terminal 2 — frontend
cd /Users/bdm/LWA/lwa-app/lwa-web
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Then open:

- `http://localhost:3000/engines` — engine room (list of 10)
- `http://localhost:3000/engines/operator_admin` — deep link
- `http://localhost:3000/engines/world_game` — deep link
- `http://localhost:3000/demo` — public demo journey

Click "Run safe demo" on any engine card. You should see a JSON response
from the backend with `engine_id`, `summary`, `output`, and `warnings`.

## 5. Verify the connect (smoke test)

```bash
# Direct backend smoke
curl -fsS http://localhost:8000/engines | jq '.count, .engines | keys[:3]'
curl -fsS http://localhost:8000/engines/health | jq '.healthy_count, .count'
curl -fsS -X POST http://localhost:8000/engines/operator_admin/demo \
  -H 'content-type: application/json' -d '{}' | jq '.engine_id, .status'

# Frontend health badge
# open /engines and watch the top-right badge: "X/10 engines healthy"
```

## 6. Stage → engine map (for the public demo)

The `/demo` route's nine-stage journey binds each stage to a backend
engine via `lib/lwa-engine-stage-map.ts`. This lets investors and
creators see that the demo flow is grounded in real backend modules:

| Stage | Engine |
|---|---|
| `landing` | `operator_admin` |
| `first_mission` | `creator` |
| `source_added` | `creator` |
| `clips_ready` | `brain` |
| `recovery_available` | `render` |
| `proof_saved` | `proof_history` |
| `signal_sprint` | `world_game` |
| `marketplace_teaser` | `marketplace` |
| `return_loop` | `social_distribution` |

The mapping is data only. The demo page may render an "open in engine
room" link per stage that deep-links to `/engines/{engine_id}`.

## 7. What is intentionally not connected

- No payment, payout, or crypto endpoint is wired from the frontend.
- No auth-required admin routes are wired in this lane.
- The frontend never calls `/generate` from the engine surfaces; that
  remains the existing clip-studio path.
- The frontend never calls a per-engine Railway service directly from a
  consumer-facing page; only the main backend `/engines` route.

## 8. Files added by the connect slice

```
lwa-web/lib/lwa-engine-stage-map.ts
lwa-web/components/engines/EngineHealthBadge.tsx
lwa-web/components/engines/EngineDeepLinkPanel.tsx
lwa-web/app/engines/[engineId]/page.tsx
docs/deployment/LWA_FRONTEND_BACKEND_CONNECT.md   (this file)
```

The previously committed pieces — `lib/backend-engines-api.ts`,
`components/engines/BackendEngineRoomPanel.tsx`, and
`app/engines/page.tsx` — are unchanged.
