# LWA Multi-Source Doctrine Intake

## Status

This document is a repo-visible intake ledger for the latest operator-provided source bundle.

It captures the combined direction from:

- ChatGPT strategy/doctrine threads
- Claude strategy/spec/code threads
- Codex implementation/history logs
- LWA Worlds Master Council Report chunks
- Frontend rebuild specs
- Codex terminal runbooks/artifacts
- MVP truth/state summaries

This file is mandatory context for Codex. It does not replace the existing doctrine. It adds traceability for the newest uploaded bundle and tells Codex how to use it.

## Why This Exists

The operator is building LWA across multiple tools at the same time:

- ChatGPT creates doctrine, architecture, product direction, and execution prompts.
- Claude creates parallel specs/code ideas that must be preserved and adapted.
- Codex implements inside the repo.
- GitHub docs are the source of truth that stops context from getting lost.

Codex must treat all uploaded strategic/build files as required source material, but must still reconcile them against the actual repo before modifying runtime code.

## Mandatory Source Categories From The Uploaded Bundle

### 1. Master Council Report

The Master Council Report defines the full platform direction:

- Phase 1 clipping engine hardening
- FREE_LAUNCH_MODE
- fallback hardening
- README/developer onboarding polish
- competitive intelligence
- platform signal database
- marketplace architecture
- RPG/world system: The Signal Realms
- social API plan
- blockchain/NFT/appchain roadmap as future proof layer
- hiring/council roles
- master Codex prompt stack

Codex must use it as the long-range architecture map, not as permission to dump all code into one unsafe commit.

### 2. Current Product Truth / MVP State

The app is currently a real MVP, not a mockup.

Current truth to preserve:

- public URL to clip-pack flow exists
- backend can return titles, hooks, captions, timestamps, scores, and asset links
- backend real-clip pipeline can generate raw/edited clip assets when healthy
- vertical 9:16 exports exist when the pipeline succeeds
- iOS preview/share/save behavior has been reported working
- iOS Debug, Release, and Archive builds have reportedly passed

Current gaps to close:

- direct phone/camera roll/Files/Drive uploads
- full editor/timeline/trim/caption editing
- bulk batch review
- campaign manager
- direct social posting
- account/workspace/cloud history
- strong entitlement/paywall enforcement
- full Whop workflow
- OpusClip-level 20-40 polished clips per source

Codex must preserve the honest customer-facing claim:

> LWA is a working long-form-to-short-form clip generator and review console. It is being upgraded into a full creator campaign operating platform.

### 3. Frontend Rebuild Doctrine

The frontend rebuild is mandatory and should be treated as a major open product slice.

Required UX direction:

- source-first input
- auto destination as default
- rendered proof first
- strategy-only results useful but secondary
- one strong generate action
- clear recommendation rail
- clear processing phases
- lead best clip first
- rendered clips lane
- strategy-only lane
- packaging/export rail
- mythic premium world layer at the edges, not blocking utility
- mobile-safe stacking

Likely frontend targets:

- `lwa-web/components/clip-studio.tsx`
- `lwa-web/components/VideoCard.tsx`
- `lwa-web/components/HeroClip.tsx`
- `lwa-web/lib/types.ts`
- `lwa-web/lib/api.ts`

Codex must not treat all result cards equally. Rendered/playable clips must be visually and functionally distinct from strategy-only outputs.

### 4. Codex Terminal Track Rules

The uploaded terminal lane docs establish a strict rule:

- Frontend prompt belongs to frontend terminal / `lwa-web` only.
- Backend prompt belongs to backend terminal / `lwa-backend` only.
- iOS must not be touched unless explicitly assigned.
- If the wrong terminal receives the wrong prompt, stop and report status.
- Do not commit if backend/web/iOS boundaries were crossed unintentionally.

Codex must preserve this lane discipline even when working autonomously.

### 5. Codex Artifact Bundle

The Codex artifact bundle is part of the build record and includes:

- START HERE Codex Terminal runbook
- master Codex terminal prompt
- Codex system prompt
- frontend rebuild track prompt
- backend free launch + fallbacks prompt
- Director Brain v0 prompt
- marketplace MVP later prompt
- Realms + proof layer later prompt
- emergency stop prompt
- master execution report
- roadmap spreadsheet
- investor pitch deck
- architecture PDF/blueprint/diagram
- terminal runbook

