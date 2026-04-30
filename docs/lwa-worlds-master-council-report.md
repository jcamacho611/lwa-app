# LWA Worlds — Master Council Report

**Status:** mandatory execution source for LWA / IWA / LWA Worlds.

**Compiled:** April 29, 2026  
**Founder:** Justin "Big Daddy Macho" Camacho  
**Repository:** `jcamacho611/lwa-app`  
**Backend:** `lwa-backend-production-c9cc.up.railway.app`  
**Frontend:** `lwa-the-god-app-production.up.railway.app`

This document consolidates the uploaded Master Council Report into the repo as an execution source. It is not optional brainstorming. It is the product, technical, hiring, and Codex command plan for LWA Worlds.

Codex must use this report together with:

- `docs/lwa-worlds-mandatory-doctrine.md`
- `docs/company/lwa-codex-execution-ledger.md`
- `docs/company/lwa-autonomous-codex-execution-brief.md`
- Claude doctrine/spec/code docs when provided

## Document Map

1. Phase 1: LWA Clipping Engine Day 3 Sprint
2. Competitive Intelligence Matrix
3. Platform Signal Database
4. Marketplace Architecture
5. RPG / World System: The Signal Realms
6. Social API Integration Plan
7. Blockchain / NFT / Appchain Roadmap
8. Hiring Plan
9. Master Codex Prompt Stack
10. Council Executive Summary

---

# Part 1 — Phase 1: LWA Clipping Engine Day 3 Sprint

## What ships in Phase 1

The MVP running on Railway covers ingest, transcribe, moment detection, cut, caption, score, and 9:16 export. Day 3 hardens the production surface instead of adding disconnected features.

Required deliverables:

1. `FREE_LAUNCH_MODE`
   - Single env-driven flag.
   - Opens app with no paywall/auth gate.
   - Keeps abuse prevention via IP cap.
   - Allows Justin to post the public link without breaking production.

2. Fallback hardening
   - Every external call must be wrapped.
   - Covers yt-dlp, Whisper, OpenAI, Anthropic, ffmpeg, and render/export.
   - Typed fallback response.
   - Deterministic degraded output.
   - Never 500 the frontend for recoverable provider/source failures.

3. README polish
   - Clear engineer-facing repo entry point.
   - Live URLs.
   - Local dev.
   - Required env vars.
   - Architecture diagram.
   - API examples.
   - Railway deploy notes.

## Required Day 3 implementation intent

Codex must adapt this to the actual repo paths. The report uses examples like `apps/backend` and `apps/web`, but this repo may use `lwa-backend` and `lwa-web`. Codex must inspect first and adapt rather than blindly pasting paths.

### FREE_LAUNCH_MODE requirements

- Backend env: `FREE_LAUNCH_MODE=true|false`
- Frontend env: `NEXT_PUBLIC_FREE_LAUNCH_MODE=true|false`
- Backend setting exposed as `settings.free_launch_mode`
- Auth dependencies must support synthetic guest/free-launch user when enabled.
- Anonymous traffic must remain capped by IP.
- Paid checks must not block free launch use.
- Frontend banner: `FreeLaunchBanner` visible only when frontend flag is true.

### Fallback requirements

Add/adapt fallback service with deterministic behavior:

- transcript fallback: split source timeline into 30s windows labeled `Segment N`
- moment fallback: pick three evenly spaced 30s windows
- caption fallback: transcript text verbatim
- hook fallback: first seven words of segment
- provider/source/render failures return degraded result instead of raw error leak
- log structured error context: step, request/source id, error class, sanitized error message

### Verification checklist

- backend compile passes
- backend tests pass
- frontend type-check passes
- frontend lint/build pass where available
- bad URL returns degraded response or clean source fallback, not raw 500
- repeated anonymous usage triggers rate limit eventually
- banner renders when enabled
- invalid Anthropic/OpenAI keys do not destroy the whole user flow

### Railway env vars

- `FREE_LAUNCH_MODE=true`
- `NEXT_PUBLIC_FREE_LAUNCH_MODE=true`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `WHISPER_MODEL=small`
- `MAX_VIDEO_MINUTES=30`
- `RATE_LIMIT_GUEST_RPM=30`
- `DATABASE_URL`
- `REDIS_URL`
- `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET` if rendered storage is enabled
- `LOG_LEVEL=info`
- `SENTRY_DSN` optional

---

# Part 2 — Competitive Intelligence Matrix

## Market structure

