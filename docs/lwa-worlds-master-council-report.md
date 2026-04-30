# LWA Worlds — Master Council Report

**Status:** Strategic architecture and execution roadmap.  
**Compiled:** April 29, 2026.  
**Repository:** `jcamacho611/lwa-app`  
**Backend:** `lwa-backend-production-c9cc.up.railway.app`  
**Frontend:** `lwa-the-god-app-production.up.railway.app`

> This document is a planning, product, hiring, and Codex prompt pack for the LWA / IWA platform. It is intentionally stored under `docs/` so it does not change runtime behavior. Treat broad market, legal, pricing, API, compensation, and blockchain claims as items requiring fresh verification before investor, legal, or production use.

---

## Document Map

1. Phase 1: LWA Clipping Engine — Day 3 Sprint
2. Competitive Intelligence Matrix
3. Platform Signal Database
4. Marketplace Architecture
5. RPG / World System — The Signal Realms
6. Social API Integration Plan
7. Blockchain / NFT / Appchain Roadmap
8. Hiring Plan — Founding Council
9. Master Codex Prompt Stack
10. Council Executive Summary

`[ASSUMPTION]` marks reasoned inference, not verified fact. `FREE_LAUNCH_MODE` is the proposed public launch flag.

---

# Part 1 — Phase 1: LWA Clipping Engine

## Phase 1 Objective

The current MVP should be hardened before adding marketplace, RPG, blockchain, or social posting. The safest first move is to improve production reliability without changing the core product spine.

## What ships first

1. **FREE_LAUNCH_MODE** — an environment-driven flag that opens the app for public testing while keeping abuse controls.
2. **Fallback hardening** — every external dependency is wrapped so failures return degraded structured output instead of crashing the frontend.
3. **README polish** — a concise onboarding document for engineers and candidates.

## Day 3 Codex Prompt

```text
ROLE: You are a senior backend engineer working on the lwa-app monorepo.
TASK: Implement Day 3 of the Director Brain sprint in a single PR.
Never touch iOS, never add a native build target, and never introduce a new external service.

1. Add FREE_LAUNCH_MODE
   - Read os.getenv("FREE_LAUNCH_MODE", "false").lower() == "true" in backend config and expose settings.free_launch_mode.
   - When true, get_current_user() should return a synthetic GuestUser(id="guest", tier="free_launch") instead of returning 401 for unauthenticated public testing.
   - When true, rate limit anonymous traffic by IP at 30 requests/minute and skip paid entitlement checks.
   - Add a web banner component that renders only when NEXT_PUBLIC_FREE_LAUNCH_MODE === "true".

2. Fallback hardening
   - Wrap download, transcription, moment detection, and render steps with typed try/except handling.
   - Log structured fields: step, video_id, error_class, error_msg.
   - Return a typed degraded result object instead of raising out of the pipeline.
   - Add deterministic fallbacks for transcript windows, moment windows, captions, and hooks.

3. README polish
   - Include what it does, live URLs, local dev, required env vars, architecture diagram, API surface, and deploy notes.

4. Verification
   cd lwa-backend && python3 -m py_compile $(git ls-files '*.py')
   cd lwa-backend && python3 -m unittest discover
   cd lwa-web && npm run type-check
   cd lwa-web && npm run lint

OUTPUT: git diff and one-paragraph PR description.
```

## Phase 1 Railway Env Vars

| Var | Value | Service |
|---|---|---|
| `FREE_LAUNCH_MODE` | `true` | backend |
| `NEXT_PUBLIC_FREE_LAUNCH_MODE` | `true` | web |
| `OPENAI_API_KEY` | existing | backend |
| `ANTHROPIC_API_KEY` | existing | backend |
| `WHISPER_MODEL` | `small` | backend |
| `MAX_VIDEO_MINUTES` | `30` | backend |
| `RATE_LIMIT_GUEST_RPM` | `30` | backend |
| `DATABASE_URL` | Railway database, if enabled | backend |
| `REDIS_URL` | Railway Redis, if enabled | backend |
| `LOG_LEVEL` | `info` | backend |

---

# Part 2 — Competitive Intelligence Matrix

## Positioning

The clipping market is crowded. LWA should not position itself as only another long-form-to-short-form clipping tool. The stronger wedge is:

**AI clipping + operator dashboard + marketplace + progression layer + per-platform intelligence.**

## Competitor Summary

