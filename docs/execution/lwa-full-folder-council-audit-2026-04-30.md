# LWA Full Folder Council Audit — 2026-04-30

## Scope

This audit covers the visible canonical LWA repository and connected execution context available from GitHub and the latest uploaded Codex continuation packet.

Repository audited: `jcamacho611/lwa-app`

Default branch: `main`

Production frontend recorded in canonical handoff: `https://lwa-the-god-app-production.up.railway.app`

Production backend recorded in canonical handoff: `https://lwa-backend-production-c9cc.up.railway.app`

## Important limitation

This is a GitHub/connected-context audit. It does not claim to see any unpushed local files sitting only in `/Users/bdm/LWA/lwa-app` on the Mac. The uploaded Codex continuation text mentions local dirty worktrees and local branches; those must still be verified locally before merge.

## Sources reviewed

- GitHub repository metadata
- recent pull requests
- open issues
- branch list
- `README.md`
- `docs/execution/codex-current-handoff.md`
- `docs/execution/connected-app-command-center-index.md`
- `lwa-backend/app/main.py`
- `lwa-backend/app/core/config.py`
- `lwa-web/package.json`
- uploaded Codex continuation packet covering Chunk 4, Chunk 8, Chunk 9, Chunk 11, Director Brain v0, guest UX problems, and frontend simplification work

## Executive verdict

LWA is no longer a loose idea. It is a real multi-surface product/repo with:

- working backend app structure
- working frontend app structure
- iOS folder present and repeatedly protected from unrelated edits
- Railway production URLs documented
- active GitHub command center
- merged scaffolds for marketplace, Realms, social integrations, proof, operator dashboard, growth, and creative command center
- Whop verified webhook MVP merged
- Seedance disabled-safe scaffold merged
- quality gate foundation merged
- Director Brain backend improvements merged
- one active draft PR for Director Brain v0 + recommendation rail
- new open issues for Chunk 11 auth hardening and guest generate UX launch blocker

Primary concern: the repo has accumulated many branches, duplicate/superseded PRs, and multiple simultaneous Codex contexts. The product can still move fast, but only if changes are isolated by issue/branch and the canonical source of truth remains `main` + command-center issues.

## Immediate launch blocker ranking

1. **P0 — Guest generate UX**: Issue #73. Fix raw JSON export, live-stream preflight, no-preview card display, out-of-credits CTA, and one-input guest flow.
2. **P0 — Auth/ownership/security**: Issue #72 / Chunk 11. Needed before real marketplace, payouts, admin actions, and user-owned resource protection.
3. **P0 — Open PR #71 decision**: Draft PR is mergeable into `feat/source-poc-matrix`, not `main`. It must be reviewed against current branch strategy before merging.
4. **P1 — Local branch hygiene**: uploaded Codex log shows dirty local worktrees. Only scoped commits should be staged. No `git add .` until local diff is audited.
5. **P1 — Full verification pass**: backend tests, frontend type-check/build, route smoke, Railway health, and incognito guest QA after Issue #73.

---

# Council Reports

## 1. Founder / CEO Council — Justin / High Director of the Signal

### What is clear

The founder direction is extremely clear and repeatedly documented:

- Do not restart.
- Finish, add, complete, enhance.
- Preserve existing working systems.
- Avoid duplicates.
- Use connected apps and professional council lanes.
- Keep LWA clipping-first.
- Guest flow must be simple: one input, one action, useful output.
- Do not show confusing raw JSON or black broken-looking previews to users.

### Status

Strong. Founder intent is captured in issues, docs, handoff files, uploaded continuation logs, and command-center artifacts.

### Risks

- Too many simultaneous AI/Codex sessions can cause branch drift.
- Founder urgency is valid, but merge discipline must stay strict.

### Required action

The CEO council should enforce this rule:

```text
No branch merges unless the branch states issue number, files changed, tests run, and whether iOS/backend/frontend were touched.
```

---

## 2. Principal Engineering Council

### Current backend architecture

`lwa-backend/app/main.py` registers many route groups, including generation, upload, campaigns, wallet, posting, clip status, visual generation, Seedance, Whop webhooks, clips, edit, and intelligence routes.

The backend config file contains extensive production configuration for:

- free launch mode
- guest rate limits
- plan/credit limits
- generated assets
- uploads
- usage stores
- abuse controls
- clipping/platform databases
- JWT config
- OpenAI/Anthropic/Ollama/Seedance/visual engine
- Whop verification
- social platform keys
- service version