The clipping market is crowded. The wedge is not “another clipper.” LWA must become the only platform combining:

- clipping engine
- creator marketplace
- progression/RPG identity
- multi-platform algorithm intelligence
- operator dashboard

## Competitor positioning

### OpusClip

Known wedge:

- Strong category recognition.
- Virality scoring.
- Clip generation.

LWA response:

- “OpusClip gives you a number. LWA gives you a director.”
- Per-platform intelligence instead of one global virality score.
- Transparent ledger.
- API/automation for operators.
- Marketplace and progression moat.

### Vizard / Klap / Munch

LWA response:

- Director Brain reranks and explains clips.
- UGC marketplace adds supply and monetization.
- Trend signal becomes explicit, not black box.

### Descript / Captions.ai

LWA response:

- Web-first, automation-first.
- Short-form-native instead of transcript-editor-first.
- No iOS dependency in MVP.

### CapCut / Submagic

LWA response:

- LWA is not a manual editor. It is an operator platform.
- Caption styles are necessary but not enough.
- Marketplace + Realms creates retention.

### Repurpose.io / Vidyo.ai

LWA response:

- Routing plus content creation plus economy.

## Sales objection responses

- “OpusClip already does this.” → OpusClip does step 1. LWA does clipping, packaging, marketplace, identity, and earnings flow.
- “Cheaper tools exist.” → LWA is built around operator workflow, per-platform intelligence, API/economy, and marketplace—not simple minutes.
- “I trust one virality score.” → TikTok, Reels, Shorts, LinkedIn, Twitch, and Whop rank different signals. LWA scores per platform.
- “Crypto worries me.” → Core product does not require wallet/crypto. Blockchain is optional proof/cosmetic layer later.

## Competitor-resistant features

1. Director Brain
2. Signal Realms RPG layer
3. Marketplace
4. Polymarket-backed trend signal as read-only cultural intelligence
5. Multi-account operator dashboard

---

# Part 3 — Platform Signal Database

## Per-platform ranking signals

### TikTok

- Optimal: 7–60s entertainment, 15–90s education
- Hook: first 1–3s
- Ranking: completion, shares, saves, comments, likes, rewatches
- Captions: original burned-in preferred
- Hashtags: 3–5 specific

### Instagram Reels

- Optimal: 15–60s, longer eligible where platform supports
- Hook: first 2s
- Ranking: DM shares, watch time, saves
- TikTok watermark penalized
- Hashtags: 3–5

### YouTube Shorts

- Optimal: 15–60s
- Hook: first second
- Ranking: engaged views, rewatches, swipe-away ratio
- Title keywords matter heavily

### YouTube long-form

- Optimal: 8–15 minutes for new channels
- Ranking: CTR, average view duration, satisfaction, session watch time

### LinkedIn video

- Optimal: under 90s vertical/native
- Hook: first 3s
- Ranking: dwell time, comment depth, saves, DM shares
- External links reduce reach
- Hashtags: 3 max

### Facebook Reels

- Optimal: 15–60s
- Ranking: watch time, shares, completion

### X / Twitter video

- Optimal: under 2:20
- Ranking: replies, reposts, likes, premium amplification

### Twitch clips

- Optimal: 5–60s
- Ranking: clip view velocity, channel traffic

### Whop / community

- Optimal: course chapters 4–10 minutes, posts under 90s
- Ranking: completion, day-7 retention, comments, member-share rate

## Category modifiers

- Podcast: open mid-sentence on punchline, quotability and DM shares
- Gaming: first frame in action, rewatches and velocity
- Finance: show specific number early, saves/comments
- Coaching: pain point within 2s, saves/DM shares
- Beauty: visual transformation first, saves
- Medspa: before/after first frame, no medical-claim language
- Music: drop/hook audio first, replays/creates
- Sports: highlight first, shares
- Education: curiosity gap, saves
- Debate/commentary: strong claim, comments/replies
- Reaction: face + context first
- Product demo: use-case first
- AI/tech: output demo first
- Local business: location/offer early

## Hook formula library

Codex must convert these into prompt templates/eval fixtures:

1. Contrarian claim
2. Named-persona callout
3. Dollar amount, only if true/disclosed
4. Pattern interrupt
5. Numbered list promise
6. Time compression
7. Reverse hook
8. Named enemy/comparison
9. Specific name-drop
10. Before/after
11. Unfinished number
12. Unexpected admission
13. Framework name
14. Implied secret
15. CTA-shaped hook
16. Objection-first hook
17. Paradox
18. Dialogue cold-open
19. Counter-trend
20. Dataset/pattern hook

