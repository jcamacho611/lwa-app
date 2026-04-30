# LWA Codex Chunk Sequence

## Status

This file converts the current LWA master stack into sequential Codex chunks. It is designed to prevent Codex from burning credits by implementing the wrong architecture or mixing unrelated systems into one PR.

Use this with:

- `docs/company/lwa-github-codex-master-fusion-prompt.md`
- `docs/company/lwa-claude-codex-fusion-guardrails.md`
- `docs/lwa-worlds-master-council-report.md`
- `docs/lwa-worlds-mandatory-doctrine.md`
- `docs/company/lwa-codex-execution-ledger.md`
- `docs/company/lwa-autonomous-codex-execution-brief.md`

## Chunk 15 — Master Repo Fusion + Implementation Status Map

Goal:

Fuse the master docs into GitHub, audit actual repo state, correct path assumptions, and create a living implementation status map.

Do:

- Run repo audit.
- Confirm actual backend/frontend paths.
- Fuse/update docs under `docs/company/`.
- Create/update `docs/company/lwa-implementation-status.md`.
- Create/update `docs/company/lwa-architecture-compatibility-map.md`.
- Create/update `docs/company/lwa-source-of-truth.md`.
- No runtime code unless the audit proves a tiny docs-linked correction is required.

Do not:

- Start marketplace.
- Start Realms.
- Start blockchain.
- Start social integrations.
- Touch `lwa-ios/`.

Prompt source:

- `docs/company/lwa-github-codex-master-fusion-prompt.md`

## Chunk 16 — Source Handling / FREE_LAUNCH / Fallback Hardening

Goal:

Implement the single safest P0 product-hardening slice selected by the Chunk 15 audit.

Priority order:

1. Source handling hardening if source contracts are inconsistent.
2. `FREE_LAUNCH_MODE` if missing/incomplete.
3. deterministic fallback hardening if provider/source failures still 500.
4. README polish if A-C are already done.

Do:

- Preserve `/health`, `/v1/generate`, `/v1/jobs`, `/v1/uploads`.
- Preserve Source POC runner.
- Preserve entitlements/quota.
- Preserve revenue events.
- Preserve generated asset retention.

Do not:

- Start marketplace.
- Start Realms.
- Start Stripe/Whop payouts.
- Start blockchain.
- Touch `lwa-ios/`.

## Chunk 17 — Director Brain v0 + Platform Prompt Pack

Goal:

Add the first Director Brain layer without destabilizing generation.

Do:

- Add/adapt `director_brain` service.
- Add platform-aware prompt packs.
- Implement TikTok/Reels/Shorts/LinkedIn reasoning modes.
- Reuse existing Claude/OpenAI routing if present.
- Keep OpenAI-first or fallback mode when Claude is disabled.
- Add tests/evals for output shape and provider fallback.

Do not:

- Duplicate Claude provider routing.
- Claim guaranteed virality.
- Rewrite the generation pipeline.

## Chunk 18 — Caption Preset Renderer + Hook Formula Library

Goal:

Install the Master Council platform signal database as real structured product data.

Do:

- Add 20 hook formulas as data/templates.
- Add 14 category modifiers as structured data.
- Add 7 caption presets as overlay specs.
- Add tests for formula/category/preset retrieval.
- Connect to Director Brain if safe.

Do not:

- Force full pixel-perfect FFmpeg rendering if overlay specs are the safer first step.

## Chunk 19 — Frontend Premium Generate Flow Polish

Goal:

Improve the revenue-facing generate flow while preserving working app behavior.

Do:

- Tighten first-use flow.
- Improve source upload copy.
- Show public URLs as best-effort.
- Preserve CTA/revenue event tracking.
- Preserve generated result cards and playable asset behavior.
- Use premium dark creator-native language.

Do not:

- Replace the app shell.
- Hide working outputs.
- Break `/generate`.

## Chunk 20 — Marketplace Compatibility Audit, Docs-Only First

Goal:

Determine how marketplace should fit the actual repo persistence and route structure.

Do:

- Audit backend persistence pattern.
- Decide whether to use current store pattern, SQLite, Postgres, SQLAlchemy, Alembic, or migration plan.
- Create marketplace implementation map.
- Create safety copy and banned category docs.
- No live money movement.

Do not:

- Add Stripe transfers.
- Add live seller onboarding.
- Add payout cron.

## Chunk 21 — Marketplace MVP Dark Scaffold, No Live Payouts

Goal:

Add marketplace route/page/backend scaffold with safe placeholder states.

Do:

- Products/jobs/campaigns scaffold.
- Seller profile placeholder.
- Orders/payout statuses as mock/internal safe state.
- Dispute/review/takedown states.
- Earnings disclaimers.
- Integer cents only if money fields exist.

Do not:

- Move real money.
- Verify payments unless webhook infrastructure is implemented and tested.

## Chunk 22 — Realms Static Content + Profile Shell, No Blockchain

Goal:

Install The Signal Realms as app identity/progression shell.

Do:

- Classes.
- Factions.
- Quest content.
- Badge/relic catalogs.
- Profile shell.
- XP formula helpers.
- Cosmetic-only copy.

Do not:

- Sell XP.
- Unlock app features with relics.
- Add chain writes.

## Chunk 23 — Social API OAuth Shell, No Posting Until Approved

Goal:

Add integration scaffolds without unsafe platform actions.

Do:

- Provider config/env docs.
- OAuth start/callback shells where safe.
- Integration status endpoint/page.
- Polymarket read-only trend plan/ingestor if compatible.

Do not:

- Post to TikTok/Instagram/YouTube without approval.
- Store social tokens without encryption.
- Add betting/trading flows.

## Chunk 24 — Off-Chain Proof / Merkle Dry Run, No Mainnet

Goal:

Add optional provenance foundation without crypto risk.

Do:

- Issuance abstraction.
- Deterministic hashable records.
- Daily Merkle snapshot dry-run.
- Proof UI copy.

Do not:

- Deploy contracts.
- Add NFT purchases.
- Add tokenomics.
- Add investment language.

## Standard Final Report For Every Chunk

Codex must return:

1. Branch and starting commit.
2. Files inspected.
3. Source docs used.
4. Protected files detected.
5. Files changed.
6. What was implemented.
7. What was preserved.
8. Tests run.
9. Blockers.
10. Commit hash/message.
11. Next chunk prompt.

## Immediate Next Prompt

Use `docs/company/lwa-github-codex-master-fusion-prompt.md` for Chunk 15.