### What is strong

- Backend is modular and already has many capability surfaces.
- Route registration is centralized.
- Config is env-driven.
- Production and Railway assumptions are documented.
- Multiple backend scaffold PRs were merged safely and narrowly.

### Risks

- `app.main` has many route imports. Any broken import can break boot.
- SQLite-backed persistence appears to be used heavily; marketplace/money/payout evolution must be careful.
- Auth/ownership is not yet fully hardened, which is dangerous before money/admin expansion.

### Required action

Complete Issue #72 after #73, but do not mix it with guest UX. Add roles, actor dependency, admin guard, owner-or-admin checks, and docs/tests.

---

## 3. Frontend / Product UX Council

### Current frontend architecture

`lwa-web/package.json` shows Next.js 14, React 18, TypeScript, Tailwind, Three.js, Spine WebGL, Rive, Framer Motion, and Anthropic SDK.

### What is strong

- The frontend stack supports the mythic/world/character vision.
- The product has a real live UI surface.
- Free launch banner exists.
- Director Brain display surfaces have been progressively added.
- The uploaded logs show guest simplification work was attempted and some frontend type-checks/builds passed.

### Critical problem

Guest UX is still the most dangerous visible launch issue. The user specifically reported:

- export bundle opens JSON
- black preview/no-preview experience feels broken
- live stream handling confuses the user
- clutter remains unacceptable
- first click should automate or clearly move forward

### Required action

Issue #73 is the top frontend issue. It should be implemented before deeper auth, marketplace, Realms, or social features.

### Non-negotiable UX rule

```text
Guest view = source input + generate action + clean hook-first results. No operational dashboard panels.
```

---

## 4. AI / Media Pipeline Council

### Current status

- Director Brain improvements are merged in PR #63.
- Open draft PR #71 adds a deterministic Director Brain v0 slice and recommendation rail on `feat/source-poc-matrix`.
- Quality gate foundation merged in PR #47.
- Omega visual engine tests merged in PR #62.
- Core intelligence foundations merged in PR #50.

### What is strong

The intelligence system is no longer just concept docs. Backend services/tests exist for Director Brain, quality gate, proof, marketplace primitives, social integration primitives, etc.

### Risks

- Multiple Director Brain paths/branches may overlap: PR #63 merged Director Brain v0.2 fields, while #71 also adds Director Brain v0 and recommendation rail on a feature branch. Must avoid duplicate or conflicting Director Brain modules.
- Strategy-only outputs must remain clearly non-rendered.

### Required action

Review PR #71 manually. Merge only if it adds non-duplicative value beyond current `main`, or retarget/cherry-pick only the frontend recommendation rail if backend overlap exists.

---

## 5. Backend / Render Pipeline Council

### Current status

- README documents rendered-first UI and strategy-only lane.
- Quality gate service and tests exist.
- Visual engine and Seedance disabled-safe scaffolds exist.
- Health/dependency state was previously confirmed in conversation: ffmpeg, yt-dlp, OpenAI configured.

### Risks

- Live-stream URLs can produce strategy-only/no-preview output. This must be preflighted in frontend and eventually classified in backend source validation.
- Export bundle UX currently exposes backend JSON behavior to users.

### Required action

Backend should stay untouched for #73 unless the frontend cannot force download due to missing `download_url`/filename fields. If backend is touched, update export endpoint to return a download-safe attachment or explicit frontend-ready response.

---

## 6. Marketplace / Revenue Council

### Current status

- Marketplace scaffold foundation merged in PR #64.
- Billing/entitlements/credits/earnings/payout-placeholder work from uploaded Codex log appears to have been completed locally with tests, but its canonical GitHub merge state must be verified.
- Whop verified webhook MVP merged in PR #37.
- Growth/sales/investor pack merged in PR #68.

### What is strong

- Money safety rules are repeated everywhere: integer cents, no guaranteed earnings, no fake payouts.
- Whop entitlement verification has a real HMAC signature MVP when env-gated.

### Risks

- Payout placeholders must not be mistaken for real payouts.
- Revenue event tracking is non-authoritative unless backed by verified webhook/payment state.
- Auth/ownership still missing, so marketplace expansion must wait for Issue #72.

### Required action

Do not build real payouts until auth/roles, webhook idempotency, ledger/dispute/KYC safety, and admin guards are implemented and tested.

---

## 7. Game Systems / Signal Realms Council

### Current status