## Caption presets

1. `crimson_pulse`
2. `clean_op`
3. `karaoke_neon`
4. `signal_low`
5. `bigframe`
6. `medspa_safe`
7. `dev_brutal`

Codex must implement them first as structured overlay specs before pixel-perfect rendering.

---

# Part 4 — Marketplace Architecture

## Core decisions

- Stripe Connect Express is primary rail for marketplace v1.
- Whop is secondary/community/membership rail.
- Marketplace supports clip templates, hook packs, B-roll bundles, caption presets, brand kits, prompt packs, clip commission products.
- Platform take rate target: configurable, default around 10%.
- Payouts: pending, held, approved, scheduled, in_transit, paid, failed, reversed/refunded/disputed.
- No guaranteed income language.

## Data areas

Codex must adapt schemas to actual repo persistence. If Postgres/SQLAlchemy/Alembic exists, use migrations. If the repo currently uses JSON stores or a platform store, scaffold with that pattern first and document migration path.

Required areas:

- users
- seller accounts
- products
- product assets
- orders
- payouts
- disputes
- ledger entries
- webhook events

## Required backend routes

- `POST /sellers/onboard`
- `GET /sellers/me`
- `POST /products`
- `PATCH /products/{id}`
- `GET /products/{id}`
- `GET /marketplace`
- `POST /orders`
- `GET /orders/{id}`
- `POST /webhooks/stripe`
- `POST /webhooks/whop`
- `POST /disputes`
- `GET /sellers/{id}/payouts`
- `POST /payouts/{id}/instant`
- `POST /admin/takedown`

For first implementation, real payout movement must be feature-flagged/disabled until verification, keys, webhook signatures, refund/dispute logic, and ops/legal copy exist.

## Frontend routes

- `/marketplace`
- `/marketplace/[id]`
- `/sell/onboard`
- `/sell/products`
- `/sell/products/new`
- `/disputes/new`
- `/disputes/[id]`
- `/admin/disputes`

## Legal and fraud requirements

Marketplace UI must include:

- “Earnings vary. No guarantee of income.”
- FTC disclosure fields where relevant.
- refund policy per listing
- banned categories list
- rights/ownership acknowledgement
- review/moderation state
- KYC requirement before live public listing where payouts are enabled

Fraud requirements:

- first-sale payout hold
- velocity checks
- webhook idempotency
- asset checksums
- preview watermarking later
- manual review for high-risk sellers/listings

---

# Part 5 — RPG / World System: The Signal Realms

## Premise

Creators are Signalbearers who channel attention through noise. The realm is divided into factions and classes. Progression is tied to real app actions, not purchased XP.

## Classes

- Hookwright
- Captioneer
- Reframer
- Trendseer
- Loremaster
- Voicewright
- Ironforger
- Pricer
- Auditor
- Diplomat
- Cartographer
- Oracle

## Factions

- Crimson Court
- Black Loom
- Verdant Pact
- Iron Choir
- Saffron Wake
- Glass Synod
- Tide Marshal
- Driftborn
- Emberkin
- Chorus of Thoth
- House Polis
- Outer Signal

## XP model

- Per skill, not only global.
- XP from realized outcomes.
- Never pay-to-win.
- XP cannot be purchased.
- Evidence hash/idempotency required.

Formula:

```text
xp_to_next(level n) = floor(100 * 1.12^(n-1))
total_xp(level n) = sum_{k=1..n-1} xp_to_next(k)
```

## Quest categories

- Onboarding
- Marketplace
- Director Brain
- Mastery
- Civic
- Frontier

Initial quest names include:

- First Signal
- Voice of the Realm
- The Hook is Mightier
- Caption Cantata
- Frame Discipline
- Multitongue
- Cross the Veil
- The Patron's Mark
- The Glass Eye
- The Naming Ceremony
- List the First Stone
- Patron Found
- Honest Coin
- The Watermark Vow
- The Tally
- The Tenfold Patron
- The Auditor's Nod
- The Refund Returned
- The Bundle
- The Hundred
- The Director's Whisper
- Per-Platform Voice
- The Trend Reading
- The Polymarket Glance
- The Reddit Pulse
- The Algorithm Pact
- The DM Whisper
- The Depth Score
- The Engaged View
- The Director's Crown

## Badge/relic model