If these artifacts are not present in the repo, Codex must preserve their existence as docs/source references and should add missing text versions when available.

### 6. Claude Code / Claude Doctrine Rule

Claude-provided code/specs are mandatory source material.

Codex must:

1. Identify every Claude-originated file/chunk.
2. Preserve it as doctrine/spec if it cannot be safely pasted.
3. Inspect imports and module assumptions.
4. Adapt code to the real repo structure.
5. Install the functionality when it belongs to the active slice.
6. Create missing support modules only when that is the correct integration path.
7. Never ignore Claude code merely because an earlier assistant warned not to paste it directly.
8. Never blindly paste Claude code if it imports nonexistent modules or breaks the app.

The standard is: **use it in full by adapting it into LWA correctly, not by careless copy-paste.**

## Unified Execution Priority After Intake

Codex must execute in this order:

1. Reconcile doctrine/ledger/Claude/source-bundle against actual repo state.
2. Preserve working clipping/generation flows.
3. Finish route/source stability.
4. Finish source upload/source-type hardening.
5. Install/reconcile reported Codex slices:
   - backend revenue event tracking
   - web multi-destination money CTA system
   - backend intelligence/entitlement hardening
   - any-source source-engine realignment
   - company ops/recruitment/MVO docs
6. Execute the frontend rebuild slice.
7. Execute backend FREE_LAUNCH_MODE + fallback hardening.
8. Execute Director Brain v0.
9. Execute marketplace skeleton + internal economy placeholders.
10. Execute RPG/Signal Realms profile shell.
11. Execute UGC foundation.
12. Execute social integration scaffolds.
13. Execute mobile readiness bridge.
14. Execute proof/chain placeholders only, not real token/payout/chain launches.

## Implementation Rules

Codex should work autonomously, but every implementation must be traceable.

Before coding, Codex must report:

- branch and commit
- dirty files
- doctrine files found
- ledger files found
- Claude/source-bundle files found
- installed slices
- missing slices
- conflicting slices
- planned touched files
- planned untouched files
- tests to run

During coding, Codex must:

- keep commits scoped
- avoid iOS unless assigned
- avoid hardcoded secrets
- preserve existing routes/contracts unless a defect is proven
- put external-dependent systems behind disabled feature flags
- use truthful product copy
- avoid guaranteed earnings/views/viral claims
- avoid token/staking/yield/gambling language

After coding, Codex must report:

- files inspected
- files changed
- tests run
- failures/blockers
- installed features
- missing features
- commit hash/message
- next autonomous slice

## Active Next Prompt For Codex

```text
You are Codex operating inside repo jcamacho611/lwa-app.

Read first:
- docs/lwa-worlds-mandatory-doctrine.md
- docs/company/lwa-codex-execution-ledger.md
- docs/company/lwa-autonomous-codex-execution-brief.md
- docs/company/lwa-multi-source-doctrine-intake.md
- docs/lwa-worlds-integrated-architecture.md if present
- docs/lwa-ios-app-store-mobile-readiness-bridge.md if present
- every Claude/source-bundle doc or code file present in docs/ or provided by the operator

Mission:
Use all ChatGPT, Claude, and Codex context as mandatory project source material. Reconcile it against the actual repo and then implement the platform in scoped autonomous slices.

Do not ignore Claude code. Adapt it to the real repo and integrate it where it belongs.
Do not blindly paste code that breaks imports or working flows.
Do not touch lwa-ios unless explicitly assigned.
Do not create fake payment verification, guaranteed earnings, token/staking/yield/gambling features, or hardcoded secrets.

First action:
Perform the doctrine/source-bundle reconciliation audit.

Then install missing work in this order:
1. route/source stability
2. source upload/source-type hardening
3. reported Codex foundations
4. frontend rebuild
5. backend FREE_LAUNCH_MODE + fallbacks
6. Director Brain v0
7. marketplace + internal economy skeleton
8. Signal Realms RPG shell
9. UGC foundation
10. social integration scaffolds
11. mobile readiness bridge
12. proof/chain placeholders only

Run appropriate backend/frontend/docs verification for each slice.
Commit only clean scoped changes.
Report exact files, tests, blockers, commit hash, and next slice.
```

## Definition Of Done For This Intake

This intake is complete when:

- this file exists in repo
- the autonomous Codex brief points to this file
- PR #44 includes the new intake
- Codex can start from repo docs without needing this chat open
- future implementation reports reference this file when using the uploaded source bundle