- Signal Realms scaffold merged in PR #65.
- Proof/off-chain scaffold merged in PR #67.
- Founder wants RPG/world layer, but current practical priority remains clipping-first.

### What is strong

- Realms rules are safe: no bought XP, badges earned, relics cosmetic, no investment framing.
- Proof is off-chain/provenance-only.

### Risks

- World/character layer can drift into clutter and distract from clipping product.
- Any blockchain or relic UI must not imply financial upside.

### Required action

Keep Realms behind clear scaffold/beta docs until core clipping UX is clean and Issue #73 is fixed.

---

## 8. Legal / Compliance / Trust Council

### Current status

- Safety language is strong across docs.
- Marketplace restrictions and no-guarantee rules are present.
- Polymarket is documented as read-only cultural metadata, not betting/trading advice.
- Proof/blockchain is provenance-only.

### High-risk gaps

- Demo/auth behavior must not be production-trusted.
- Admin/finance/ownership routes need guards.
- User-owned files/jobs/earnings/deliveries must not be accessible by other users.
- Role claims from frontend must not be trusted.

### Required action

Issue #72 is compliance-critical. It must be implemented before any real marketplace/payout/admin expansion.

---

## 9. Growth / Sales / Investor Council

### Current status

- Growth/sales/investor pack merged in PR #68.
- Gmail labels/drafts exist per connected-app index.
- Canva/Figma/Lovable collateral exists.

### What is strong

- Outreach infrastructure exists.
- Product truth vs roadmap is separated.
- No guaranteed earnings language is baked into the sales guidance.

### Risks

- Sales should not drive traffic until Issue #73 is fixed; confusing guest UX damages trust.
- Investor demo should avoid raw JSON/export/black preview issues.

### Required action

Pause broad outreach until guest generate path is clean in incognito with a normal uploaded YouTube URL and export no longer opens raw JSON.

---

## 10. DevOps / Infrastructure Council

### Current status

- Railway production URLs are documented.
- README has backend/frontend Railway deploy settings.
- Config is env-heavy and production-sensitive.
- Auto-merge is disabled in repo settings.

### Risks

- Many environment variables exist; env drift between backend and frontend can cause false behavior.
- Railway CLI may require auth locally, as noted in uploaded context.
- Open draft PR #71 targets `feat/source-poc-matrix`, not `main`.

### Required action

Maintain an env checklist:

```text
FREE_LAUNCH_MODE
NEXT_PUBLIC_FREE_LAUNCH_MODE
OPENAI_API_KEY
ANTHROPIC_API_KEY for web character route if used
LWA_DEFAULT_CREDITS_REMAINING
LWA_DEFAULT_PLAN_NAME
WHOP_WEBHOOK_SECRET if Whop verification enabled
LWA_ENABLE_WHOP_VERIFICATION
```

---

## 11. iOS Council

### Current status

`lwa-ios/` exists and is documented as not a Railway deploy target. Multiple PRs explicitly preserved iOS untouched.

### What is strong

- The team has consistently avoided accidental iOS changes.
- iOS appears to be treated as a separate lane.

### Risks

- Auth identity linking will eventually matter for Apple/iOS, but this is not part of Issue #73.

### Required action

Do not touch iOS until a dedicated iOS branch/issue exists.

---

## 12. World Engine / Visual Systems Council

### Current status

- Frontend dependencies include Three.js, Spine WebGL, and Rive.
- Character/world vision exists in connected docs and previous artifacts.
- Seedance/visual engine scaffolds exist in backend.

### What is strong

The repo can support the future living-world direction technically.

### Risks

- The founder repeatedly rejected clutter and world-layer interference with the clipping workflow.
- World visuals must not replace product proof.

### Required action

Keep world/character UI either background-safe or outside the guest generate core until the clip flow is elite.

---

## 13. Prototype / Experiments Council

### Current status

- Lovable prototype exists and is ready.
- Canva/Figma assets are indexed.
- Standalone LWA engine CLI prototype merged in PR #48.

### Risks

- Prototype work must not be confused with production features.
- Experiments must stay clearly labeled.

### Required action

Use prototypes for demo/support only. Do not let them override production repo truth.

---

# Folder-Level Audit

## Root

### Status

The repo root has a clear README and docs folder. The README describes current product truth: ranked clip packs, Director Brain metadata, rendered-vs-strategy-only workflow, recovery actions, backend/frontend/iOS layout, and Railway deploy settings.

### Needed

Add a short `CURRENT_TOP_PRIORITY.md` or keep updating command-center issue #49 so Codex does not chase old chunks out of order.