| Tool | Known category | LWA wedge |
|---|---|---|
| OpusClip | AI clipping/category leader | Per-platform Director Brain, transparent credit ledger, marketplace layer |
| Vizard | Long upload clipping, captions, brand kit | Override and re-rank moments; marketplace for creative assets |
| Munch | Trend-aware clipping | Transparent trend sources and platform-specific scoring |
| Descript | Transcript-first editor | Short-form-native workflow instead of full editor competition |
| Captions.ai | Mobile-native capture/edit/caption | Web-first automation and operator flow |
| CapCut | Template-heavy manual editor | Bulk repurposing and operator workflows |
| Submagic | Caption styling and B-roll | Add marketplace, RPG, and Director Brain beyond captions |
| Klap | AI clipping/dubbing | Pair dubbing with marketplace and operator dashboard |
| Veed.io | Browser video editor | Avoid editor depth fight; focus on creator operations |
| Repurpose.io | Routing/automation | Own creation plus routing |

## Sales Objection Responses

- **“OpusClip already does this.”** LWA should answer: “OpusClip gives clips. LWA gives a director, platform strategy, packaging, and eventually marketplace distribution.”
- **“Cheaper tools exist.”** LWA should compete on operator value, not lowest price.
- **“I don’t trust crypto.”** Blockchain features must remain optional, cosmetic, and provenance-only.

---

# Part 3 — Platform Signal Database

## Platform Signal Draft

| Platform | Hook window | Primary signal draft | LWA action |
|---|---:|---|---|
| TikTok | 1–3s | Completion, rewatches, shares | Optimize first frame and retention loop |
| Instagram Reels | ~2s | Sends/DM shares, watch time, saves | Package for shareability and clean captions |
| YouTube Shorts | ~1s | Viewed vs swiped, engaged views, retention | Strong cold open and title keywords |
| LinkedIn | ~3s | Dwell, comment quality, saves | Professional hook and no external-link dependency |
| Facebook Reels | ~3s | Watch time and shares | Clear visual context and broad captions |
| X video | ~2s | Replies/reposts | Opinionated hook and debate angle |
| Twitch clips | ~3s | Clip velocity and context | Open on in-action moment |
| Whop/community | ~3s | Completion, retention, comments | Education/community packaging |

## Hook Formula Library

Use these formulas as prompt-pack seeds:

1. Contrarian claim
2. Named-persona callout
3. Dollar amount, with truthful disclosure
4. Pattern interrupt
5. Numbered-list promise
6. Time compression
7. Reverse hook
8. Named enemy
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
20. Dataset hook

## Caption Style Presets

| Preset | Use |
|---|---|
| `crimson_pulse` | sales, finance, debate |
| `clean_op` | education, B2B, coaching |
| `karaoke_neon` | gaming, music, entertainment |
| `signal_low` | podcasts/talking heads |
| `bigframe` | cinematic/personal brand |
| `medspa_safe` | regulated beauty/health/finance-safe phrasing |
| `dev_brutal` | AI/tech/dev demos |

---

# Part 4 — Marketplace Architecture

## Marketplace V1 Decision

Stripe Connect Express should be the first marketplace payment rail. Whop integration should be a separate later PR. Keep the marketplace out of Phase 1 hardening.

## Core Backend Concepts

- `users`
- `seller_accounts`
- `products`
- `product_assets`
- `orders`
- `payouts`
- `disputes`
- `ledger_entries`
- `webhook_events`

## Marketplace Routes

```text
POST   /sellers/onboard
GET    /sellers/me
POST   /products
PATCH  /products/{id}
GET    /products/{id}
GET    /marketplace
POST   /orders
GET    /orders/{id}
POST   /webhooks/stripe
POST   /disputes
GET    /sellers/{id}/payouts
POST   /admin/takedown
```

## Marketplace Safety Requirements

- Money stored as integer cents only.
- Webhooks idempotent via `webhook_events.id`.
- Append-only ledger is source of truth.
- Seller payout state machine must support holds, refunds, disputes, failures, and reversals.
- UI must include earnings disclaimers and banned-category guardrails.

---

# Part 5 — RPG / World System: The Signal Realms

## Premise

The Signal Realms is the LWA progression layer. Creators are “Signalbearers” with classes, factions, quests, badges, and relics. This should be retention and identity, not pay-to-win.

## Classes

Hookwright, Captioneer, Reframer, Trendseer, Loremaster, Voicewright, Ironforger, Pricer, Auditor, Diplomat, Cartographer, Oracle.

## Factions

Crimson Court, Black Loom, Verdant Pact, Iron Choir, Saffron Wake, Glass Synod, Tide Marshal, Driftborn, Emberkin, Chorus of Thoth, House Polis, Outer Signal.

## Rules

