# LWA Worlds — Codex Prompt Pack

## Purpose

This artifact gives Justin exact Codex prompts to run one task at a time.

## Global Codex Rules

- Preserve existing backend routes unless a defect is proven.
- Do not touch `lwa-ios` unless explicitly instructed.
- Do not redesign the whole app at once.
- Use additive edits by default.
- Every backend prompt must include compile/test verification.
- Every frontend prompt must include type-check/build verification.
- Do not create fake features.
- Do not break the working generation flow.
- Adapt `apps/backend` and `apps/web` examples to actual paths: `lwa-backend` and `lwa-web`.

## Prompt 1 — Source Handling Hardening

Role: senior backend engineer.

Task: harden upload/source behavior without changing the generation product contract.

Files likely involved:

- `lwa-backend/app/services/source_contract.py`
- `lwa-backend/app/services/source_ingest.py`
- `lwa-backend/app/api/routes/upload.py`
- `lwa-backend/app/api/routes/generate.py`
- `lwa-backend/app/models/schemas.py`
- `lwa-backend/tests/`

Constraints:

- keep `/v1/generate`, `/v1/jobs`, and `/v1/uploads` working
- do not expose raw extractor/provider errors
- keep public URLs best-effort
- keep source matrix tooling passing

Verification:

```bash
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend && python3 -m unittest discover -s tests
```

Commit message:

`backend: harden source handling contract`

## Prompt 2 — Free Launch Mode

Role: backend/frontend engineer.

Task: add production-safe free launch mode.

Files likely involved:

- `lwa-backend/app/core/config.py`
- `lwa-backend/app/dependencies/auth.py`
- `lwa-backend/app/services/entitlements.py`
- `lwa-backend/app/api/routes/generate.py`
- `lwa-web/app/layout.tsx`
- `lwa-web/components/FreeLaunchBanner.tsx`

Constraints:

- no full auth rewrite
- no permanent paywall removal
- no iOS work
- backend flag: `FREE_LAUNCH_MODE`
- frontend flag: `NEXT_PUBLIC_FREE_LAUNCH_MODE`

Verification:

```bash
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend && python3 -m unittest discover -s tests
cd ../lwa-web && npm run type-check && npm run build
```

Commit message:

`feat: add free launch mode guardrails`

## Prompt 3 — Fallback Hardening

Role: AI/media pipeline engineer.

Task: wire deterministic fallback helpers into generation/pipeline failure paths.

Files likely involved:

- `lwa-backend/app/services/fallbacks.py`
- `lwa-backend/app/services/clip_service.py`
- `lwa-backend/app/services/video_service.py`
- `lwa-backend/app/api/routes/generate.py`
- `lwa-backend/tests/`

Constraints:

- degraded output beats a crash
- no raw stack traces to customers
- release quota on true failure
- preserve existing response shape as much as possible

Verification:

```bash
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend && python3 -m unittest discover -s tests
```

Commit message:

`backend: add deterministic degraded fallbacks`

## Prompt 4 — Director Brain v0

Role: AI/media pipeline engineer.

Task: connect Director Brain v0 to the existing generation output.

Files likely involved:

- `lwa-backend/app/services/director_brain.py`
- `lwa-backend/app/services/hook_formula_library.py`
- `lwa-backend/app/services/caption_presets.py`
- `lwa-backend/app/services/clip_service.py`
- `lwa-backend/tests/`

Constraints:

- do not duplicate Claude/OpenAI providers if existing
- keep provider failures safe
- preserve existing generation route

Verification:

```bash
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend && python3 -m unittest discover -s tests
```

Commit message:

`backend: add Director Brain v0 packaging`

## Prompt 5 — Frontend Command Center

Role: frontend engineer and UI designer.

Task: polish the current generate experience into a premium clipping command center.

Files likely involved:

- `lwa-web/components/clip-studio.tsx`
- `lwa-web/components/HeroClip.tsx`
- `lwa-web/components/VideoCard.tsx`
- `lwa-web/lib/types.ts`
- `lwa-web/lib/api.ts`

Constraints:

- rendered proof first
- strategy-only results clearly labeled
- do not fake editor features
- preserve working API contract

Verification:

```bash
cd lwa-web && npm run type-check && npm run build
```

Commit message:

`web: polish clipping command center`

## Prompt 6 — Marketplace Audit

Role: full-stack engineer and marketplace operator.

Task: audit persistence/routes for marketplace compatibility. Docs first, no live payments.

Verification:

```bash
git diff --check
```

Commit message:

`docs: add marketplace compatibility audit`

## Prompt 7 — Realms Static Shell

Role: full-stack engineer and game systems designer.

Task: add static Signal Realms shell using existing app structure.

Constraints:

- no purchasable XP
- no feature unlocks from relics
- no chain dependency

Commit message:

`feat: add Signal Realms static shell`

## Prompt 8 — Social Status Shell

Role: backend/frontend engineer.

Task: add provider status shell before real OAuth actions.

Constraints:

- no posting until provider approval
- no token storage without encryption

Commit message:

`feat: add social integration status shell`

## Prompt 9 — Off-Chain Provenance Dry Run

Role: backend engineer.

Task: add deterministic off-chain provenance records and JSON export.

Constraints:

- no mainnet
- no wallet requirement
- no app feature unlocks

Commit message:

`backend: add off-chain provenance dry run`
