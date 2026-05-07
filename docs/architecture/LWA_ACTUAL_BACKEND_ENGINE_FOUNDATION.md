# LWA Actual Backend Engine Foundation

## Purpose

This document describes the **actual Python backend engine modules** added to `lwa-backend`. These are not frontend TypeScript libraries, UI panels, or mock route stubs — they are real, importable, testable Python modules that live in `lwa-backend/app/engines/` and form the modular foundation for all future LWA backend work.

---

## What Was Added

### Engine Modules (`lwa-backend/app/engines/`)

| Module | Engine ID | Status | Purpose |
|---|---|---|---|
| `creator.py` | `creator` | LOCAL_READY | Hook generation, caption packaging, clip prioritization |
| `brain.py` | `brain` | LOCAL_READY | Provider routing, style selection, confidence reasoning |
| `render.py` | `render` | SCAFFOLDED | Render plan, asset selection, queue handoff |
| `marketplace.py` | `marketplace` | SCAFFOLDED | Campaign matching, opportunity surfacing |
| `wallet_entitlements.py` | `wallet_entitlements` | SCAFFOLDED | Credit checking, plan gate enforcement |
| `proof_history.py` | `proof_history` | LOCAL_READY | Proof record shaping, audit summary |
| `world_game.py` | `world_game` | LOCAL_READY | Mission progress, XP preview, Lee-Wuh guidance |
| `safety.py` | `safety` | LOCAL_READY | Source risk check, money flow guard, provider guard |
| `social_distribution.py` | `social_distribution` | SCAFFOLDED | Post packaging, schedule planning |
| `operator_admin.py` | `operator_admin` | LOCAL_READY | System readiness summary, launch gate status |

### Supporting Files

- **`base.py`** — Abstract `LwaEngine` base class, `EngineStatus` enum, `EngineCapability`, `EngineHealth`, `EngineDemoResult` dataclasses, and safe payload helpers (`safe_payload`, `text_value`, `number_value`).
- **`registry.py`** — Engine registry and factory: `get_engine_registry()`, `get_engine()`, `get_engine_health()`, `run_engine_demo()`, `engine_ids()`.
- **`__init__.py`** — Package exports for all public types and registry functions.

### Routes (`lwa-backend/app/api/routes/engines.py`)

Four new endpoints registered at `/engines`:

| Method | Path | Description |
|---|---|---|
| GET | `/engines` | List all engines with metadata |
| GET | `/engines/health` | Health status for all engines |
| GET | `/engines/{engine_id}` | Metadata for a single engine |
| POST | `/engines/{engine_id}/demo` | Run a safe local demo for an engine |

### Tests (`lwa-backend/tests/test_engines.py`)

Comprehensive test suite covering:
- Registry completeness (all 10 engines present)
- Health snapshots for every engine
- Invalid engine ID handling
- Parametrized `demo_run()` for every engine
- No engine claims `PRODUCTION_READY` by default
- Safety gates: wallet engine blocks payouts
- Safety gates: social engine blocks posting
- Safety gates: render engine blocks paid provider calls
- Capability consistency (payment capabilities not marked local_safe)
- JSON serialisability of all engine metadata

---

## Safety Gates

Every engine at `SCAFFOLDED` or `LOCAL_READY` status enforces hard safety gates:

| Gate | Enforced By |
|---|---|
| No payment processing | `WalletEntitlementsEngine` — `payment_blocked: True` |
| No payout execution | `WalletEntitlementsEngine` — `payout_blocked: True` |
| No social posting | `SocialDistributionEngine` — `posting_blocked: True` |
| No render provider calls | `RenderEngine` — `execution_blocked: True` |
| No real campaign claims | `MarketplaceEngine` — `claims_blocked: True` |
| No database writes | `ProofHistoryEngine` — `written: False` |
| No ledger writes | `WorldGameEngine` — `ledger_write_blocked: True` |
| No external actions | `SafetyEngine` — `no_external_action_taken: True` |

These gates are tested in `test_engines.py` and will remain enforced until each engine is explicitly promoted to `BACKEND_READY` or higher with the appropriate provider integrations in place.

---

## Engine Status Lifecycle

```
SCAFFOLDED → LOCAL_READY → BACKEND_READY → PROVIDER_READY → PRODUCTION_READY
```

| Status | Meaning |
|---|---|
| `SCAFFOLDED` | Shape defined; deterministic demo only |
| `LOCAL_READY` | Full local logic; no external provider needed |
| `BACKEND_READY` | Integrated with internal services (DB, job queue) |
| `PROVIDER_READY` | Connected to at least one external provider |
| `PRODUCTION_READY` | Fully tested, monitored, production traffic safe |

**No engine starts at `PRODUCTION_READY`.** This status must be earned through integration, testing, and monitoring.

---

## Current Status Summary

As of initial foundation:

- **LOCAL_READY**: `creator`, `brain`, `proof_history`, `world_game`, `safety`, `operator_admin`
- **SCAFFOLDED**: `render`, `marketplace`, `wallet_entitlements`, `social_distribution`
- **PRODUCTION_READY**: none

---

## Why Railway Still Shows Few Services

All 10 engine modules live **inside the `lwa-backend` FastAPI service**. They are not separate Railway services yet. This is intentional — the foundation is built as a monolith first, then individual engines can be extracted into separate services as they reach `PRODUCTION_READY` status and justify the operational overhead.

---

## Future Deployment Roadmap

When an engine reaches `PRODUCTION_READY`, it can be extracted into its own Railway service:

| Engine | Potential Future Service |
|---|---|
| `render` | `lwa-render-worker` |
| `social_distribution` | `lwa-social-worker` |
| `marketplace` | `lwa-marketplace-api` |
| `wallet_entitlements` | `lwa-wallet-api` |
| `brain` | `lwa-brain-api` |

Until then, all engines are accessible via the `/engines` routes on the existing `lwa-backend` service.

---

## No New Secrets Required

All engines at `SCAFFOLDED` and `LOCAL_READY` status require **zero new environment variables or secrets**. They are fully testable with `pytest` in a local environment with no external dependencies.

---

## Existing Routes Preserved

The engine foundation does not modify any existing routes. The following contracts are unchanged:

- `POST /generate` — clip generation
- `POST /v1/jobs` — async job creation
- `GET /v1/jobs/{job_id}` — job status
- `GET /health` — service health
