# LWA TEAM EXECUTION INDEX

This is the team-facing source of truth for the current LWA build. Use this when handing work to Windsurf, Codex, or any engineer. It organizes the ChatGPT project thread, the Windsurf log, the Lee-Wuh issue, the no-API requirement, and the full platform route plan into one execution order.

## What LWA is now

LWA is no longer just a clip generator. LWA is a creator operating system with connected product surfaces:

1. Clip generation and content decision engine.
2. Dashboard / command center.
3. Lee-Wuh game / realm / progression layer.
4. Marketplace and campaign work layer.
5. Wallet / credits / usage / later payout layer.
6. Upload / ingestion layer.
7. History / proof vault layer.
8. Lee-Wuh living visual agent and Blender / 3D asset pipeline.

The product promise remains simple:

```text
Drop content. Get the best thing to post. Progress your creator world. Turn output into money.
```

## Current verified repo anchors

These are known repo anchors the team should treat as existing context:

```text
docs/runbooks/LWA_FULL_PLATFORM_PAGE_BLUEPRINT.md
lwa-backend/app/services/deterministic_clip_engine.py
lwa-backend/scripts/test_offline_generation.py
lwa-web/lib/demo-data.ts
lwa-web/app/dashboard/page.tsx
lwa-web/app/realm/page.tsx
lwa-web/app/marketplace/page.tsx
lwa-web/app/campaigns/page.tsx
lwa-web/app/wallet/page.tsx
lwa-web/app/upload/page.tsx
lwa-web/app/history/page.tsx
```

Known missing or incomplete anchor:

```text
lwa-web/components/navigation.tsx
```

The `/game` route may not exist yet. Current game/world route appears to be `/realm`. Do not duplicate blindly. If `/realm` is the canonical game route, either keep `/realm` or create `/game` as a safe redirect/link shell to `/realm`.

## Open issue anchor

Issue #148 is the Lee-Wuh living agent build home:

```text
https://github.com/jcamacho611/lwa-app/issues/148
```

It defines Lee-Wuh as the clickable, animated, breathing, world-aware intelligence layer of the site, with marketplace routing, game/world portal behavior, Blender source pipeline, GLB export target, and future Rive/Spline/XR path.

## Non-negotiable build laws

```text
- Do not touch lwa-ios unless explicitly assigned.
- Do not force push.
- Do not delete existing files unless unavoidable and explained.
- Do not add new external AI dependencies for core output.
- External AI can remain optional enhancement only.
- LWA must work without external AI APIs for strategy clips.
- Rendering is optional.
- Intelligence is required.
- Never return empty clip results.
- Minimum output is 3 strategy clips.
- Strategy-only clips must not pretend to be rendered playable videos.
- Lee-Wuh must never render as a generic emoji mascot.
- LWA remains the product/company name.
- Lee-Wuh is the mascot, living agent, and world guide.
```

## Critical warning from the Windsurf log

The log shows that earlier work committed backend/frontend files even while frontend type-check/build errors were still present. That must not happen again.

Hard rule:

```text
No commit is allowed unless the relevant verification commands pass.
```

For frontend work:

```bash
cd lwa-web
npm run type-check
npm run build
npm run lint
```

For backend work:

```bash
cd lwa-backend
python3 -m compileall .
python3 scripts/test_offline_generation.py
```

For repo hygiene:

```bash
git diff --check
git status -sb
```

Warnings can be reported. Errors are blockers.

## Correct execution order

### Phase 0 — Stabilize current main

Goal: confirm main is clean before new work.

Run:

```bash
cd lwa-web
npm run type-check
npm run build
npm run lint

cd ../lwa-backend
python3 -m compileall .
python3 scripts/test_offline_generation.py

cd ..
git diff --check
git status -sb
```

If any command fails, stop and fix that before adding features.

### Phase 1 — Finish no-API user experience

Goal: make the app truthfully usable without external AI APIs.

Required behavior:

```text
User pastes text/transcript/idea or a source fails.
LWA still returns at least 3 strategy clips with title, hook, caption, post_rank, why_this_matters, cta, thumbnail_text, and render_status.
```

Tasks:

```text
1. Verify deterministic engine returns 3+ clips.
2. Verify /generate or /v1/generate falls back to deterministic output if normal generation fails.
3. Verify /v1/generate-text or equivalent text path exists.
4. Verify demo-data.ts is actually wired to a visible Try Demo action.
5. Verify frontend maps offline clips to normal result cards.
6. Verify best clip appears first.
7. Verify no dead error screen appears when APIs/rendering fail.
```

Commit only after backend offline test and frontend checks pass.

Recommended commit:

```text
feat(core): finish no-api generation fallback
```

### Phase 2 — Navigation and platform shell

Goal: make the multi-page creator OS navigable.

Tasks:

```text
1. Create or verify `lwa-web/components/navigation.tsx`.
2. Link Dashboard, Generate, Realm/Game, Campaigns, Marketplace, Upload, History, Wallet.
3. Do not duplicate route logic.
4. If `/game` is missing and `/realm` exists, create a light `/game` route that points users into `/realm`, or standardize nav to `/realm`.
5. Do not touch backend.
```

Recommended commit:

```text
feat(web): add platform navigation shell
```

