# LWA Worlds — Master Build Bible

## Purpose

This is the internal source-of-truth artifact for LWA / IWA.

It explains what exists now, what is planned, what must be built, what must not be promised, and how the system fits together.

## 1. Product Truth

LWA / IWA is a working AI content repurposing MVP, not just a mockup.

Current product truth must be verified against the repo before public claims, but the project direction is:

- public URL-based clipping and generation
- backend generation pipeline
- clip packs with hooks, captions, timestamps, scores, titles, and asset links
- Railway frontend/backend deployment direction
- upload and source handling work in progress
- revenue-intent and operator workflow planning

What LWA is not yet:

- not a full nonlinear video editor
- not guaranteed extraction from every platform URL
- not direct social posting yet
- not a full marketplace yet
- not a full Signal Realms RPG yet
- not a blockchain product yet
- not an iOS-first product in MVP

## 2. Company Vision

LWA Worlds expands from the AI clipping wedge into a full creator operating system:

1. AI long-form-to-short-form clipping
2. Director Brain per-platform intelligence
3. premium creator command center
4. creator marketplace
5. Signal Realms RPG progression
6. social API distribution and trend intelligence
7. optional proof-of-creation and cosmetic identity layer

## 3. Product Architecture

### Frontend

Path: `lwa-web`

Responsibilities:

- source input
- generation command center
- upload/public URL states
- clip pack review
- result cards
- export/packaging rail
- free launch banner when enabled
- future marketplace and Realms shells

### Backend

Path: `lwa-backend`

Responsibilities:

- source ingestion
- generation routes
- job routes
- upload routes
- entitlement/quota behavior
- AI/media pipeline
- event logging
- fallbacks
- future marketplace/social/Realms/proof APIs

### AI / Media Pipeline

Responsibilities:

- source extraction
- transcript/moment detection
- hook/caption generation
- scoring/ranking
- render/export flow
- graceful fallback when providers or extractors fail

### Marketplace

Future system around listings, templates, hooks, brand kits, caption packs, campaign work, reviews, disputes, and payout-readiness.

### Signal Realms

Future identity/retention system around classes, factions, XP, quests, badges, and cosmetic relics.

### Social Integrations

Future provider layer for YouTube, TikTok, Instagram, Twitch, Reddit, trend data, and approved publishing workflows.

### Proof / Provenance

Future optional off-chain-first provenance layer. No required wallet. No feature unlocks from cosmetic items.

## 4. Current Deployment

Repo:

- `jcamacho611/lwa-app`

Known deployment direction:

- frontend: `https://lwa-the-god-app-production.up.railway.app`
- backend: `https://lwa-backend-production-c9cc.up.railway.app`

Env categories:

- backend API keys
- AI provider keys
- upload/render storage paths
- entitlement/quota settings
- free launch flags
- social provider keys later
- payment provider keys later

## 5. Build Phases

### Phase 1 — Clipping hardening

- source contract
- free launch mode
- deterministic fallbacks
- README/Railway polish

### Phase 2 — Frontend rebuild

- premium command center
- upload-first UX
- best clip first
- strategy-only lane
- export/packaging rail

### Phase 3 — Director Brain

- per-platform prompts
- hook formulas
- caption presets
- model routing
- platform scoring explanations

### Phase 4 — Marketplace

- audit first
- dark scaffold
- seller/listing/admin shells
- verified webhooks before payment state
- disputes/refunds/review queue before payouts

### Phase 5 — Signal Realms

- static shell first
- class/faction/quest content
- event-based XP later
- no pay-to-win

### Phase 6 — Social APIs

- provider status shell
- OAuth shell
- token encryption
- no direct posting until approval

### Phase 7 — Optional proof/provenance

- off-chain dry run
- deterministic records
- proof JSON
- optional wallet later

## 6. Council Responsibilities

| Council title | Real role | Owns | Must prevent |
|---|---|---|---|
| High Director of the Signal | Founder / CEO | vision, money, launch, sales, investors | scattered priorities |
| Architect of Realms | Product architect | product architecture and roadmap | duplicate architecture |
| Hand of the Director | Principal full-stack engineer | backend, frontend, deployment, APIs | breaking working routes |
| Forgemaster of Signals | AI/media pipeline engineer | clipping, models, fallbacks, rendering | provider lock-in and brittle failures |
| Loremaster of the Realms | Game systems designer | XP, classes, factions, quests | pay-to-win systems |
| Auditor of the Glass Synod | Marketplace ops lead | disputes, refunds, review, payout readiness | unsafe money movement |
| Veilwright | UI/UX designer | premium command center | generic SaaS clutter |
| Sigilbearer | Proof/economy engineer | optional provenance, wallets later | feature-gated collectibles |
| Keeper of the Charter | Legal/compliance advisor | claims, terms, risk rules | guaranteed income or investment language |

## 7. Legal / Safety Rules

- no guaranteed income
- no guaranteed virality
- no investment language for badges, relics, or proof
- XP cannot be bought
- cosmetic items must not unlock core app functionality
- money values use integer cents
- webhooks must be idempotent
- social tokens must be encrypted before storage
- preserve existing work by default
- do not touch `lwa-ios` unless explicitly approved

## 8. Artifact Map

| Artifact | Purpose | Audience |
|---|---|---|
| Master Build Bible | source of truth | founder, team, Codex context |
| Codex Prompt Pack | engineering execution | Codex, engineers |
| Frontend Rebuild Artifact | UI/UX rebuild | frontend/design |
| Operations Playbook | launch execution | Maria/ops |
| Investor + Sales Artifact | outreach and demos | sales/investors |
| Hiring Council Artifact | recruiting | Justin/recruiters |
| Legal Safety Artifact | claim controls | ops/legal |

## 9. 30-Day Plan

### Week 1

- land Chunk 16 P0 hardening
- verify source contract
- finish free launch behavior
- wire fallbacks into pipeline

### Week 2

- Director Brain v0
- platform prompts
- hook formulas
- caption presets

### Week 3

- frontend generate flow polish
- premium command center shell
- monetization CTA polish

### Week 4

- marketplace compatibility audit
- Realms static shell
- launch checklist

## 10. Justin’s Operating Checklist

Daily:

- check PR status
- decide next safe slice
- keep sales copy honest
- push one execution lane forward

Weekly:

- review roadmap
- record demo clips
- update Maria/ops tasks
- update investor/sales material
- approve or reject PRs

## Source note

Derived from the Master Council Report uploaded in the project thread and the Chunk 15/16 repo work.
