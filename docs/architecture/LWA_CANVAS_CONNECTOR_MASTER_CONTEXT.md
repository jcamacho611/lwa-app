# LWA Canvas Connector Master Context

## Purpose

This document is the single context packet for Canvas, Windsurf, Codex, GitHub agents, and any builder working on LWA.

It explains what LWA is, where the project is, what exists, what must be preserved, what still needs to be built, and how to build safely without shrinking the vision or breaking the current repo.

Use this as the first document to read before making changes.

---

## One-line identity

LWA is an interactive creator universe where content, workflow, AI assistance, gameplay, opportunity discovery, marketplace systems, and monetization all live in one system.

It starts with AI content/video tools, but it is no longer just a clip tool.

---

## Clean public description

LWA is an Interactive Creator Universe that helps creators, builders, and digital earners create content, complete workflows, unlock opportunities, package campaigns, build identity, and turn attention into income.

---

## Internal product definition

LWA combines:

- Video OS
- Command Center
- Lee-Wuh AI guide / mascot / character system
- Director Brain intelligence
- Proof Vault + Style Memory
- Campaign Export Packager
- Opportunity / Money Missions
- Marketplace
- Wallet / economy layer
- Game world / realm / progression
- Company OS
- Integrations
- Admin/operator tooling

The core product path is:

```text
source → best clip → save proof → package campaign → unlock/export/pay → learn what works → next mission
```

---

## Naming rules

Use these names consistently:

```text
LWA = product, company, app, platform, frontend, backend, repo
Lee-Wuh = mascot, AI guide, council leader, in-world character, brand identity
Video OS = content/video generation and processing layer
Command Center = main operational workspace
Money Missions = opportunities, marketplace, campaigns, earning paths
Director Brain = scoring, ranking, recommendation, and learning intelligence
Proof Vault = saved proof, winning clips, rejected clips, evidence, portfolio memory
Style Memory = creator preferences, voice, hooks, captions, audience, niche
Realm / World = game/progression/identity layer
Company OS = business/team/agency layer
```

Do not rename LWA to Lee-Wuh.
Do not describe LWA as only a clip tool.
Do not bury the product under lore.

---

## Current repo checkpoint

Repo:

```text
jcamacho611/lwa-app
```

Primary frontend appears under:

```text
lwa-web/
```

Primary backend appears under:

```text
lwa-backend/app/
```

Known important commits/checkpoints:

```text
PR #143 — feat: add LWA Omega engine bundle and reliability hardening
Branch: feat/local-ffmpeg-renderer-v0
Status: draft/open/mergeable when created

commit a9d5e34 — feat: complete Issue #142 - backend routes + frontend command center wiring
commit ed0cd7b — docs: add Director Brain ML repo build spec
```

Known Issue:

```text
Issue #142 = autonomous coordination / council / build operating log
```

---

## What already exists or has been pushed in the trajectory

### Core

- public GitHub repo
- Next.js frontend
- FastAPI-style backend structure
- Railway-oriented deployment direction
- security and env handling docs/rules
- multiple validation passes reported: frontend type-check, Next.js build, backend compile

### Video / content layer

- Video OS direction
- render engine v0 direction
- ingest engine v0 direction
- source asset system
- Clip Studio / generate flow
- timeline/source panels
- batch review direction
- creative engines direction
- caption/audio/render/export trajectory

### Command Center

- Command Center route/panels trajectory
- 13-tab Command Center wiring reported
- panels reported for Character System, Game World, Marketplace, Campaign Export, Creative Engines, Video OS, Source Timeline, Batch Review

### Lee-Wuh identity layer

- Lee-Wuh mascot / hero / brand system direction
- Lee-Wuh character states direction
- Lee-Wuh app-wide guide requirement
- Blender / Rive / Spline / XR production specs direction
- approved character references from user uploads

### Game / world layer

- Realm / world direction
- character system direction
- game world backend/frontend route trajectory
- progression, XP, quests, identity, world zones direction

### Money / opportunity layer

- Opportunities / Money Missions direction
- marketplace direction
- campaign export direction
- jobs/opportunity engine direction
- wallet/economy/integrations direction
- Whop/checkout/paywall direction not fully locked yet

### Intelligence layer

- Director Brain ML repo build spec added
- Proof Vault + Style Memory spec created in conversation
- Feedback Learning Loop trajectory
- Lee-Wuh tool-control layer still needed

---

## Absolute safety rules

Always preserve existing work by default.

Do not remove, delete, replace, reset, or rewrite existing systems unless there is a clear defect, hard conflict, or explicit reason.

Do not break:

```text
/generate
existing backend contracts
existing routes
Command Center
Railway deploy assumptions
```

Do not touch:

```text
lwa-ios/
```

unless a task explicitly requires it.

Never commit:

```text
.env
secrets
tokens
private keys
model.pkl
vectorizer.pkl
.joblib
.onnx
.pt
.pth
.blend
.glb
.gltf
.fbx
.obj
.mp4
.mov
.zip
.psd
.wav
.aiff
```

Live paid providers must be disabled by default and env-gated.