- Badges are soulbound/earned only.
- Relics are cosmetic/tradeable later.
- No app feature unlocks from relics.
- No monetary rights from badges.
- Phase 1 is off-chain only.

## Required routes

- `POST /characters/me`
- `GET /characters/me`
- `POST /quests/{code}/claim`
- `GET /badges/me`
- `GET /relics/me`
- `GET /leaderboards/{skill}`

Frontend:

- `/realm`
- `/realm/character`
- `/realm/quests`
- `/realm/badges`
- `/realm/relics`
- `/realm/leaderboards/[skill]`

---

# Part 6 — Social API Integration Plan

## Providers

- YouTube Data API v3
- TikTok for Developers
- Instagram Graph API
- Twitch Helix
- Polymarket Gamma API
- Reddit API
- Google Trends / pytrends or provider later

## Build sequence

Build now:

- YouTube read shell
- Twitch read/clip shell
- Polymarket read-only trend ingestor
- Reddit/Google Trends controlled read/scaffold
- TikTok Login Kit/sandbox shell
- Instagram sandbox/dev shell

Build later after review:

- YouTube upload
- TikTok direct post
- Instagram publish
- commercial Reddit scale

## Polymarket constraints

- Read-only public cultural signal.
- No trading.
- No betting.
- No recommendation to wager.
- Label as cultural-attention research only.

## Required tables/areas

- integration links
- encrypted access/refresh tokens
- integration status
- trend signals
- trend taxonomy

## Required routes

- `POST /integrations/{provider}/start`
- `GET /integrations/{provider}/callback`
- `GET /integrations/me`
- `DELETE /integrations/{provider}`

## Trend worker

- Polymarket every 10 minutes
- Reddit hot configured subs every 15 minutes
- normalize tags
- store scores 0..1

---

# Part 7 — Blockchain / NFT / Appchain Roadmap

## Principle

In MVP and through Phase 5, blockchain features are optional cosmetics or proof-of-creation only.

No investment framing. No feature unlocks. No tokens. No staking. No yield. No fractionalization.

## Phase plan

0. Off-chain ledger only
1. Testnet proof-of-creation via daily Merkle roots
2. Mainnet soulbound badges later
3. Cosmetic ERC-1155 relics later
4. Appchain decision much later

## Required placeholder service

Add/adapt issuance abstraction when Realms foundation exists:

- `issue_badge(character_id, badge_code, evidence)`
- `issue_relic(character_id, relic_code, qty=1)`
- `get_proof(character_id)`
- deterministic hashable issuance records
- daily Merkle root JSON snapshot

Frontend proof tab:

- off-chain proof
- provenance only
- cosmetic only
- no investment value

---

# Part 8 — Hiring Plan

## Founding council roles

1. Founder / CEO — High Director of the Signal
2. Founding Product Architect / Creative Technical Director — Architect of Realms
3. Principal Full-Stack Engineer — Hand of the Director
4. AI / Media Pipeline Engineer — Forgemaster of Signals
5. Game Systems Designer — Loremaster of the Realms
6. Marketplace Operations Lead — Auditor of the Glass Synod
7. UI/UX Product Designer — Veilwright
8. Blockchain / Economy Engineer — Sigilbearer
9. Legal / Compliance Advisor — Keeper of the Charter

## Required company ops docs

Codex must create/maintain:

- `docs/company/lwa-elite-recruitment-and-mvo-system.md`
- `docs/company/lwa-creator-tester-program.md`
- `docs/company/lwa-sales-closer-program.md`
- `docs/company/lwa-advisor-partner-investor-system.md`
- `docs/company/lwa-support-the-build-mvo.md`
- `docs/company/lwa-recruitment-outreach-scripts.md`
- `docs/company/lwa-team-intake-forms.md`
- `docs/company/lwa-7-day-team-build-plan.md`

## Interview filters

Codex/team docs must include interview filters for:

- full-stack webhook/idempotency skill
- AI/media pipeline fallback thinking
- game systems/economy balance
- marketplace fraud/dispute handling
- premium UI taste
- blockchain/security/legal clarity

---

# Part 9 — Master Codex Prompt Stack

Codex prompt stack must be converted into tasks/issues and implemented in order.

## P1 — Clipping engine hardening

1. Day 3 sprint
2. typed fallback result and four-layer fallbacks
3. Director Brain v0
4. webhook idempotency framework
5. Redis/IP rate limit middleware

## P2 — Marketplace

6. marketplace MVP scaffold
7. Whop integration
8. dispute UI
9. payout state machine cron

