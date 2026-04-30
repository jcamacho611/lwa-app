# LWA Codex Chunk 15 — Master Repo Fusion Prompt

## Purpose

This prompt exists so Codex can continue the LWA / IWA build safely without restarting, duplicating architecture, or building future-phase systems before the core clipping product is hardened.

This is the official continuation direction:

- Preserve the existing repo.
- Build additively.
- Treat `jcamacho611/lwa-app` as the source of truth.
- Verify the real repo paths before editing.
- Fuse the Master Council Report and prior chunk work into `docs/company/`.
- Separate shipped / in-progress / planned / unknown.
- Select one safe P0 implementation slice next.

---

## Paste This Into Codex

```text
You are working inside the existing GitHub repo:

Repository: jcamacho611/lwa-app
Default branch: main

You are executing Chunk 15 — LWA Master Repo Fusion.

This is NOT a restart.
This is NOT a rebuild.
This is NOT a generic redesign.
This is NOT permission to paste giant unrelated code into the repo.

The existing repo is the source of truth.

Your job is to fuse the uploaded LWA master planning files, prior chunk work, current thread intelligence, and current repo reality into the repo safely, then identify the next safest implementation slice.

================================================================================
PRIMARY MISSION
================================================================================

Turn the existing LWA / IWA app into a real revenue-generating AI clipping product.

The product direction is:

- AI content repurposing platform
- video-to-viral short-form workflow
- creator / clipper operating system
- ranked clip packs with hooks, captions, timestamps, scores, and assets
- premium creator workspace
- future marketplace
- future Signal Realms RPG progression
- future social integrations
- future cosmetic/provenance blockchain layer

Primary promise:

Drop in one long-form source and get ranked short-form outputs with hooks, captions, timestamps, scores, and workflow-ready assets.

Operational promise:

Move from generation to queue to campaigns to payout-readiness inside one premium workspace.

================================================================================
ABSOLUTE RULES
================================================================================

DO NOT:
- restart the repo
- create a new app from scratch
- create parallel apps/backend or apps/web folders if the real repo uses lwa-backend/lwa-web
- overwrite working routes
- delete existing implementation
- touch lwa-ios unless a task explicitly says iOS audit only
- add live Stripe payouts before the marketplace/payment safety layer is ready
- add blockchain/mainnet contracts
- add NFT purchases
- add crypto trading
- add Polymarket betting/trading
- claim guaranteed virality
- claim guaranteed income
- claim payment verified unless a verified webhook actually exists
- unlock paid access from client-submitted events
- expose raw tokens, cookies, API keys, stack traces, yt-dlp internals, or bot-check errors
- build marketplace, Realms, social APIs, blockchain, and frontend redesign all in one PR

ALWAYS:
- preserve existing code by default
- prefer additive edits
- audit before editing
- adapt to the actual repo structure
- protect /health, /v1/generate, /v1/jobs, uploads, entitlements, revenue events, generated assets
- run tests before committing
- commit only isolated clean slices
- report exact files changed
- separate actual metrics from assumptions
- mark docs/plans clearly when not implemented yet

================================================================================
FIRST REQUIRED ACTION — AUDIT BEFORE EDITING
================================================================================

Before making code changes, run and report:

pwd
git rev-parse --abbrev-ref HEAD
git rev-parse --short=7 HEAD
git status --short
find . -maxdepth 3 -type f | sort | sed -n '1,500p'

Then inspect:

- README.md
- docs/
- docs/company/
- lwa-backend/
- lwa-web/
- tools/poc/
- package files
- backend app entrypoint
- backend route registration
- backend schema/config files
- backend tests
- frontend app routes
- frontend lib/types
- frontend components
- source matrix runner
- revenue event route/logger if present

Search:

rg -n "FREE_LAUNCH_MODE|NEXT_PUBLIC_FREE_LAUNCH_MODE|source_type|source_matrix|revenue/events|RevenueEvent|Director Brain|director_brain|marketplace|realm|Realms|Polymarket|Stripe|Whop|webhook|entitlement|quota|fallback|yt-dlp|cookies|bot-check|unsupported" .

Return an audit summary BEFORE editing:

1. actual repo structure
2. backend path
3. frontend path
4. whether apps/backend or apps/web exists
5. actual backend framework style
6. actual test runner style
7. existing source handling files
8. existing revenue tracking files
9. existing docs/company files
10. existing marketplace/realm/social/blockchain files if any
11. dirty files before work
12. safest next slice

================================================================================
SECOND REQUIRED ACTION — FUSE MASTER DOCS INTO REPO
================================================================================

Create or update a clean documentation system under:

docs/company/

Add/update these docs:

1. docs/company/lwa-source-of-truth.md
2. docs/company/lwa-master-council-report.md
3. docs/company/lwa-execution-roadmap.md
4. docs/company/lwa-implementation-status.md
5. docs/company/lwa-architecture-compatibility-map.md
6. docs/company/lwa-codex-prompt-stack.md
7. docs/company/lwa-claim-safety-rules.md
8. docs/company/lwa-revenue-and-monetization-plan.md
9. docs/company/lwa-marketplace-future-plan.md
10. docs/company/lwa-realms-future-plan.md
11. docs/company/lwa-social-api-future-plan.md
12. docs/company/lwa-blockchain-proof-future-plan.md
13. docs/company/lwa-next-safe-slice.md

These docs must:

- preserve the master vision
- clearly label implemented vs planned
- adapt paths to the real repo structure
- avoid false claims
- avoid guaranteed income/virality
- state public URLs are best-effort
- state revenue events are non-authoritative unless verified webhooks exist
- state marketplace/payouts/blockchain are future phases unless already implemented
- state cosmetic blockchain features must not unlock app functionality

================================================================================
THIRD REQUIRED ACTION — CREATE IMPLEMENTATION STATUS MAP
================================================================================

Create/update:

docs/company/lwa-implementation-status.md

It must include:

| Area | Status | Evidence in repo | Safe next step |
|---|---|---|---|
| Core generation | | | |
| Upload/source handling | | | |
| Public URL support | | | |
| Source POC Matrix | | | |
| Revenue intent tracking | | | |
| FREE_LAUNCH_MODE | | | |
| Fallback hardening | | | |
| Director Brain | | | |
| Caption presets | | | |
| Marketplace | | | |
| Realms/RPG | | | |
| Social APIs | | | |
| Blockchain/proof | | | |
| iOS/mobile | | | |
| Investor/data room | | | |
| Frontend premium UI | | | |
| Railway deployment | | | |

Use only repo evidence.
If unknown, say unknown.
If planned, say planned.
Do not pretend planned systems are shipped.

================================================================================
FOURTH REQUIRED ACTION — SELECT ONLY ONE NEXT SAFE CODE SLICE
================================================================================

After docs/status are fused, implement ONLY the safest next code slice if compatible.

Choose from this order:

P0 Slice A — Source handling hardening
Use if source_type/upload/public URL behavior is not fully consistent.

Implement:
- central allowed format map
- stable source_type contract
- clean unsupported-file errors
- clean public URL blocked fallback
- no raw yt-dlp/cookies/bot-check leaks
- frontend upload accept list if safe
- tests
- keep Source POC runner working

Stable source_type values:
- video_upload
- audio_upload
- image_upload
- prompt
- music
- campaign
- url

P0 Slice B — FREE_LAUNCH_MODE
Use if free launch mode is missing or incomplete.

Implement:
- backend FREE_LAUNCH_MODE config
- guest/free launch user behavior if compatible with existing auth
- IP abuse cap if existing rate-limit pattern supports it
- frontend NEXT_PUBLIC_FREE_LAUNCH_MODE banner
- no forced payment/Whop during free launch
- tests/docs

P0 Slice C — Fallback hardening
Use if pipeline still returns 500s on provider/source failures.

Implement:
- deterministic fallback helpers
- clean failure responses
- status/status_reason fields if compatible
- no pipeline full rewrite unless existing code is already broken
- tests for bad URL/provider failure returning usable degraded result

P0 Slice D — README polish
Use if A-C are mostly complete.

Implement:
- update README.md with real repo paths
- live URLs
- local dev
- env vars
- API examples
- deploy notes
- claim safety

IMPORTANT:
Only implement one P0 slice in this run unless changes are docs-only.
Do not start marketplace, Realms, Polymarket, blockchain, or Stripe payments in this run.

================================================================================
PROTECTED FLOWS
================================================================================

Do not break:

- /health or /healthz if present
- /v1/generate
- /v1/jobs
- /v1/uploads
- source matrix runner
- entitlements/quota
- revenue event tracking
- generated asset retention
- frontend type-check
- existing routes
- Railway compatibility

================================================================================
REVENUE EVENT RULES
================================================================================

If revenue event tracking exists:

- preserve it
- do not change schema unless necessary
- do not unlock access from it
- keep authoritative=false
- keep logs optional and nonfatal
- keep metadata sanitized
- keep no secrets logged

If it does not exist:

Do NOT implement it in this run unless selected as the one safe code slice.

================================================================================
MARKETPLACE / REALMS / SOCIAL / BLOCKCHAIN RULES
================================================================================

These are future-phase unless repo evidence proves otherwise.

Allowed now:
- docs
- future plan
- compatibility map
- safety rules

Not allowed now:
- live payouts
- Stripe transfers
- Whop seller payouts
- NFT purchases
- token economics
- chain writes
- social posting
- Polymarket betting/trading

================================================================================
VERIFICATION REQUIRED
================================================================================

Run the verification that matches the actual repo.

Likely commands:

python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend && python3 -m unittest discover -s tests
cd ../lwa-web && npm run type-check
cd ..
git diff --check
git status --short

If npm lint exists and is stable:
cd lwa-web && npm run lint

If tools/poc exists:
python3 -m unittest discover -s tools/poc
python3 tools/poc/source_matrix_runner.py --help

If local HTTP sandbox blocks live POC execution, report it as blocked, not failed.

Do not fake test results.

================================================================================
COMMIT RULE
================================================================================

Commit only if:

- changes are isolated
- no unrelated dirty files
- tests pass
- no iOS files touched
- no secrets
- no generated media/results committed unless intended docs
- git diff --check passes

Commit message:

docs: fuse LWA master execution system

or, if code slice included:

backend: harden source handling for upload-first generation

or:

feat: add free launch mode guardrails

or:

backend: add deterministic fallback hardening

================================================================================
FINAL REPORT FORMAT
================================================================================

Return exactly:

# LWA MASTER REPO FUSION REPORT

## 1. Reality Check
- Branch:
- Starting commit:
- Dirty files before work:
- Actual backend path:
- Actual frontend path:
- Actual route structure:
- Actual test style:

## 2. Source Documents Fused
- Docs created:
- Docs updated:
- Planning assumptions corrected:
- Paths corrected from master docs:

## 3. Implementation Status Map
- Core generation:
- Upload/source handling:
- Public URL support:
- Source POC Matrix:
- Revenue intent tracking:
- FREE_LAUNCH_MODE:
- Fallback hardening:
- Director Brain:
- Marketplace:
- Realms:
- Social APIs:
- Blockchain:
- iOS/mobile:
- Investor docs:

## 4. Code Slice Selected
- Selected slice:
- Why this was the safest next step:
- Slices intentionally skipped:

## 5. Files Inspected
- ...

## 6. Files Changed
- ...

## 7. What Was Implemented
- ...

## 8. What Was Preserved
- /health:
- /v1/generate:
- /v1/jobs:
- uploads:
- entitlements:
- revenue events:
- generated assets:
- frontend:
- iOS:

## 9. Tests / Verification
- backend compileall:
- backend tests:
- frontend type-check:
- tools/poc tests:
- source matrix runner:
- git diff --check:
- git status:

## 10. Claim Safety
- Safe customer-facing claim:
- Claims not allowed yet:

## 11. Remaining Gaps
- P0:
- P1:
- P2:

## 12. Next Prompt
Give the exact next Codex prompt for the next safest slice.

## 13. Commit
- Commit made:
- Commit hash:
- Commit message:

================================================================================
EXECUTE NOW
================================================================================

Start with audit.
Fuse the docs.
Create/update the implementation status map.
Then implement only one safest P0 code slice if clean and compatible.
Run verification.
Commit if clean.
```

---

## Direction Confirmation

This prompt keeps LWA moving exactly toward the requested direction:

1. real AI clipping product first
2. revenue foundation second
3. marketplace third
4. Realms/RPG retention layer after core product stability
5. social APIs only after safety/OAuth approval
6. blockchain only as cosmetic/provenance after off-chain proof
7. no restarts, no duplicate architecture, no fake shipped claims

## Next Human Action

Open this file in GitHub or copy the prompt above into Codex.

After Codex finishes, paste the final report back into ChatGPT and ask for Chunk 16.