## `lwa-backend/`

### Status

Healthy but broad. The backend has many route families and substantial configuration.

### Strengths

- Central FastAPI entrypoint.
- Many route groups already registered.
- Env-driven settings.
- Whop webhook MVP.
- Seedance/visual disabled-safe scaffold.
- Quality gate, Director Brain, and intelligence foundations.

### Weaknesses

- Auth/role/ownership layer is not yet done.
- Many features are scaffolded, not production-complete.
- Need strict boot/import tests after every route addition.

### Priority

Issue #72 after Issue #73.

## `lwa-web/`

### Status

Powerful stack and visible product surface. Also the current top source of user-facing pain.

### Strengths

- Next.js stack.
- World/character-ready dependencies.
- Generate/result surface exists.
- Free launch banner exists.
- Director Brain display support exists.

### Weaknesses

- Guest generate flow still needs simplification.
- Export bundle UX must stop exposing raw JSON.
- Live-stream preflight must prevent bad source expectations.
- No-preview strategy-only state must look intentional, not broken.

### Priority

Issue #73 now.

## `lwa-ios/`

### Status

Present, intentionally not touched by current web/backend work.

### Priority

Leave alone unless dedicated iOS issue/branch.

## `docs/`

### Status

Very rich. Contains command center, handoff, phase runbooks, algorithm chunks, scaffold docs, growth/creative/proof/social/marketplace docs.

### Strengths

- Excellent continuity for Codex and other agents.
- Connected-app index prevents losing work.
- Context/memory export exists.

### Weaknesses

- Docs volume is now high. Need one current top-priority pointer.
- Some historical docs reference older paths like `apps/backend`; newer audit corrects to `lwa-backend`/`lwa-web`.

### Priority

Keep docs additive, but do not let docs replace runtime verification.

## `tools/`

### Status

Contains standalone LWA engine CLI prototype from PR #48.

### Priority

Keep isolated from production runtime.

---

# Branch / PR Audit

## Open PRs

### PR #71 — `[codex] add Director Brain v0 recommendation rail`

Status: open, draft, mergeable.

Base: `feat/source-poc-matrix`, not `main`.

Risk: potential overlap with current `main` Director Brain work from PR #63 and frontend display work from PR #41.

Decision required:

```text
Do not merge blindly. Review diff against current main/feature branch. If valuable, cherry-pick scoped frontend rail or retarget after checking conflicts.
```

## Recently merged major PRs

- #70 creative command center pack
- #69 operator dashboard scaffold
- #68 growth sales investor pack
- #67 off-chain proof scaffold
- #66 social integrations scaffold
- #65 Signal Realms scaffold
- #64 marketplace scaffold
- #63 Director Brain scoring output
- #62 Omega visual engine tests
- #50 core intelligence foundations
- #48 standalone LWA engine CLI prototype
- #47 quality gate foundation
- #42 remaining algorithm chunks
- #41 Director Brain intelligence panel fields
- #39 free launch banner
- #38 Seedance disabled-safe scaffold
- #37 Whop verified webhook MVP
- #34 Chunk 16 source/Director Brain intelligence
- #33 compare/use-case hub pages
- #32 remaining build runbook
- #30 master council report and audit
- #28 Chunk 16 P0 source and Director Brain foundations

## Superseded / duplicate PRs

- #55 closed in favor of later Omega test path
- #46 closed hardening duplicate/unmergeable
- #45 duplicate docs runbook
- #44 broader docs branch closed
- #36 superseded Claude/Seedance branch
- #29 replaced by #30

## Branch hygiene note

Branch list is large. Branches that correspond to merged/closed PRs should eventually be pruned after confirming no unique commits remain.

---

# Open Issue Audit

## #73 — Fix guest generate UX

Status: top launch blocker.

Owner: Frontend/Product UX Council.

Required before serious public demo.

## #72 — Chunk 11 auth/roles/security

Status: security-critical.

Owner: Principal Engineering + Legal/Trust.

Required before real marketplace/admin/money scaling.

## #35 — Remaining Work Queue

Status: still relevant. Launch-critical checklists remain.

## #24 — Any-source God App realignment

Status: strategic direction. Important but should not derail #73.

## #23 — Game/blockchain ecosystem exploration

Status: later exploration. Do not run before core UX/auth.

## #22 — Recruiting operating system

Status: company ops. Useful, but not a product blocker.

## #16 — Master production checklist

