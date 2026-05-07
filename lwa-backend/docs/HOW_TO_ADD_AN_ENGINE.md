# How to add a new LWA backend engine

Adding a new engine should take ~30 minutes if you follow the existing
pattern. Every new engine automatically becomes:

- discoverable via `GET /engines` and `GET /engines/health`,
- demo-runnable via `POST /engines/<id>/demo`,
- deployable as its own Railway service via the generic
  `engine_service_app.py` (set `LWA_ENGINE_SERVICE_ID=<id>`),
- testable from the local CLI: `python scripts/engine_demo.py <id> '{}'`.

---

## 1. Pick an honest status

Allowed: `scaffolded`, `local_ready`, `backend_ready`, `provider_ready`,
`production_ready`. Default to `scaffolded` until the engine has
deterministic local logic. A new engine should never claim
`production_ready` until on-call exists for it.

## 2. Create the engine module

File: `lwa-backend/app/engines/<engine_id>.py`

Use the existing `BackendEngine` dataclass from `app/engines/base.py`:

```python
from __future__ import annotations
from typing import Any
from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    return build_demo_result(
        summary="<engine_id> engine returned a deterministic local result.",
        output={"received": dict(payload)},
        warnings=["Local-only — no provider or external action."],
    )


ENGINE = BackendEngine(
    engine_id="<engine_id>",
    name="<Engine Display Name>",
    status="local_ready",
    capabilities_list=(
        capability("<cap_id>", "<Cap Label>", "<one-line description>"),
    ),
    next_required_integrations_list=(
        "<what is needed to advance status one step>",
    ),
    demo_summary="<one-line demo summary>",
    demo_runner=_demo,
)

# Re-export the contract at module level (registry import expects this)
engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
```

## 3. Register the engine

Edit `lwa-backend/app/engines/registry.py`:

1. `from .<engine_id> import ENGINE as <engine_id>_engine`
2. Append `<engine_id>_engine` to the `ENGINE_REGISTRY` tuple — placement
   in the tuple controls UI order on the engine room page.

That's it for backend wiring. The unified `/engines` route picks it up
automatically.

## 4. Update consumer-facing metadata (optional but recommended)

These are **frontend** files; only touch them when you also want the
engine to appear in the demo journey UI and Railway deploy docs.

- `lwa-web/lib/lwa-engine-stage-map.ts`
  Add a binding to `LWA_ENGINE_STAGE_BINDINGS` so a demo stage points at
  the new engine. Add the engine id to the `LwaBackendEngineId` union.

- `lwa-web/lib/lwa-engine-deploy-order.ts`
  Append a record to `LWA_ENGINE_DEPLOY_ORDER` with the recommended
  Railway deploy order, risk level, and `safeForDemo` flag.

- `docs/deployment/LWA_RAILWAY_ENGINE_SERVICES.md`
  Add the engine to the Section 5 deploy-order table.

- `docs/deployment/railway-templates/`
  Optionally add a `railway.<engine_id>.json` template (run the helper
  script in `docs/deployment/LWA_RAILWAY_ENGINE_SERVICES.md`).

- `docs/deployment/engines.http`
  Add a request block so anyone can hit the new engine's demo route.

- `scripts/smoke_engines.sh`
  Append the new id to the `ENGINES` array and a `SAMPLE_PAYLOAD` entry.

## 5. Add tests

File: `lwa-backend/tests/test_<engine_id>_demo.py` (optional) — at minimum,
the existing `tests/test_engines.py` will already exercise the new
engine because it iterates the registry.

## 6. Validate

```bash
cd lwa-backend
python3 scripts/engine_demo.py --list                  # new engine should appear
python3 scripts/engine_demo.py <engine_id> '{}'        # demo path returns dict
python3 -m compileall -q app
python3 -m pytest tests/test_engines.py -q

cd ..
./scripts/smoke_engines.sh                              # all 11+ pass
make web-typecheck                                      # tsc clean
```

## 7. Deploy decision

A new engine **does not** automatically become a Railway service. It
ships in the main backend's `/engines` route from day one. Promotion to
its own Railway service is a separate, intentional action — see
`docs/deployment/LWA_RAILWAY_ENGINE_SERVICES.md` Section 7 for the UI
steps.

## Hard rules

- Never `executes_payouts`, `posts_to_social`, or `calls_paid_providers`
  inside the `_demo` path.
- Never write to a real datastore from `_demo`. Use input echoing or
  in-memory return values.
- Never claim `production_ready` until the engine has on-call coverage
  documented in `docs/architecture/`.
- Never read environment secrets in the engine module — secrets belong
  in `app/core/config.py` and `services/`.