### Phase 3 — Lee-Wuh living agent v0

Goal: install Lee-Wuh as a useful clickable guide without waiting for perfect Blender.

Build:

```text
lwa-web/components/lee-wuh/LivingLeeWuhAgent.tsx
lwa-web/components/lee-wuh/LeeWuhWorldBackdrop.tsx
```

Behavior:

```text
- floating bottom-right visual presence
- idle aura/breathing CSS motion
- click opens speech/options panel
- routes users to Generate, Marketplace, Post Job, Campaigns, Realm, Dashboard/Company OS
- uses image/PNG/SVG fallback first
- never blocks the main work zone
- never uses emoji fallback
```

Recommended commit:

```text
feat(web): add Lee-Wuh living agent shell
```

### Phase 4 — Lee-Wuh visual system for /generate

Goal: make /generate beautiful, intense, smooth, and non-crowded.

Design law:

```text
The center is the work zone.
Lee-Wuh is atmosphere and presence at the edges.
The user must know what to do in 3 seconds.
```

Tasks:

```text
1. Use blurred/low-opacity Lee-Wuh world background.
2. Keep input and result cards clean.
3. Best clip is the hero.
4. Ranked clip stack below.
5. Strategy-only badge is clear.
6. Character is bottom-right or edge presence, not center clutter.
```

Recommended commit:

```text
feat(web): apply Lee-Wuh generate page visual system
```

### Phase 5 — Blender / 3D pipeline

Goal: make the Lee-Wuh 3D production path real, but not required for app load.

Create or verify:

```text
brand-source/lee-wuh/references/
brand-source/lee-wuh/textures/
brand-source/lee-wuh/lee-wuh-character-blockout.blend
scripts/blender/create_lee_wuh_living_agent.py
lwa-web/public/characters/lee-wuh/lee-wuh.glb
lwa-web/public/characters/lee-wuh/lee-wuh-idle.glb
lwa-web/public/characters/lee-wuh/lee-wuh-loading.glb
lwa-web/public/characters/lee-wuh/lee-wuh-victory.glb
```

Rules:

```text
- GLB is an upgrade, not a dependency.
- App must load with PNG/SVG fallback if GLB is missing.
- High-poly Blender source and web-optimized GLB are separate assets.
```

Recommended commit:

```text
feat(blender): add Lee-Wuh character blockout pipeline
```

### Phase 6 — Marketplace and campaign shell safety

Goal: create money/opportunity surfaces without fake payouts.

Rules:

```text
- No fake payouts.
- No fake escrow.
- No guaranteed earnings.
- Marketplace money UI must be demo/manual until ledger exists.
- Campaigns can support manual/draft workflow first.
```

Recommended commit:

```text
feat(web): harden marketplace and campaign shells
```

### Phase 7 — Auth, ownership, ledger before real money

Goal: server-side safety before any real payment or payout.

Backend must have:

```text
Actor model
get_current_actor
require_admin
require_owner_or_admin
server-side entitlement checks
audit log for admin/money actions
credits ledger
webhook idempotency before paid automation
```

Recommended commit:

```text
feat(backend): add ownership guards and ledger foundation
```

## Windsurf master prompt

Paste this to Windsurf when continuing from this point:

```text
You are the LWA Senior Full-System Engineer.

Read `docs/runbooks/LWA_TEAM_EXECUTION_INDEX.md` first.

Your job is to continue the build in order without breaking existing work.

Current priority:
1. Verify main is clean.
2. Finish no-API generation fallback in real user experience.
3. Add or verify platform navigation.
4. Add Lee-Wuh living agent v0.
5. Apply Lee-Wuh visual system to /generate.
6. Only then continue Blender, marketplace, campaign, game, wallet, and money systems.

Non-negotiables:
- Do not touch `lwa-ios`.
- Do not force push.
- Do not add external AI dependencies to core output.
- Do not delete existing routes/components.
- Do not commit with failing type-check/build/lint.
- Do not create fake payouts.
- Do not use emoji fallback for Lee-Wuh.

Before editing:
- Print `git status -sb`.
- Print exact files you plan to touch.
- State whether web/backend/iOS will be touched.

After editing:
- Run required verification commands.
- Report files changed.
- Report what was preserved.
- Report what remains incomplete.
- Give the commit message.

Start with Phase 0 verification only. Do not skip ahead.
```

## Emergency stop prompt

Use this if Windsurf deviates:

```text
STOP.

Do not rewrite the app.
Do not touch `lwa-ios`.
Do not add external AI dependencies.
Do not remove `/generate`.
Do not add payment or payout logic.
Do not commit while checks are failing.
Do not use emoji fallback for Lee-Wuh.

Return to `docs/runbooks/LWA_TEAM_EXECUTION_INDEX.md` and continue the current phase only.
```

## Done condition for current sprint

The current sprint is done only when:

```text
- Main passes type-check/build/lint.
- Backend offline test passes.
- User can generate 3+ strategy clips without external AI APIs.
- Demo mode is visible and works.
- Dashboard/generate/realm/marketplace/campaigns/wallet/upload/history routes render.
- Navigation links the core platform pages.
- Lee-Wuh is available as a living guide or at least a non-emoji visual fallback.
- No fake payout or fake escrow language is shipped.
```
