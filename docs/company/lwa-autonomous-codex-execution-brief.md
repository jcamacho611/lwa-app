# LWA Autonomous Codex Execution Brief

## Status

This is the consolidated execution brief for the next time Codex is available.

It combines:

- ChatGPT doctrine
- Claude doctrine/spec/code requirements
- Codex execution ledger
- LWA Worlds direction
- source/revenue/CTA/backend intelligence work already reported
- latest multi-source doctrine intake from uploaded ChatGPT/Claude/Codex files
- the instruction to integrate provided Claude code only after repo reconciliation proves exactly where it fits

This document exists so Codex can work autonomously without losing context.

## Absolute Mission

Build LWA into the full LWA Worlds platform:

**AI clipping engine + any-source generation + marketplace + UGC + RPG/world progression + internal economy ledger + social intelligence + admin/moderation + future proof/chain layer.**

The current clipping engine is the foundation. Do not replace it. Extend it.

## Mandatory Source Documents

Before coding, Codex must read:

1. `docs/lwa-worlds-mandatory-doctrine.md`
2. `docs/company/lwa-codex-execution-ledger.md`
3. `docs/company/lwa-autonomous-codex-execution-brief.md`
4. `docs/company/lwa-multi-source-doctrine-intake.md`
5. `docs/lwa-worlds-integrated-architecture.md` if present
6. `docs/lwa-ios-app-store-mobile-readiness-bridge.md` if present
7. Any Claude doctrine/spec/code file added under `docs/company/`, `docs/`, or attached by the operator

## Execution Philosophy

Codex should be aggressive and autonomous in execution, but not destructive.

Execution-first means:

- inspect the repo
- identify missing parts
- implement the next highest-value slice
- add tests
- run verification
- commit cleanly
- report exact changes
- continue to the next slice when safe

Execution-first does **not** mean:

- deleting working systems
- overwriting the clipping engine
- inventing fake finished features
- shipping payment unlocks without verification
- creating illegal earnings/investment claims
- touching iOS without an iOS task
- pasting code that imports modules that do not exist

## Non-Negotiable Integration Rule For Claude Code

If the operator provides Claude code/specs, Codex must not discard them.

Codex must:

1. Preserve the Claude code/spec in repo docs or source files.
2. Inspect every referenced import/path/module.
3. Adapt the code to the actual LWA repo structure.
4. Integrate the code fully where it belongs if it compiles and matches the architecture.
5. If direct paste would break the app, create the missing supporting module or adapt the imports.
6. If a feature depends on unavailable secrets, external accounts, legal review, Apple review, or payment-provider setup, scaffold it behind disabled-by-default feature flags.
7. Write an integration report explaining what was used, what was adapted, what remains blocked, and why.

Do not ignore Claude code. Do not blindly paste Claude code if it breaks imports. Adapt and install it correctly.

## Current Reported Codex Work To Reconcile

From `docs/company/lwa-codex-execution-ledger.md`, Codex must verify whether these are installed on the working branch:

1. Backend revenue event tracking foundation
   - reported commit `80a2970`
   - `POST /v1/revenue/events`
   - JSONL revenue intent logger
   - `authoritative=false`
   - metadata sanitization
   - quota-blocked hook

2. Web multi-destination money CTA system
   - reported local commit `0be4645`
   - pushed matching commit found as `05567ea1e7050dd3bd7f4214c3decd080500cd3a`
   - centralized money links
   - `MoneyCtaPanel`
   - `/offers`
   - frontend `/api/revenue-events`

3. Backend clip intelligence and entitlement hardening
   - reported commit `4b2e17f`
   - safer clip limits
   - packaging profiles
   - provider/intelligence provenance
   - Attention Compiler helpers
   - route contract tests

4. Any-source source-engine realignment
   - reported commit `2c95f7e`
   - source material / prompts / files / campaigns / ideas / objectives through `/generate`

5. Company ops / recruitment docs
   - elite recruitment system
   - creator tester program
   - sales closer program
   - advisor/partner/investor system
   - support-the-build MVO
   - outreach scripts
   - intake forms
   - 7-day execution plan

