# LWA Full Platform Page Blueprint

This document locks the corrected platform-level vision into the repo so Windsurf, Codex, and future engineers stop treating LWA as only a clip generator.

## Product truth

LWA is a creator operating system made of connected surfaces:

- Generate
- Dashboard
- Game / Realm
- Marketplace
- Campaigns
- Wallet
- Upload
- History

The clip engine is the core, but the full product is bigger than clipping.

---

## 1. `/generate` — Clip Generation Engine

### Job
Turn source content into ranked, packaged content output.

### Must show
- source input
- auto/manual platform selection
- generate button
- best clip first
- ranked clips
- strategy-only fallback clips
- hooks
- captions
- CTA
- thumbnail text
- copy/export actions

### Hard law
This route must always return usable output.

If no external AI or rendering works, the user still gets:

- at least 3 clips
- hooks
- captions
- post order
- packaging

---

## 2. `/dashboard` — Command Center

### Job
Tell the user what to do next.

### Must show
- welcome/status panel
- current best clip
- next action
- recent runs
- campaign status
- wallet/credits summary
- active missions

### User feeling
“I know exactly what to do next.”

---

## 3. `/game` or `/realm` — World / Progression System

### Job
Turn LWA into a living creator world, not a boring utility.

### Must show
- Lee-Wuh character/world presence
- creator level
- XP/progress meter
- missions
- achievements
- unlocks
- style memory
- proof vault progress

### Mission examples
- Generate first clip pack
- Copy first hook
- Export first bundle
- Complete first campaign
- Return for day two

### User feeling
“My creator journey is progressing.”

---

## 4. `/marketplace` — Money + Opportunity Layer

### Job
Let users discover ways to earn, sell, buy, or fulfill content work.

### Must show
- available campaign opportunities
- clip pack service offers
- creator service listings
- brand/campaign cards
- payout potential
- submission status

### Early version
Scaffold only:

- marketplace hero
- opportunity cards
- coming soon / beta CTA

### Future version
- creator profiles
- brand offers
- content bounties
- proof-based submissions

---

## 5. `/campaigns` — Campaign Operating System

### Job
Manage content campaigns from requirements to submission.

### Must show
- active campaigns
- required platforms
- deliverables
- due dates
- payout or value
- clip assignment status
- export/submission actions

### User feeling
“I can turn clips into campaign work.”

---

## 6. `/wallet` — Credits + Money State

### Job
Show user’s plan, credits, payouts, and money state.

### Must show
- current plan
- credits remaining
- run usage
- payout status
- ledger/history
- upgrade CTA

### Hard law
Never confuse users about whether they can run a job.

---

## 7. `/upload` — Content Ingestion

### Job
Let users bring raw material into LWA.

### Must show
- upload card
- supported file/source types
- public URL option
- prompt/text fallback
- upload history

### Future version
- camera roll
- Google Drive
- Dropbox
- direct files

---

## 8. `/history` — Proof + Past Runs

### Job
Let users revisit past outputs and build trust.

### Must show
- previous clip packs
- best clips
- exported/copy status
- campaign-linked outputs
- proof vault progress

### User feeling
“LWA remembers my work.”

---

## Navigation rules

Every page must link back to:

- Generate
- Dashboard
- Game/Realm
- Marketplace
- Campaigns
- Wallet
- Upload
- History

Navigation must not break existing routes.

---

## Windsurf prompt — Full Platform Scaffold

Paste into Windsurf after reliability fixes pass:

```text
You are expanding LWA from a clip generator into the full creator operating system.

Create or verify these Next.js routes:
- /generate
- /dashboard
- /game or /realm
- /marketplace
- /campaigns
- /wallet
- /upload
- /history

Rules:
- Do not break existing /generate.
- Do not touch lwa-ios.
- Do not delete existing components.
- Scaffold safely first.
- Each page must render without crashing.
- Reuse existing ClipStudio/page shell/components where possible.
- Add navigation links between the platform pages.
- Keep pages premium, creator-native, dark, mythic, and simple.
- Do not add external AI dependencies.
- Do not build marketplace payments yet.
- Do not build heavy game logic yet.

Each page must include:
1. Page title
2. One-line user promise
3. Primary next action
4. Status/coming-soon section if logic is not ready
5. Link back to Generate and Dashboard

After scaffolding, run:
- cd lwa-web && npm run lint
- cd lwa-web && npm run type-check
- cd lwa-web && npm run build

Return:
1. files created
2. files edited
3. routes added
4. verification results
5. recommended commit message

Commit only if all checks pass.

Recommended commit:
feat(web): scaffold full LWA platform routes
```

---

## Done condition

This phase is done when every required platform route exists and renders safely.

This is not the final build. This is the platform skeleton so the full vision has a real home in the repo.