## P3 — Director Brain and per-platform intelligence

10. per-platform hook rewriter
11. caption preset renderer

## P4 — RPG layer

12. Realms scaffold
13. XP awarder hooks
14. quest engine

## P5 — Social APIs

15. multi-provider OAuth shell
16. Polymarket trend ingestor

## P6 — Blockchain placeholder

17. issuance abstraction
18. daily Merkle anchor job

## P7 — Internal tools

19. operator multi-account dashboard
20. trust and safety review queue

---

# Part 10 — Council Executive Summary

## Top product insights

1. The clipper is the wedge; the operator platform is the business.
2. Per-platform intelligence is more defensible than one virality score.
3. Marketplace plus clipper creates network effects.
4. RPG progression is a retention moat.
5. `FREE_LAUNCH_MODE` buys early usage signal.
6. Polymarket trend signal is unique if kept read-only.
7. Web-first avoids App Store complexity in MVP.
8. Cosmetic-only proof assets are the durable chain posture.
9. Stripe Connect plus Whop gives payments optionality.
10. Operator dashboard is the long-term product center.

## Top backend requirements

1. FastAPI backend on current repo architecture.
2. No microservices until forced.
3. Money in cents only.
4. Webhooks idempotent via event ids.
5. Append-only ledger for balances.
6. Encrypted social tokens.
7. Fallback hardening everywhere.
8. Rate limiting by IP/user.
9. Idempotent XP awarder via evidence hash.
10. Structured logs and request IDs.

## Top frontend requirements

1. Next.js App Router in current repo structure.
2. Premium dark operator aesthetic.
3. Free launch banner.
4. Realms pages.
5. Earnings disclaimer on money pages.
6. Wallet optional only.
7. Operator dashboard.
8. Optimistic UI where appropriate.
9. Shared types if/when repo supports them.
10. Type-check and lint clean before PR.

## Sales opportunities

- agencies running 5–50 accounts
- podcast networks
- coaches and educators
- medspa/regulated verticals
- local business chains
- sports clip distributors
- music distributors
- Whop community owners
- streamers/Twitch creators
- AI/tech operators

## Mistakes to avoid

- per-minute pricing as core model
- guaranteed income claims
- NFT feature unlocks
- fractionalized relics
- premature iOS MVP
- missing webhook idempotency
- floats for money
- pay-for-XP
- single-provider AI lock-in
- Polymarket betting UX

## 30-day build plan

Week 1:

- Day 3 sprint
- Director Brain v0

Week 2:

- marketplace MVP scaffold
- premium dark design/Realms moodboard

Week 3:

- XP curves/classes/factions/quests
- caption presets and hook library

Week 4:

- Stripe Connect sandbox
- public `FREE_LAUNCH_MODE` link and first 100 users

## 90-day roadmap

Days 1–30:

- Phase 1 hardening
- marketplace MVP
- Director Brain v0
- RPG scaffolding

Days 31–60:

- Whop integration
- disputes
- quest pass
- Twitch/YouTube read integrations
- Polymarket ingestor

Days 61–90:

- TikTok/Instagram review prep
- operator dashboard
- off-chain proof anchoring
- first paying-user push

## Implementation checklist

1. Confirm council/team structure.
2. Land Day 3 sprint.
3. Set free launch env vars.
4. Stand up Director Brain v0.
5. Ship Realms aesthetic.
6. Stripe Connect sandbox.
7. Finalize quests/badges/relics.
8. Merge marketplace MVP.
9. Legal/ops docs.
10. Caption renderer and hook library.
11. Webhook idempotency.
12. Off-chain issuance abstraction.
13. Public launch link.
14. Trust/safety review queue.
15. OAuth integrations.
16. Legal/privacy/refund posture.
17. Chain decision later.
18. Quarterly legal-safety review.

---

# Codex Execution Requirement

Codex must not treat this report as optional. It must:

1. read this file first
2. audit repo compatibility
3. preserve existing working clipping app
4. adapt paths to the actual repo
5. implement in ordered slices
6. scaffold blocked external systems behind flags
7. never ignore Claude code/specs
8. verify and commit scoped changes

## Next prompt

Use the prompt in `docs/company/lwa-autonomous-codex-execution-brief.md`, then proceed with the Master Council build order above.

---

**End.**

Cosmetic items only. Earnings vary. No guarantee of income. Not legal, financial, or investment advice. Blockchain features are optional and provenance-only. Product is web-first; iOS targets are out of scope in Phase 1.
