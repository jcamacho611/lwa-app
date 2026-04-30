# LWA Current Merge Audit

## Date

2026-04-30

## Purpose

Record what has been committed/merged so far, what was audited for duplicates, and what should happen next.

## Main branch status

The following docs/artifacts were committed directly to `main`:

- `docs/lwa-worlds/operations-playbook.md`
- `docs/lwa-worlds/investor-sales-artifact.md`
- `docs/lwa-worlds/founding-council-hiring-artifact.md`
- `docs/lwa-worlds/director-brain-algorithm-artifact.md`
- `docs/lwa-worlds/master-algorithm-database-stack.md`
- `docs/lwa-worlds/sql/lwa_algorithm_foundation.sql`
- `docs/lwa-worlds/README.md` updates linking new artifacts
- `docs/lwa-worlds/codex-prompt-pack.md` expanded with algorithm, frontend, Whop, launch, and database prompts
- `docs/company/lwa-remaining-work-checklist.md`
- `docs/company/lwa-file-creation-and-duplicate-policy.md`

## PR status

PR #37, `backend: add Whop verified webhook MVP`, is already merged.

Merged functionality from PR #37:

- Whop webhook service
- signed webhook route
- idempotent event storage
- user plan update by verified email event
- tests for signature, mapping, replay, upgrade/downgrade behavior

Explicitly not included in PR #37:

- marketplace payouts
- seller balances
- Stripe Connect movement
- Whop submerchant payouts
- iOS changes
- frontend changes

## Director Brain support module audit

The following backend support modules exist on `main` and should not be duplicated:

- `lwa-backend/app/services/platform_signals.py`
- `lwa-backend/app/services/hook_engine.py`
- `lwa-backend/app/services/caption_style_engine.py`
- `lwa-backend/app/services/offer_detector.py`
- `lwa-backend/app/services/quality_gate.py`
- `lwa-backend/app/services/fallback_engine.py`
- `lwa-backend/app/services/creator_profile.py`
- `lwa-backend/app/services/campaign_engine.py`
- `lwa-backend/app/services/learning_loop.py`

The support-module tests exist at:

- `lwa-backend/tests/test_director_brain_support_modules.py`

## Frontend Director Brain display audit

The frontend type contract already includes optional Director Brain, quality gate, offer, campaign, render, and strategy-only fields in:

- `lwa-web/lib/types.ts`

The frontend display already renders the Director Brain package panel and separates rendered vs strategy-only clips in:

- `lwa-web/components/VideoCard.tsx`

## Backend generation integration audit

The generation route preserves `/generate`, `/process`, and `/v1/generate` and calls `build_clip_response` in:

- `lwa-backend/app/api/routes/generate.py`

The backend clip service already calls `apply_director_brain_foundation(...)` inside `build_clip_response` and includes rendered/strategy-only counts in the processing summary in:

- `lwa-backend/app/services/clip_service.py`

## Duplicate decision

No duplicate files were deleted during this audit.

Council decision:

- Keep `docs/company/*` as repo operating-system docs.
- Keep `docs/lwa-worlds/*` as execution artifacts and prompt packs.
- Keep `docs/lwa-worlds/sql/lwa_algorithm_foundation.sql` as a SQL migration blueprint, not a live production migration.
- Keep backend service modules as implementation scaffolds.
- Do not merge `feat/director-brain-support-modules` because it has no unique commits ahead of `main`.

## Deployment status note

The active LWA project Railway backend/frontend statuses are successful for the latest checked commit:

- `LWA PROJECT - lwa-backend`: success
- `LWA PROJECT - lwa the god app`: success

A separate/older Railway status context named `profound-growth - lwa-backend` was observed as failing. Do not treat that as active-app blocking unless it is confirmed to be the active production service.

## Remaining work

### P0

- Run backend compile/tests in local or Codex environment.
- Run frontend type-check/build in local or Codex environment.
- Smoke test `/health` and `/v1/generate` on Railway.
- Confirm Whop webhook delivery before claiming live paid entitlement enforcement.

### P1

- Deepen actual scoring output from Director Brain support modules into every generated clip, if current generated output is still using fallbacks.
- Expand campaign role generation after production smoke tests pass.
- Add operator dashboard metrics after generation event data is stable.

### P2

- Decide whether to migrate SQL blueprint into real migrations after current store strategy is confirmed.

### Future

- Marketplace scaffold only after trust/safety and webhook verification.
- Realms static shell only after core clipping flow is strong.
- Social OAuth/status shell only after token encryption and provider scope plan.
- Off-chain proof dry run only; no mainnet/blockchain feature unlocks.
