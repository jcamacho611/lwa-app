# LWA Claude + Codex Fusion Guardrails

## Status

This file exists to protect completed Claude/Codex work while LWA Worlds is fused into the repo and prepared for pull, push, commit, PR review, and merge to `main`.

The founder has identified the Claude work as protected implementation context. Future agents must not overwrite it, casually rewrite it, or replace it with generic architecture.

## Protected Claude / Codex Workstreams

### 1. Any-source engine and upload-first source typing

Protected files/areas:

- `.gitignore`
- `tools/poc/source_matrix_runner.py`
- `tools/poc/test_source_matrix_runner.py`
- `tools/poc/README.md`
- `lwa-backend/app/services/source_ingest.py`
- `lwa-backend/app/api/routes/upload.py`
- `lwa-backend/app/api/routes/generate.py`
- `lwa-backend/app/models/schemas.py`
- `lwa-backend/tests/test_any_source_engine.py`
- `lwa-backend/tests/test_premium_guards.py`
- `lwa-web/lib/types.ts`

Protected behavior:

- Upload acceptance reports `source_type`.
- Upload source classification must remain shared through `source_ingest`.
- Video uploads classify as `video_upload`.
- Audio uploads classify as `audio_upload`.
- Image uploads classify as `image_upload`.
- `/v1/uploads` response includes `source_type`.
- `source_ref` includes `source_type`.
- `/v1/generate` uses the same source classifier.
- POC matrix runner covers upload, prompt, music, campaign, YouTube fallback, Twitch fallback, and unsupported URL fallback lanes.
- POC fixtures/results remain ignored under `poc/`.

Do not remove or rewrite this. Only additive fixes are allowed unless tests prove a defect.

### 2. POC source matrix tooling

Protected behavior:

- Runner command:

```bash
python3 tools/poc/source_matrix_runner.py --base-url http://127.0.0.1:8000
```

- Optional flags:

```bash
--youtube-url
--twitch-url
--unsupported-url
--client-id
```

- Tool must continue checking:
  - `/health`
  - `/v1/uploads`
  - `/v1/generate`
  - upload media URLs
  - strategy-only package paths
  - public URL fallback safety
  - raw extractor error leakage

### 3. LWA Worlds frontend shell

Protected files/areas:

- `lwa-web/lib/worlds/types.ts`
- `lwa-web/lib/worlds/mock-data.ts`
- `lwa-web/lib/worlds/copy.ts`
- `lwa-web/lib/worlds/utils.ts`
- `lwa-web/components/worlds/*`
- `lwa-web/app/command-center/page.tsx`
- `lwa-web/app/marketplace/**`
- `lwa-web/app/ugc/**`
- `lwa-web/app/worlds/**`
- `lwa-web/app/earnings/page.tsx`
- `lwa-web/app/economy/page.tsx`
- `lwa-web/app/integrations/page.tsx`
- `lwa-web/app/admin/marketplace/page.tsx`

Protected behavior:

- Command Center routes through App Router.
- Worlds pages are additive and do not replace existing generation flow.
- Command Center links to existing `/generate`.
- Mock data remains available as fallback until backend `/worlds` endpoints are connected.
- Earnings, rights, blockchain, AI, and Polymarket safety copy must remain visible.
- No guaranteed revenue/views/payouts copy.
- No live crypto or payout claims.

### 4. Claude / Seedance branches

Known branches:

- `feat/claude-seedance-platform`
- `feat/claude-seedance-integration`

Known PR:

- PR #6: `[codex] Add Claude routing and simplify premium generation`
  - Current target: `dev`
  - Status observed: open draft
  - Scope includes Claude routing, disabled-safe Seedance adapter, premium generator UI improvements.

Guardrail:

- Do not duplicate Claude/Seedance provider code in a separate path.
- Do not remove disabled-safe behavior.
- Do not claim Seedance is live unless the exact vendor contract and keys are verified.
- If main needs Claude/Seedance, first compare PR #6 against current main/dev and rebase or cherry-pick carefully.

### 5. Open PRs / merge posture observed

Observed PRs:

- PR #25: `web: harden uploaded video rendered output flow`
  - Base: `main`
  - Status observed: open, mergeable.
  - Scope: frontend URL normalization for rendered assets.
  - Safe priority: high, because it prevents false rendered state and broken open/download actions.

- PR #9: `Finish backend health exposure and iOS auto-target contract alignment`
  - Base: `main`
  - Status observed: open draft, not mergeable.
  - Scope includes `lwa-ios`.
  - Guardrail: do not touch or merge until explicitly approved because current founder instruction repeatedly says do not touch `lwa-ios/`.

- PR #6: Claude/Seedance provider work.
  - Base: `dev`.
  - Guardrail: inspect/rebase before any merge to `main`.

## Required Safe Merge Order

1. Merge or resolve PR #25 first if checks are clean.
2. Re-check `main` after PR #25.
3. Bring doctrine/docs branch into PR against `main`.
4. Compare Claude/Seedance PR #6 against updated `main` and `dev` before trying to fuse provider code.
5. Do not merge PR #9 until explicit iOS approval is given.
6. Run full checks after each merge boundary.

## Required Pre-Merge Checks

Backend:

```bash
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend && python3 -m unittest discover -s tests && cd ..
```

POC tooling:

```bash
python3 -m unittest discover -s tools/poc
python3 -m py_compile tools/poc/source_matrix_runner.py tools/poc/test_source_matrix_runner.py
```

Frontend:

```bash
cd lwa-web
npm run type-check
npm run build
cd ..
```

Repo hygiene:

```bash
git diff --check
git status --short
```

Manual proof where sandbox permits:

```bash
python3 tools/poc/source_matrix_runner.py --base-url http://127.0.0.1:8000
```

If localhost HTTP is blocked in sandbox, record that as blocked and run outside sandbox before final merge.

## Absolute Do-Not-Touch Zones Without Explicit Approval

- `lwa-ios/`
- live payout movement
- real crypto transactions
- Polymarket trading/betting flows
- direct TikTok/Instagram posting without platform approval
- frontend env exposure of server secrets
- removal of existing generation/upload/history/campaign/plan/credit behavior

## Next Codex Instruction

Before implementing any new feature, Codex must:

1. read this file
2. read `docs/lwa-worlds-master-council-report.md`
3. inspect current PR/branch state
4. identify overlap with Claude-protected files
5. state whether it will edit protected files
6. if protected files must be edited, explain why and keep changes additive/minimal
7. run the verification matrix above

## Current recommended next action

Prepare the docs/doctrine PR to `main`, but do not merge provider/backend code until PR #25 is merged or explicitly skipped.

Suggested doctrine PR title:

`docs: add LWA Worlds master execution doctrine`

Suggested PR body:

- Adds Master Council Report.
- Adds build queue and fusion guardrails.
- Protects Claude any-source/source-matrix and Worlds frontend shell work.
- Documents safe merge order and verification matrix.
- Does not change runtime code.
