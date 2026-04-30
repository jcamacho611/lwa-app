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
- Never invent playable/download URLs.
- Strategy-only results must be clearly labeled.
- Money-related systems must use integer cents and idempotent webhooks.

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

## Prompt 5 — Director Brain support modules

```text
You are the LWA backend architecture council.

Using LWA_DIRECTOR_BRAIN_V0, create the supporting algorithm modules that make LWA feel like a full creator operating system, not just a clip scorer.

Build or scaffold these modules:

1. platform_signals.py
2. hook_engine.py
3. caption_style_engine.py
4. offer_detector.py
5. quality_gate.py
6. fallback_engine.py
7. creator_profile.py
8. campaign_engine.py
9. learning_loop.py

Rules:
- Preserve existing backend routes.
- Add optional fields only.
- Do not break existing clip generation.
- Do not touch lwa-ios.
- Do not redesign frontend.
- Do not require live social API integrations.
- Do not fake posting.
- Do not invent playable clip URLs.
- Money-related scoring must be called RevenueIntentScore or OfferFitScore, not guaranteed income.
- If rendering fails, return honest strategy-only results.
- Keep all outputs JSON-safe and frontend-friendly.

Each module should include:
- typed input/output models
- pure scoring/helper functions where possible
- deterministic fallback behavior
- unit tests
- comments explaining scoring logic

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant backend tests

Expected output:
1. files created/changed
2. module responsibilities
3. new fields added to clip response
4. tests added
5. verification results
6. commit message
```

## Prompt 6 — Backend checkpoint after algorithm modules

```text
PAUSE AND REPORT.

Do not continue editing.
Do not commit.

Report:
1. current branch
2. git status --short
3. exact files changed
4. whether any lwa-ios files were touched
5. whether any lwa-web files were touched
6. whether existing backend routes were changed
7. tests run
8. test results
9. any errors or skipped tests
10. recommended next backend step

Wait after reporting.
```

## Prompt 7 — Frontend Director Brain display

```text
You are the LWA frontend implementation engineer.

Task:
Update the web frontend so it can display Director Brain output cleanly without breaking the existing generation flow.

Files likely involved:
- lwa-web/components/clip-studio.tsx
- lwa-web/components/HeroClip.tsx
- lwa-web/components/VideoCard.tsx
- lwa-web/lib/types.ts
- lwa-web/lib/api.ts only if necessary

Frontend requirements:
1. Preserve the current source input and generation flow.
2. Preserve existing backend API compatibility.
3. Add support for optional Director Brain fields:
   - algorithm_version
   - recommended_platform
   - recommended_content_type
   - recommended_output_style
   - platform_recommendation_reason
   - render_status
   - strategy_only
   - reason_not_rendered
   - post_rank
   - hook_variants
   - caption_style
   - thumbnail_text
   - cta_suggestion
   - why_this_matters
   - quality_gate_status
   - revenue_intent_score
   - offer_fit_score
4. Clearly separate:
   - rendered clips
   - raw-only clips
   - strategy-only clips
5. Never show strategy-only results as playable clips.
6. Never invent preview/download URLs.
7. Show the best clip first.
8. Show post order.
9. Show why the clip matters.
10. Show copy buttons for hooks, captions, CTA, and package.
11. Keep the app premium, dark, creator-native, and simple.
12. Do not touch backend.
13. Do not touch lwa-ios.
14. Do not build fake direct posting.
15. Do not build a full editor.

Before editing, report:
- git status --short
- exact files you plan to touch
- confirmation that backend/iOS will not be edited

Verification:
- npm run lint if available
- npm run typecheck if available
- npm run build if available

Expected output:
1. files changed
2. fields supported
3. UI behavior added
4. verification results
5. commit message
```

## Prompt 8 — Caption style + quality gate integration

```text
You are the LWA AI/media pipeline engineer.

Task:
Integrate caption style recommendations and quality gate results into the clip generation output without breaking existing generation.

Goals:
1. Add caption style recommendations to each clip.
2. Add quality gate status to each rendered or raw clip.
3. Keep strategy-only results honest.
4. Never mark failed renders as ready.
5. Preserve existing routes and response compatibility.

Fields to support:
- caption_style
- caption_style_reason
- emphasis_words
- suggested_caption_position
- quality_gate_status
- quality_gate_warnings
- render_readiness_score

Quality gate should check:
- playable asset exists
- audio likely exists
- timestamps are valid
- duration is reasonable
- clip is not marked rendered without URL
- strategy-only clips do not pretend to be downloadable

Constraints:
- Do not touch frontend.
- Do not touch lwa-ios.
- Do not change route names.
- Add optional fields only.
- Keep fallback deterministic.

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant backend tests

Expected output:
1. files changed
2. quality gate behavior
3. caption style behavior
4. tests added/updated
5. verification results
6. commit message
```