Mock/metadata-only v0 is acceptable when it helps land safe product structure.

---

## Builder law

Every new product feature must complete this chain:

```text
service → route → frontend helper → UI panel/page → reachable navigation → validation
```

If a service exists but has no route, add the route.
If a route exists but has no helper, add the helper.
If a helper exists but has no UI, add UI.
If UI exists but is unreachable, wire navigation.
If feature exists only as docs, turn it into safe metadata-only v0 code when appropriate.

Do not stop at docs.
Do not stop at hero copy.
Do not stop at issue creation.
Do not stop at PR creation.
Do not create disconnected engines.

---

## Core loop to lock

The most important product loop is:

```text
1. User enters LWA
2. Lee-Wuh appears
3. User chooses Content Mission or Money Mission
4. User pastes/uploads source or picks opportunity
5. LWA produces a useful output/reward
6. Best result appears first
7. User saves proof or exports package
8. Unlock/pay path is clear
9. Style Memory / Director Brain learn from the action
10. User returns for next mission
```

This loop matters more than adding more panels.

---

## First Mission pattern

The user provided a canvas-safe First Mission example with mission states:

```text
home
content
money
```

Use it as product behavior, not as code to copy blindly.

The correct idea:

```text
Lee-Wuh asks: Content or money?
Content Mission → /generate
Money Mission → /opportunities
Command Center → /command-center
```

Implementation rule:

Do not create root `app/` files if the frontend lives in `lwa-web/`.
Do not replace the real generate flow with mock data.
Do not overwrite the homepage unless clearly safe.
Add first-mission surfaces additively.

Suggested safe files:

```text
lwa-web/app/first-mission/page.tsx
lwa-web/components/mission/FirstMissionChooser.tsx
lwa-web/components/mission/ContentMissionCard.tsx
lwa-web/components/mission/MoneyMissionCard.tsx
lwa-web/app/opportunities/page.tsx if missing
```

---

## Lee-Wuh live character system

Lee-Wuh must become more than a mascot or chatbot.

Lee-Wuh should be:

- always-present guide
- AI character
- app-state interpreter
- mission guide
- next-best-action recommender
- tool controller
- first game/world character
- future 3D/VR/avatar identity

Lee-Wuh should be able to trigger app actions safely:

```text
generate clips
score hooks
save proof
open opportunities
package campaigns
explain safety/cost warnings
navigate Command Center panels
summarize next move
```

Do not make Lee-Wuh block core UI.
Keep him useful and premium.

---

## Director Brain ML v0

A Director Brain ML spec is now in repo:

```text
docs/architecture/LWA_DIRECTOR_BRAIN_ML_REPO_BUILD_SPEC.md
```

Build it safely.

Do not copy random `/backend/ml/engine.py` paths blindly.
Use the real repo structure.

Expected backend files:

```text
lwa-backend/app/services/director_brain_ml.py
lwa-backend/app/api/routes/director_brain_ml.py
```

Expected routes:

```text
POST /api/v1/director-brain/score
POST /api/v1/director-brain/rank
POST /api/v1/director-brain/learn
GET  /api/v1/director-brain/status
```

Good content definition:

```text
engagement potential + conversion potential + viral hook strength + user preference + proof/history outcome
```

Start with deterministic heuristic scoring v0.
Do not require sklearn for v0.
Do not commit pickle/model artifacts.

---

## Proof Vault + Style Memory v0

LWA needs a memory layer so it learns what works.

Proof Vault should store:

- winning clips
- rejected clips
- approved hooks
- rejected hooks
- proof assets
- performance notes
- campaign evidence

Style Memory should store:

- brand voice
- caption preferences
- visual style preferences
- audience/niche notes
- offer/CTA notes
- platform performance notes
- Lee-Wuh recommendations

Suggested route groups:

```text
/api/v1/proof-vault/*
/api/v1/style-memory/*
```

Suggested panel:

```text
lwa-web/components/command-center/ProofVaultStyleMemoryPanel.tsx
```

This layer should feed Director Brain, Lee-Wuh, Campaign Export, Marketplace, and Feedback Learning.

---

## Missing connective systems council report

The hidden need is not more random engines.

LWA needs connective tissue:

1. Killer first-session loop
2. Source-of-truth product hierarchy
3. Rendered-first trust system
4. Runtime smoke testing
5. Entitlement/paywall truth
6. Persistent creator identity
7. Lee-Wuh tool-control layer
8. Data contract registry
9. Event tracking layer
10. Onboarding and empty-state system
11. Demo mode with sample source
12. Launch offer compression
13. Real export package
14. Admin/operator panel
15. Observability and failure recovery
16. Legal/safety/content-rights layer
17. Repository discipline

Priority order:

```text
1. Lock First Mission loop
2. Runtime smoke hardening
3. Proof Vault + Style Memory
4. Director Brain ML v0
5. Lee-Wuh tool control
6. Paid export/unlock truth
7. Demo mode
8. Event tracking
9. Admin/operator panel
10. Marketplace/game economy loops
```

---

## Rendered-first trust rule

Users must know what is real output and what is strategy.

Separate these states visually:

```text
Ready / playable / export-ready
Rendering / queued / processing
Strategy only / recommendation only / not rendered
Failed / retry available
Locked / upgrade to export
```

If strategy-only outputs look like finished clips, users will think the product is fake or broken.

---

## Paid unlock/export truth

LWA needs a real money path:

```text
free preview
locked full export
Whop or Stripe checkout
plan/entitlement check
credits or usage limits
premium unlock state
export package download or delivery
```

Export package should include more than clips:

- hooks
- captions
- timestamps
- thumbnail text
- CTAs
- platform notes
- posting order
- proof-save option
- campaign metadata

---

## Demo mode

LWA needs a reliable demo path that always works.

Add sample source / sample clip pack capability so a new user, investor, or Whop visitor can see the full loop without uploading anything.

Demo flow:

```text
Use sample source → generate sample clip pack → save proof → package campaign → show Style Memory update → show unlock/export
```

---

## Event tracking layer

Track events:

```text
generate_clicked
source_added
clip_generated
clip_saved
clip_rejected
hook_approved
hook_rejected
export_clicked
payment_started
payment_completed
opportunity_opened
campaign_packaged
style_memory_updated
lee_wuh_action_triggered
```

These events should feed:

- Director Brain
- Proof Vault
- Style Memory
- Feedback Learning Loop
- Admin/operator panel

---

## Admin/operator panel

LWA needs an operator surface for founder/admin use:

```text
users
runs
jobs
errors
costs
provider status
render status
failed jobs
retry buttons
mock/live flags
queue recovery
```

This keeps the company from flying blind.

---

## Runtime smoke hardening

Build passing is not enough.

For every backend route added:

```text
import module
register router
start backend if possible
hit endpoint
confirm JSON shape
confirm frontend helper path
confirm panel renders useful state
```

A route that compiles but fails at runtime is not complete.

---

## Frontend design direction

Use:

- black background
- purple aura
- gold accents
- white text where needed
- premium, creator-native, mythic but useful feeling

Do not clutter the product.
Do not hide the source input.
Do not make every button goofy.
Do not turn every screen into lore.

Lee-Wuh should guide at edges/corners/panels, not block workflows.

---

## Blender / 3D / XR direction

Lee-Wuh has approved reference images and should become a production-ready character later.

Repo should contain lightweight specs/scripts/docs only.
Do not commit heavy production assets.

Future character requirements:

- chibi final-boss creature
- jeweled dreadlocks
- black/gold/purple palette
- African + Japanese fusion with streetwear
- expressive states
- rig-ready
- optional sword
- future GLB/Rive/Spline/XR compatibility

Production assets should live outside the repo unless optimized and explicitly approved.

---

## Validation commands

Before commit:

```bash
git status --short
git branch --show-current
git diff --stat
```

If backend touched:

```bash
python3 -m compileall lwa-backend/app
```

If frontend touched:

```bash
cd lwa-web
npm run type-check
npm run build
cd ..
```

Always:

```bash
git diff --check
git status --short
```

Safety checks:

```bash
git status --short | grep -Ei "\.env|secret|token|key|credential|pem|p12|mobileprovision|provisionprofile" || true
git status --short | grep -Ei "\.pkl|\.joblib|\.onnx|\.pt|\.pth|\.blend|\.glb|\.gltf|\.mp4|\.mov|\.zip|\.psd|\.wav|\.aiff|\.obj|\.fbx" || true
git status --short | grep "lwa-ios" || true
```

---

## Autonomous builder prompt

Use this prompt in Canvas/Windsurf/Codex:

```text
Read docs/architecture/LWA_CANVAS_CONNECTOR_MASTER_CONTEXT.md first.

You are building LWA as an Interactive Creator Universe, not a clip tool.

Preserve all existing work by default.
Never remove anything unless necessary.
Preserve /generate.
Do not touch lwa-ios.
Do not commit secrets or heavy assets.
Keep paid/live providers disabled by default and env-gated.

Build missing connective systems, not disconnected engines.

Core loop to lock:
First Mission → Command Center → Generate → Best Clip → Save Proof → Campaign Export → Unlock/Pay → Style Memory update → Next Mission.

If a piece is missing, add it safely.
If a service exists without a route, add route.
If route exists without helper, add helper.
If helper exists without UI, add UI.
If UI exists but unreachable, wire it.
If docs exist without code and code is needed, build metadata-only v0.

Current priority order:
1. Lock First Mission loop
2. Runtime smoke hardening
3. Proof Vault + Style Memory
4. Director Brain ML v0
5. Lee-Wuh tool control
6. Paid export/unlock truth
7. Demo mode
8. Event tracking
9. Admin/operator panel
10. Marketplace/game economy loops

Validate before commit:
- backend compile if backend touched
- frontend type-check/build if frontend touched
- git diff --check
- secret/heavy/iOS checks

Commit and push coherent slices.
Continue building after each safe slice.
```

---

## Final truth

LWA already has the pieces of a large platform.

What it needs now is not more imagination.

It needs a clear, addictive, monetized loop that connects everything:

```text
create → prove → package → monetize → learn → return
```
