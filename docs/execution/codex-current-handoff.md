# Codex Current Handoff — LWA Worlds

Updated: 2026-04-30

## Purpose

This is the single handoff file for Codex to pick up work already completed across this thread and parallel workstreams. Do not restart or duplicate existing systems. Continue from current `main`.

## Current repo truth

- Repository: `jcamacho611/lwa-app`
- Main branch is canonical.
- Open PRs were last checked as `0` in the command-center workflow.
- Production frontend: `https://lwa-the-god-app-production.up.railway.app`
- Production backend: `https://lwa-backend-production-c9cc.up.railway.app`

## Active command center

- Issue #49 — LWA Worlds all-phases command center
- Issue #51 — Phase 1 launch hardening execution
- Issue #52 — Phase 2 Director Brain execution
- Issue #53 — Phase 3 marketplace MVP execution
- Issue #54 — Phase 4 Signal Realms execution
- Issue #56 — Phase 5 social integrations execution
- Issue #57 — Phase 6 proof and blockchain execution
- Issue #58 — Phase 7 hiring and council operations execution
- Issue #59 — Phase 8 sales and investor execution
- Issue #60 — Phase 9 operator dashboard execution
- Issue #61 — Phase 10 creative system and prototype execution

## Already-created repo docs

Read these before coding:

```text
docs/execution/connected-app-command-center-index.md
docs/execution/context-and-memory-export.md
docs/execution/phase-1-launch-hardening-proof.md
docs/execution/phase-2-director-brain-evaluation.md
docs/lwa-worlds/chunk-4-sql-repository-layer.md
docs/lwa-worlds/chunk-5-frontend-display-logic.md
docs/lwa-worlds/chunk-6-campaign-social-algorithms.md
docs/lwa-worlds/chunk-7-marketplace-realms-proof.md
docs/lwa-worlds/chunk-8-editor-ios-rebuild.md
docs/lwa-worlds/chunk-9-execution-order.md
```

## Connected-app work already done

Google Drive:
- `LWA Worlds — All Phases Command Center`
- `LWA Worlds — Supreme Council Phase Tracker`
- `Justin Camacho / LWA — Context and Memory Export`
- `Justin Camacho / LWA — Structured Context Export`

Gmail:
- Labels: `LWA/Investors`, `LWA/Sales`, `LWA/Council Hiring`
- Drafts: investor intro, sales demo outreach, founding council role outreach

Canva:
- Folder: `LWA Worlds Command Center`
- Editable design: `LWA Worlds All-Phases Launch`

Figma:
- `LWA Worlds All Phases Roadmap` visual/architecture flow

Lovable:
- Prototype: `LWA Worlds Supreme Council Command Center`
- Project ID: `a8096d7a-3c35-4c31-b42a-bd97fea08cfc`
- URL: `https://lovable.dev/projects/a8096d7a-3c35-4c31-b42a-bd97fea08cfc`
- Status recorded as ready

Vercel/domain findings:
- available at lookup time: `lwaworlds.com`, `lifewithai.app`, `lwaapp.com`, `iwaapp.com`, `iwacreator.com`, `lwacreator.com`, `thesignalrealms.com`, `directorbrain.ai`
- priority: `lwaworlds.com`, `lifewithai.app`, `lwaapp.com`, `thesignalrealms.com`, then `directorbrain.ai`

## What is already implemented or documented

Phase 1:
- `FREE_LAUNCH_MODE` / launch proof runbook exists.
- backend config and frontend banner evidence are documented.
- quality gate evidence is documented.
- Next action is verification, not rewrite.

Phase 2:
- Director Brain service/tests already exist.
- evaluation runbook exists with minimum eval matrix.
- Next action is evaluation-driven enhancement, not replacement.

All phases:
- command-center issues exist.
- phase tracker exists in Drive.
- connected-app index exists in repo.

## Supreme Council operating rule

Every task must have:

```text
1. Lead council
2. Supporting councils
3. Proof standard
4. Connected-app channel
5. GitHub or Drive record
```

## Hard constraints

- Do not restart the project.
- Do not duplicate docs, modules, PRs, or branches unnecessarily.
- Do not touch iOS unless the task is a dedicated iOS branch.
- Do not fake upload completion.
- Do not fake direct social posting.
- Do not fake marketplace checkout.
- Do not fake payouts.
- Do not fake analytics.
- Do not fake playable asset URLs.
- Do not fake blockchain publishing.
- Strategy-only clips must never appear as rendered/playable.
- Rendered clips require actual playable/downloadable assets.
- Money uses integer cents only.
- Webhooks must be idempotent.
- XP cannot be bought.
- Badges are earned.
- Relics are cosmetic only.
- Proof/blockchain is optional provenance only, not investment framing.

## Recommended next Codex task

Start with Phase 1 verification and Phase 2 evaluation before building new runtime features.

### Task A — Phase 1 verification PR

Read:
- `docs/execution/phase-1-launch-hardening-proof.md`
- backend config/settings
- generate route
- source contract service
- quality gate service
- frontend `FreeLaunchBanner`
- frontend clip display utilities

Do:
- Run available backend/frontend checks.
- Add missing tests only where they verify existing behavior.
- Update docs only if env names/live URLs are stale.
- Post verification results to issue #51.

Do not:
- add marketplace runtime
- add social posting
- add editor
- add blockchain
- change iOS

### Task B — Phase 2 Director Brain eval PR

Read:
- `docs/execution/phase-2-director-brain-evaluation.md`
- Director Brain service/tests
- frontend Director Brain display components

Do:
- Add/extend eval tests from the runbook.
- Preserve existing response compatibility.
- Keep optional fields safe in frontend.
- Confirm strategy-only display never shows fake video.
- Post verification results to issue #52.

Do not:
- replace the generation flow
- collapse per-platform logic into one score
- add unapproved providers

## Verification commands

Run what exists in the actual repo layout and record skipped commands with reasons.

Backend:

```text
cd lwa-backend
python -m py_compile $(git ls-files '*.py')
pytest -x
```

Frontend:

```text
cd lwa-web
npm run type-check
npm run lint
npm run build
```

If a command is unavailable, record:

```text
SKIPPED: command unavailable in package scripts
```

## Expected Codex output

Return:

```text
1. Files inspected
2. Files changed
3. Tests/checks run
4. Tests/checks skipped with reason
5. Verification result
6. Risks
7. Follow-up issues/PRs
8. Commit message
```

## Current best first move

Create a small PR that only performs Phase 1 verification/test/doc completion, then a second PR for Phase 2 evaluation tests. Do not bundle marketplace, Realms, social posting, proof/blockchain, editor, or iOS into those PRs.