## Prompt 9 — Campaign mode backend scaffold

```text
You are the LWA product/backend architect.

Task:
Scaffold Campaign Mode for LWA.

Campaign Mode turns one source into a structured posting campaign, not just a list of clips.

Add optional campaign fields to the clip generation response.

Campaign output types:
1. lead_clip
2. trust_clip
3. sales_clip
4. educational_clip
5. controversy_clip
6. retargeting_clip
7. community_clip

Each clip may include:
- campaign_role
- campaign_reason
- funnel_stage
- suggested_post_order
- suggested_platform
- suggested_caption_style
- suggested_cta

Rules:
- Preserve existing generation route compatibility.
- Do not require account system yet.
- Do not require social posting yet.
- Do not claim campaign manager is fully built.
- Do not touch frontend.
- Do not touch lwa-ios.
- Add optional fields only.
- Keep outputs JSON-safe.

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant backend tests

Expected output:
1. files changed
2. campaign fields added
3. tests added
4. verification results
5. commit message
```

Commit message if clean:

`feat: scaffold campaign mode clip roles`

## Prompt 10 — Frontend campaign display

```text
You are the LWA frontend implementation engineer.

Task:
Display Campaign Mode fields in the web frontend without breaking the existing generation flow.

Files likely involved:
- lwa-web/components/clip-studio.tsx
- lwa-web/components/HeroClip.tsx
- lwa-web/components/VideoCard.tsx
- lwa-web/lib/types.ts

Display optional fields:
- campaign_role
- campaign_reason
- funnel_stage
- suggested_post_order
- suggested_platform
- suggested_caption_style
- suggested_cta

UI requirements:
1. Show campaign role badges.
2. Show suggested post order.
3. Show sales/trust/education/lead labels clearly.
4. Keep rendered clips first.
5. Keep strategy-only clips separate.
6. Do not fake direct posting.
7. Do not build a full campaign manager yet.
8. Do not touch backend.
9. Do not touch lwa-ios.

Verification:
- npm run lint if available
- npm run typecheck if available
- npm run build if available

Expected output:
1. files changed
2. campaign fields displayed
3. verification results
4. commit message
```

Commit message if clean:

`feat: display campaign mode clip roles`

## Prompt 11 — Whop / paid access audit

```text
You are the LWA monetization integration engineer.

Task:
Audit the existing Whop / entitlement / plan / credits flow.

Goal:
Determine what is already implemented, what is missing, and what exact minimal changes are needed before selling access through Whop.

Check:
1. frontend billing/plan display
2. backend entitlement checks
3. environment variables
4. checkout URL usage
5. webhook readiness
6. credit/plan enforcement
7. free launch mode behavior
8. guest user fallback behavior

Rules:
- Audit first.
- Do not edit files yet.
- Do not redesign monetization.
- Do not remove FREE_LAUNCH_MODE.
- Do not touch iOS.
- Do not fake completed Whop integration.

Return:
1. what exists now
2. what is missing
3. risks
4. exact files likely involved
5. smallest safe implementation plan
6. verification checklist
```

## Prompt 12 — Whop PR #37 manual merge / verification

```text
PR #37 is open and mergeable:
https://github.com/jcamacho611/lwa-app/pull/37

Task:
Merge PR #37, then verify backend tests and Railway deployment readiness.

Rules:
- Do not add marketplace payouts.
- Do not add seller balances.
- Do not add Stripe Connect money movement.
- Do not touch lwa-ios.
- Do not touch frontend unless fixing a verified backend contract issue.

After merge, verify:
- signed Whop webhook route exists
- idempotent event storage exists
- user plan updates only from signed event
- invalid signature returns failure
- replayed event is idempotent

Run:
python3 -m compileall lwa-backend/app
cd lwa-backend && python3 -m unittest discover -s tests

Expected output:
1. merge commit
2. tests run
3. verification results
4. Railway env settings needed
```

## Prompt 13 — Public launch hardening