## First Autonomous Task

The first task is not to build a random new feature.

The first task is:

**Repo Reconciliation Audit + Missing Slice Installation Plan**

Codex must inspect the actual current branch and mark each reported slice as:

- installed
- missing
- partially installed
- conflicting
- needs tests
- safe next repair

Only after the audit may Codex begin installing missing pieces.

## Required Audit Commands

Run from repo root:

```bash
pwd
git rev-parse --abbrev-ref HEAD
git rev-parse --short=7 HEAD
git status --short
find docs -maxdepth 4 -type f | sort | sed -n '1,300p'
find lwa-backend -maxdepth 5 -type f | sort | sed -n '1,520p'
find lwa-web -maxdepth 5 -type f | sort | sed -n '1,520p'
```

Search:

```bash
rg -n "revenue_events|RevenueEvent|revenue_event_log|authoritative|MoneyCtaPanel|money-links|/offers|packaging_profiles|ProviderProvenance|IntelligenceProvenance|source_type|source_formats|any-source|campaign_goal|worlds|ledger|marketplace|ugc|relic|quest|wallet|payout|moderation|fraud" docs lwa-backend lwa-web || true
```

## Required Reconciliation Report

Before coding, Codex must output:

1. branch
2. commit
3. dirty files
4. doctrine files found
5. ledger files found
6. multi-source intake files found
7. Claude files found
8. installed Codex slices
9. missing Codex slices
10. partially installed slices
11. conflicts
12. files Codex plans to touch
13. files Codex will not touch
14. tests Codex will run
15. commit plan

## Installation Priority

After audit, install missing pieces in this order:

### P0 — Preserve and stabilize current app

- routes separated correctly
- `/generate` working
- `/dashboard` not fake if existing workspace exists
- source upload/source-type handling working
- public URLs best-effort with clean fallback
- backend tests passing
- frontend type-check passing

### P1 — Install Codex-reported foundations if missing

- backend revenue event tracking
- frontend multi-destination CTA system
- backend clip intelligence hardening
- any-source source engine
- company ops docs

### P2 — Frontend rebuild

- source-first console
- auto destination recommendation
- rendered proof first
- strategy-only lane secondary
- lead clip card
- packaging/export rail
- mobile-safe containment

### P3 — Marketplace skeleton + internal economy placeholders + RPG profile shell

Implement as a vertical slice:

- frontend pages/shells
- backend routes/models if they fit existing persistence
- internal ledger placeholders
- marketplace campaign/job/submission/review states
- pending/approved/held/disputed/refunded payout states
- RPG profile/class/faction/XP/badge/relic shell
- admin/moderation overview

No real payouts yet. No real crypto yet. No token yet.

### P4 — UGC foundation

- UGC asset/template/quest submissions
- review/moderation statuses
- ownership/rights declaration
- reporting/takedown hooks
- seller-safe language

### P5 — Social integration scaffold

- YouTube
- TikTok
- Instagram
- Twitch
- Polymarket trend-only
- OpenAI
- Anthropic Claude
- Seedance / BytePlus ModelArk
- Apple App Store Connect
- Whop
- Stripe later

All clients must be isolated. No hardcoded secrets.

### P6 — iOS/mobile readiness bridge

Only after mobile/backend compatibility audit:

- `/worlds/mobile/me`
- `/worlds/mobile/dashboard`
- `/worlds/mobile/launch-safety`
- `/worlds/mobile/feature-flags`

Do not touch `lwa-ios/` unless explicitly assigned.

## Feature Flag Rule

Any unfinished or external-dependent feature must be behind a disabled-by-default flag.

Examples:

- real payouts
- external checkout in iOS
- marketplace public posting
- UGC public selling
- wallet connection
- chain proof
- Polymarket integration
- social posting
- Apple IAP
- Seedance rendering
- Anthropic routing

## Required Verification

Backend slice:

```bash
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend && python3 -m unittest discover -s tests && cd ..
git diff --check
git status --short
```

Frontend slice:

```bash
cd lwa-web
npm run type-check
npm run build
cd ..
git diff --check
git status --short
```

Docs-only slice:

```bash
git diff --check
git status --short
```

Full-stack slice:

```bash
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend && python3 -m unittest discover -s tests && cd ..
cd lwa-web && npm run type-check && npm run build && cd ..
git diff --check
git status --short
```

## Commit Rules

Use small commits:

- `docs: reconcile LWA doctrine and Codex ledger`
- `docs: add multi-source doctrine intake for Codex`
- `backend: restore revenue event tracking foundation`
- `web: restore multi-destination money CTA system`
- `backend: add clip intelligence contract hardening`
- `backend: realign source engine for any-source input`
- `web: rebuild rendered-proof-first studio experience`
- `docs: add elite recruitment and MVO operating system`
- `platform: add marketplace economy worlds skeleton`

Do not mix unrelated backend, frontend, iOS, and docs unless the slice truly requires it.

## Final Autonomous Codex Prompt

Paste this into Codex:

```text
You are Codex operating inside repo jcamacho611/lwa-app.

You are the autonomous implementation operator for LWA / IWA / LWA Worlds.

Read these first:
- docs/lwa-worlds-mandatory-doctrine.md
- docs/company/lwa-codex-execution-ledger.md
- docs/company/lwa-autonomous-codex-execution-brief.md
- docs/company/lwa-multi-source-doctrine-intake.md
- docs/lwa-worlds-integrated-architecture.md if present
- docs/lwa-ios-app-store-mobile-readiness-bridge.md if present
- any Claude doctrine/spec/code files present in docs or provided by the operator

Mission:
Build LWA into the full LWA Worlds platform: AI clipping engine, any-source generation, marketplace, UGC, RPG/world progression, internal economy ledger, social intelligence, admin/moderation, and future proof/chain layer.

Execution mode:
- Work autonomously.
- Do not ask for permission after every small step.
- Inspect, implement, test, commit, and report.
- Preserve working clipping/generation flow.
- Use all provided ChatGPT, Claude, and Codex information.
- Do not ignore Claude code; adapt it to the actual repo and integrate it fully where it belongs.
- Do not blindly paste code that imports nonexistent modules; create/adapt the proper modules.
- Do not rebuild completed Codex work from scratch; inspect and extend.

First task:
Perform a repo reconciliation audit against the doctrine, ledger, and multi-source intake.

Mark each reported Codex/Claude/source-bundle slice as installed, missing, partially installed, conflicting, needs tests, or ready.

Then install missing work in this order:
1. current app route/source stability
2. source upload/source-type hardening
3. backend revenue event tracking if missing
4. web multi-destination money CTA if missing
5. backend clip intelligence/entitlement hardening if missing
6. any-source source-engine realignment if missing
7. frontend rendered-proof-first rebuild
8. docs/company elite recruitment and MVO operating system if missing
9. marketplace skeleton + internal economy placeholders + RPG profile shell
10. UGC foundation
11. social integration scaffolds
12. mobile readiness bridge

Hard boundaries:
- Do not destroy working routes.
- Do not touch lwa-ios unless explicitly assigned.
- No hardcoded secrets.
- No fake payment verification.
- No client event can unlock paid access.
- No guaranteed earnings/views/viral claims.
- No token/staking/yield/gambling implementation.
- Wallet/chain features are placeholder/proof-only unless explicitly approved later.

Verification:
Run the right checks for each slice and commit only clean, scoped changes.

Final report every time:
1. branch and commit started from
2. files inspected
3. doctrine/ledger/intake/Claude sources used
4. files changed
5. features installed
6. features still missing
7. tests run
8. failures/blockers
9. commit hash/message
10. next autonomous slice

Begin now.
```

## Success Definition

Codex is ready when:

- the docs are present
- the execution ledger is present
- the multi-source intake is present
- Claude code/specs are preserved and reconciled
- existing Codex work is audited against the actual repo
- missing foundations are installed
- the app still builds/tests
- the next vertical slice can be implemented without losing context
