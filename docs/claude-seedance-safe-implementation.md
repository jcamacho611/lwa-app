# Claude + Seedance Safe Implementation Brief

**Repo:** `jcamacho611/lwa-app`  
**Branch:** `dev`  
**Intent:** strengthen LWA without breaking current working flows.

## Goal

Turn LWA into a stronger real clipping engine by:

1. adding **Claude** as a first-class intelligence provider now
2. adding **Seedance** as a safe adapter/integration surface now
3. preserving all existing working product flows

---

## Non-negotiable preservation rules

- Preserve all existing working flows
- Do not rebuild the app
- Do not replace the current clipping engine
- Do not remove current OpenAI, fallback, or existing generation behavior
- Do not rename stable routes unless absolutely required
- Do not break Railway deployment assumptions
- Do not break Whop/customer-facing flow
- Do not delete files just to clean things up
- Do not perform a giant refactor
- Use additive changes
- If something is uncertain, isolate it behind a new adapter/service instead of touching stable code
- Seedance must never become a breaking dependency
- Homepage and current generation must still work when Seedance is disabled

---

## Current backend seams to build on top of

Use the existing seams instead of replacing them:

- `lwa-backend/app/api/routes/generate.py`
- `lwa-backend/app/services/clip_service.py`
- `lwa-backend/app/generation.py`
- `lwa-backend/app/services/ai_service.py`
- `lwa-backend/app/core/config.py`

---

## Phase 1 — Claude integration live now

### Extend config in `lwa-backend/app/core/config.py`

Add support for:

- `ANTHROPIC_API_KEY`
- `ANTHROPIC_MODEL_OPUS`
- `ANTHROPIC_MODEL_SONNET`
- `ANTHROPIC_MODEL_HAIKU`
- `LWA_ENABLE_ANTHROPIC`
- `LWA_PREMIUM_REASONING_PROVIDER`

Preserve:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `LWA_AI_PROVIDER`
- fallback behavior
- Ollama support if already present

### Update requirements

In `lwa-backend/requirements.txt` add the official Anthropic SDK without removing existing dependencies.

### Add service

Create:

- `lwa-backend/app/services/anthropic_service.py`

Responsibilities:

- Sonnet as normal production intelligence
- Opus as premium/high-depth reasoning
- Haiku for cleanup/tagging if useful
- stronger:
  - hooks
  - hook variants
  - captions
  - caption variants
  - thumbnail text
  - CTA suggestions
  - packaging-angle consistency
  - why-this-matters
  - ranking quality
- normalize output into existing clip schema expectations
- preserve strict malformed-output fallback behavior

### Refactor provider routing safely

Update:

- `lwa-backend/app/generation.py`
- `lwa-backend/app/services/ai_service.py`

Required behavior:

- current behavior must keep working
- add provider support for:
  - `anthropic`
  - `openai`
  - `ollama`
  - `fallback`
- when `LWA_AI_PROVIDER=auto`:
  - prefer Anthropic if `ANTHROPIC_API_KEY` exists
  - otherwise OpenAI if `OPENAI_API_KEY` exists
  - otherwise Ollama if configured
  - otherwise fallback

### Premium reasoning behavior

If repo already has plan/entitlement logic, reuse it.
Do not invent a new billing system.

Expected behavior:

- regular/basic flows can use Sonnet
- premium flows can use Opus for better ranking, packaging analysis, reasoning, and explanation quality

---

## Phase 2 — Seedance adapter now, without fake live assumptions

### Critical rule

Do **not** fake a live Seedance API contract.

Implement Seedance as a safe provider adapter with strict env validation and graceful failure.
Do not hardcode guessed auth headers or guessed polling endpoints across the codebase.

### Extend config in `lwa-backend/app/core/config.py`

Add:

- `SEEDANCE_ENABLED=false`
- `SEEDANCE_API_KEY`
- `SEEDANCE_BASE_URL`
- `SEEDANCE_MODEL`
- `SEEDANCE_TIMEOUT_SECONDS`
- `SEEDANCE_POLL_INTERVAL_SECONDS`

### Add service

Create:

- `lwa-backend/app/services/seedance_service.py`

Responsibilities:

- expose a clean adapter boundary
- validate env/config
- build premium visual enhancement/background prompts
- isolate all external HTTP/provider specifics here only
- support:
  - `seedance_available(settings)`
  - `submit_seedance_job(...)`
  - `poll_seedance_job(...)`
  - `download_seedance_asset(...)`
  - `generate_seedance_background(...)`
  - `enhance_clip_with_seedance(...)`
- if contract details are missing or env vars are absent, raise a clear controlled error
- never break normal clip generation
- never expose provider secrets to the frontend

### Add schemas if needed

Prefer additive schema support for:

- Seedance background request
- Seedance job response
- Seedance job status response
- Seedance asset response

Support fields such as:

- `prompt`
- `style_preset`
- `motion_profile`
- `duration_seconds`
- `aspect_ratio`
- `seed`
- optional `reference_image_url`
- optional `source_clip_url`
- optional `source_asset_id`

### Add routes

Create:

- `lwa-backend/app/api/routes/seedance.py`

Routes:

- `POST /v1/seedance/background`
- `GET /v1/seedance/jobs/{job_id}`

Behavior:

- validate request body
- return clean disabled/misconfigured responses when Seedance is off
- keep this separate from current `/generate`, `/process`, and `/v1/jobs`
- persist job state using existing repo patterns where practical
- never interfere with the existing clip generation pipeline

### Register route safely

Update app startup/router registration without disturbing current routes.

### Asset persistence

Use the same generated asset/storage conventions already used by the repo.
Do not invent a second storage system unless absolutely necessary.

---

## Phase 3 — Frontend integration without damage

Find the current homepage/hero/background shell and current AI background component.

Add a non-breaking Seedance-enabled premium background mode that:

- does not block initial render
- falls back immediately to the existing background experience if Seedance is unavailable
- does not clutter the UI
- can optionally surface a premium animated scene/background asset
- preserves the current look and feel when disabled

Do not turn the homepage into a fragile experimental feature.

---

## Phase 4 — Safety, tests, and docs

### Add doc

Create/update:

- `docs/claude-seedance-integration.md`

Document:

- new env vars
- provider routing behavior
- fallback behavior
- what is live now
- what is adapter-only pending exact Seedance contract confirmation
- how to enable/disable Anthropic
- how to enable/disable Seedance safely

### Add checks/tests where reasonable

Cover:

- provider selection
- Anthropic fallback behavior
- Seedance disabled behavior
- schema normalization
- malformed model output fallback
- startup/import safety

---

## Work style requirements

- Make the smallest safe changes first
- Reuse current patterns before inventing new abstractions
- Keep changes localized
- Prefer new files over risky rewrites of stable files
- If a file must be edited, change only the minimum necessary sections
- Comment clearly where something is intentionally adapter-only pending vendor contract details

---

## Absolutely do not do these things

- do not rewrite the app architecture
- do not switch everything to Seedance
- do not remove OpenAI support
- do not delete fallback behavior
- do not rename stable API routes for style reasons
- do not break homepage rendering
- do not break Railway deployment
- do not silently ship guessed Seedance endpoint logic as if it were confirmed
- do not make unrelated cleanup edits

---

## Deliverable format

When implementation is done, report:

1. files changed
2. what each change does
3. env vars that must be set
4. anything still blocked specifically by missing Seedance API contract details
5. confirmation that current working flows were preserved