```text
You are the LWA launch hardening engineer.

Task:
Prepare the app for public free launch without breaking current generation.

Must include:
1. FREE_LAUNCH_MODE safety
2. guest user fallback
3. abuse-prevention IP rate limit
4. deterministic fallback clip result
5. no frontend 500 crashes
6. clean error messages
7. README launch instructions
8. Railway env var checklist

Rules:
- Preserve existing routes.
- Preserve working generation flow.
- Do not touch iOS unless explicitly required.
- Do not add heavy new systems.
- Do not block public demo usage with incomplete paywall logic.
- Fallback must be honest and never invent rendered clips.

Verification:
- backend py_compile
- backend pytest
- frontend lint/typecheck/build if frontend touched
- one manual generation test
- one failure/fallback test

Expected output:
1. files changed
2. launch hardening added
3. fallback behavior
4. env vars needed
5. verification results
6. commit message
```

Commit message if clean:

`chore: harden public launch flow`

## Prompt 14 — Algorithm database foundation

Use when moving from docs to the actual database foundation. Adapt to the current repo store first; do not force Postgres migration if the repo is still using SQLite.

```text
You are the LWA backend systems architect.

Task:
Build the first production-safe version of the LWA algorithm and database foundation.

Implement or scaffold these systems:

1. source validation
2. source metadata storage
3. generation job tracking
4. transcript segment storage
5. segment signal scoring
6. moment candidate detection
7. Director Brain scoring
8. platform fit scoring
9. offer / money moment scoring
10. hook packaging
11. caption style metadata
12. quality gate
13. clip result storage
14. clip asset storage
15. campaign mode scaffold
16. user learning events
17. usage ledger
18. webhook idempotency table
19. operator dashboard queries

Rules:
- Preserve existing backend routes.
- Add optional fields only.
- Do not break current clip generation.
- Do not touch lwa-web unless explicitly required.
- Do not touch lwa-ios.
- Do not fake direct social posting.
- Do not fake playable asset URLs.
- Strategy-only clips must be clearly marked.
- Rendered clips must have a playable or downloadable asset URL.
- Money must use integer cents only.
- Webhook processing must be idempotent.
- Keep all outputs JSON-safe.
- Add database migrations if the repo has migrations.
- If the repo does not have migrations, create SQL files under docs or backend database setup according to existing repo structure.

Required database objects:
- source_assets
- generation_jobs
- transcript_segments
- segment_signals
- moment_candidates
- algorithm_scores
- platform_fit_scores
- offer_detection_scores
- clip_packages
- caption_style_results
- quality_gate_results
- clip_results
- clip_assets
- campaigns
- campaign_items
- user_clip_events
- usage_ledger
- webhook_events

Required backend modules, if structure allows:
- source_validation.py
- source_metadata.py
- transcript_segments.py
- signal_extraction.py
- moment_detection.py
- director_brain.py
- platform_signals.py
- offer_detector.py
- hook_engine.py
- caption_style_engine.py
- quality_gate.py
- clip_results.py
- campaign_engine.py
- learning_loop.py
- usage_ledger.py
- webhook_idempotency.py

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant backend tests
- verify migrations or SQL are syntactically valid
- confirm no lwa-ios files changed
- confirm no frontend files changed unless explicitly necessary

Expected output:
1. exact files changed
2. tables/migrations added
3. modules added
4. algorithm functions added
5. tests added
6. verification results
7. risks or follow-up work
8. commit message
```

## Prompt 15 — Marketplace audit

Role: full-stack engineer and marketplace operator.

Task: audit persistence/routes for marketplace compatibility. Docs first, no live payments.

Verification:

```bash
git diff --check
```

Commit message:

`docs: add marketplace compatibility audit`

## Prompt 16 — Realms static shell

Role: full-stack engineer and game systems designer.

Task: add static Signal Realms shell using existing app structure.

Constraints:

- no purchasable XP
- no feature unlocks from relics
- no chain dependency

Commit message:

`feat: add Signal Realms static shell`

## Prompt 17 — Social status shell

Role: backend/frontend engineer.

Task: add provider status shell before real OAuth actions.

Constraints:

- no posting until provider approval
- no token storage without encryption

Commit message:

`feat: add social integration status shell`

## Prompt 18 — Off-chain provenance dry run

Role: backend engineer.

Task: add deterministic off-chain provenance records and JSON export.

Constraints:

- no mainnet
- no wallet requirement
- no app feature unlocks

Commit message:

`backend: add off-chain provenance dry run`