Status: useful long-term checklist. Should be reconciled with current command center.

## #13 — Founder vision dump

Status: core founder truth. Keep using it to reject clutter and fake completeness.

## #11 — Separate clipping UI from world-layer drift

Status: directly supports #73. Guest generate flow must remain clipping-first.

## #5 — Claude/Seedance implementation

Status: older but mostly addressed by Anthropic/Seedance work. Keep as historical context.

---

# Numerical Chunk Audit From Uploaded Context

The uploaded continuation packet says:

- Chunk 4 billing/entitlements/credits/earnings/payout-placeholder foundation was completed locally and verified with focused tests, full backend tests, backend compile, frontend type-check, and diff check.
- Codex then identified Chunk 5 as already present/covered.
- Chunk 8 jobs scaffold was started and focused tests passed.
- Chunk 9 clipping control plane was started.
- Chunk 11 auth/roles/security was planned, not necessarily implemented.
- The user requested numerical order and not jumping ahead.

Audit decision:

```text
Use Issue #73 for immediate live UX blocker.
Then verify whether Chunk 8/9 local work is pushed/PR’d.
Then continue numerical order.
Do not execute Chunk 11 until intervening pushed work is reconciled, unless security blocks money/admin paths.
```

---

# Missing / Weak Areas

## P0 missing

- Clean guest generate flow (#73)
- Auth/actor/ownership/admin guard foundation (#72)
- Full latest local branch reconciliation from uploaded Codex sessions
- Verification of Chunk 8/9 local work in GitHub
- Export bundle UX fix
- Live-stream source preflight

## P1 missing

- Consolidated branch cleanup
- Current top-priority pointer doc
- Full smoke test sheet with screenshots/URLs
- Route guard checklist implementation
- Entitlement gates applied broadly
- Production-safe demo auth plan

## P2 missing

- Real auth provider selection and implementation
- Full social OAuth/direct posting approvals
- Real marketplace routes and checkout
- Real payouts/KYC/disputes
- Real animated Spine assets
- Real character-speak route if not already implemented in web
- Real performance audit of world/character UI

---

# Recommended Execution Order

## Step 1 — Fix live guest UX

Issue: #73

Branch suggestion:

```text
fix/guest-generate-ux-73
```

Verification:

```bash
cd lwa-web && npm run type-check && npm run build
cd .. && git diff --check
```

## Step 2 — Reconcile local Chunk 8/9 work

Find whether these exist in GitHub:

```text
lwa-backend/app/worlds/jobs/*
lwa-backend/app/worlds/clipping/*
lwa-web/app/jobs/page.tsx
docs/lwa-worlds-job-queue-architecture.md
docs/lwa-worlds-job-retry-policy.md
```

If local-only, create scoped PRs.

## Step 3 — Review PR #71

Do not merge blindly. Determine whether backend Director Brain work duplicates #63 or whether only the rail is needed.

## Step 4 — Implement Chunk 11 auth/roles/security

Issue: #72

Must be additive and tested.

## Step 5 — Run full launch verification

Use issue #35 checklist.

---

# Codex Prompt For The Next Audit-Safe Move

```text
You are Codex working in jcamacho611/lwa-app.

Start with Issue #73.

Do not touch iOS.
Do not touch backend unless export API contract is actually broken.
Do not merge unrelated local dirty files.
Do not run Chunk 11 yet.

Goal:
Fix guest generate UX so a first-time user gets one-input clipping flow, live-stream preflight, no raw JSON export, no black broken preview card, no cluttered rails, and clear out-of-credits messaging.

Files allowed:
- lwa-web/components/clip-studio.tsx
- lwa-web/components/HeroClip.tsx
- lwa-web/components/VideoCard.tsx
- frontend API helper only if export download needs it

Verification:
cd lwa-web && npm run type-check && npm run build
cd .. && git diff --check

Return:
1. files inspected
2. files changed
3. guest UX before/after
4. export behavior before/after
5. live-stream behavior
6. tests run
7. commit hash
8. any deferred items
```

---

# Final Audit Judgment

No council lane is missing. The problem is not lack of ideas or lack of scaffolds. The problem is now execution order and launch discipline.

The product is closest to progress if the team does this:

1. Fix visible guest UX (#73).
2. Reconcile local pushed/unpushed chunk work.
3. Review PR #71 without duplicating Director Brain.
4. Implement auth/ownership (#72).
5. Verify production.

Do not expand into marketplace runtime, Realms runtime, social posting, or blockchain until those are clean.
