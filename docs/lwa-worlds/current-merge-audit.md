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

## Duplicate decision

No duplicate files were deleted during this audit.

Council decision:

- Keep `docs/company/*` as repo operating-system docs.
- Keep `docs/lwa-worlds/*` as execution artifacts and prompt packs.
- Keep `docs/lwa-worlds/sql/lwa_algorithm_foundation.sql` as a SQL migration blueprint, not a live production migration.
- Keep backend service modules as implementation scaffolds.
- Do not merge `feat/director-brain-support-modules` because it has no unique commits ahead of `main`.

## Deployment status note

The active LWA project Railway backend/frontend statuses were observed as successful.

A separate/older Railway status context named `profound-growth - lwa-backend` was observed as failing. Do not treat that as active-app blocking unless it is confirmed to be the active production service.

## Remaining work

### P0

- Verify backend tests after Whop + Director Brain modules.
- Verify frontend build/type-check.
- Smoke test `/health` and `/v1/generate` on Railway.
- Confirm Whop env vars on Railway:
  - `LWA_ENABLE_WHOP_VERIFICATION=true`
  - `WHOP_WEBHOOK_SECRET`
  - `WHOP_API_KEY`
  - `WHOP_COMPANY_ID`
  - `WHOP_PRODUCT_ID`

### P1

- Wire Director Brain support modules into generation output behind safe optional fields.
- Display Director Brain optional fields in `lwa-web` without fake playable clips.
- Add campaign role display after backend campaign fields are proven.

### P2

- Decide whether to migrate SQL blueprint into real migrations after current store strategy is confirmed.
- Add operator dashboard queries/views.

### Future

- Marketplace scaffold only after trust/safety and webhook verification.
- Realms static shell only after core clipping flow is strong.
- Social OAuth/status shell only after token encryption and provider scope plan.
- Off-chain proof dry run only; no mainnet/blockchain feature unlocks.