- XP comes from real creator outcomes.
- XP cannot be purchased.
- Relics are cosmetic only.
- Badges confer no monetary rights.
- Blockchain migration, if any, must be exportable from Postgres.

---

# Part 6 — Social API Integration Plan

## Build Order

1. YouTube read integrations
2. Twitch read/clip integrations
3. Polymarket public trend reads, with no betting UX
4. Reddit/Google Trends trend reads where allowed
5. TikTok Login Kit sandbox
6. Instagram sandbox/dev flow
7. TikTok/Instagram publishing only after approval

## Token Security

Social tokens must be encrypted at rest. Add one provider adapter per API and a shared integration-links table.

---

# Part 7 — Blockchain / NFT / Appchain Roadmap

## Guiding Rule

No blockchain feature should be required for core app usage. No item should imply ROI, yield, ownership of revenue, securities value, or feature unlocks.

## Phases

| Phase | Ship |
|---|---|
| 0 | Off-chain Postgres ledger |
| 1 | Optional proof-of-creation Merkle root dry run |
| 2 | Optional mainnet badges, if legally approved |
| 3 | Cosmetic relics only |
| 4 | Appchain decision only after scale forces it |

---

# Part 8 — Hiring Plan

## Founding Council Roles

1. Founder / CEO — High Director of the Signal
2. Founding Product Architect — Architect of Realms
3. Principal Full-Stack Engineer — Hand of the Director
4. AI / Media Pipeline Engineer — Forgemaster of Signals
5. Game Systems Designer — Loremaster of the Realms
6. Marketplace Operations Lead — Auditor of the Glass Synod
7. UI/UX Product Designer — Veilwright
8. Blockchain / Economy Engineer — Sigilbearer
9. Legal / Compliance Advisor — Keeper of the Charter

## Human-Required Areas

- Legal/compliance
- Marketplace trust and safety
- Smart contract audit
- RPG economy balancing
- Final design taste
- Sales, fundraising, and partnership relationships

---

# Part 9 — Master Codex Prompt Stack

## Immediate Prompt Order

1. Day 3 hardening
2. Fallback result typing
3. Director Brain v0
4. Webhook idempotency
5. Rate limit middleware
6. Marketplace MVP scaffolding
7. Whop integration
8. Dispute UI
9. Payout cron
10. Hook rewriter
11. Caption renderer
12. Realms scaffolding
13. XP awarder hooks
14. Quest engine
15. OAuth shell
16. Polymarket ingestor
17. Off-chain issuance
18. Daily Merkle dry run
19. Operator dashboard
20. Trust and Safety review queue

**Important:** Do not paste all 20 prompts into Codex at once. Execute one narrow PR at a time.

---

# Part 10 — Council Executive Summary

## Product Truth

LWA should become the operator layer around AI clipping. The clipper is the wedge. The moat is the marketplace, Realms identity, per-platform intelligence, and operator dashboard.

## Top Backend Requirements

1. FastAPI + simple deploy spine
2. No microservices until forced by scale
3. Structured fallback behavior
4. Idempotent webhooks
5. Integer money math
6. Append-only ledger
7. Token encryption
8. Redis-backed rate limits
9. Evidence-hash XP awarder
10. Structured logs and request IDs

## Top Frontend Requirements

1. Dark premium operator aesthetic
2. Simple source-first clipping flow
3. Rendered-first results
4. Strategy-only lane clearly separated
5. Realms pages later, not Phase 1
6. Marketplace pages later, not Phase 1
7. Earnings disclaimers where monetization appears
8. Optional wallet display only
9. Type checking before PRs
10. No iOS scope in Phase 1

## 30-Day Build Plan

| Week | Deliverable |
|---|---|
| 1 | Day 3 hardening + Director Brain v0 |
| 2 | Marketplace scaffolding + design system |
| 3 | XP/quest design + caption/hook systems |
| 4 | Stripe Connect sandbox + public free-launch testing |

## Critical Mistakes To Avoid

- Do not let roadmap docs become active implementation scope.
- Do not promise guaranteed earnings.
- Do not build crypto before product-market signal.
- Do not build iOS during Phase 1 hardening.
- Do not skip webhooks, ledger, fallback tests, or rate limits.
- Do not paste the whole report into Codex at once.

---

## Implementation Note

This document is the repo-safe version of the LWA Worlds Master Council Report. The full source draft was provided in chat/uploaded markdown and should be used as strategic source material. The audited implementation order is captured in `docs/lwa-worlds-master-council-audit.md`.

**Cosmetic items only. Earnings vary. No guarantee of income. Not legal, financial, or investment advice. Blockchain features are optional and provenance-only. Web-first; iOS is out of scope for Phase 1.**
