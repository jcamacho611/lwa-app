# LWA Backend Engine Completion Matrix

## Purpose

LWA should use as many backend engines/services as the product truly needs. The current repo is a monolithic backend with many internal product engines. This document tracks what exists, what is real, what is scaffolded, and what must be completed before launch.

## Engine 1 — Creator Engine

### Purpose
Turns source content into clips, hooks, captions, scores, rankings, render jobs, and exportable creator output.

### Existing areas
- `app/api/routes/generate.py`
- `app/api/routes/generation.py`
- `app/api/routes/clip_process.py`
- `app/api/routes/clip_status.py`
- `app/api/routes/clips.py`
- `app/api/routes/captions.py`
- `app/services/clip_service.py`
- `app/services/deterministic_clip_engine.py`
- `app/services/caption_engine.py`
- `app/services/hook_engine.py`
- `app/services/clip_ranking.py`
- `app/services/video_service.py`

### Current status
Started and functional in offline/no-API mode.

### Missing before launch
- persistent clip run storage verification
- rendered-video pipeline verification
- export bundle reliability
- frontend/history/proof connection audit
- full route tests

---

## Engine 2 — LWA Brain / Intelligence Engine

### Purpose
Owns the decision layer: scoring, provider routing, style memory, feedback learning, platform intelligence, campaign recommendations, and Lee-Wuh guidance.

### Existing areas
- `app/api/routes/director_brain_ml.py`
- `app/api/routes/intelligence_data.py`
- `app/api/routes/feedback_learning.py`
- `app/api/routes/style_memory.py`
- `app/services/director_brain.py`
- `app/services/director_brain_algorithm.py`
- `app/services/director_brain_ml.py`
- `app/services/provider_router.py`
- `app/services/intelligence_registry.py`
- `app/services/viral_intelligence.py`
- `app/services/learning_loop.py`

### Current status
Started. Some scaffolding and some real deterministic logic exist.

### Missing before launch
- one unified LWA Brain response contract
- provider fallback tests
- style memory persistence
- behavior-driven learning loop
- frontend explanation UI audit

---

## Engine 3 — Render / Asset / Visual Engine

### Purpose
Handles visual generation, Seedance, render jobs, Blender assets, GLB assets, video exports, and generated asset retention.

### Existing areas
- `app/api/routes/render_engine.py`
- `app/api/routes/seedance.py`
- `app/api/routes/visual_generation.py`
- `app/api/routes/video_jobs.py`
- `app/services/render_engine.py`
- `app/services/render_service.py`
- `app/services/render_queue.py`
- `app/services/render_job_store.py`
- `app/services/seedance_service.py`
- `app/services/visual_generation_service.py`
- `app/services/generated_asset_store.py`
- `app/services/asset_retention.py`
- `scripts/blender/`

### Current status
Started. Blender blockout and GLB exist for Lee-Wuh.

### Missing before launch
- render queue persistence
- provider gating
- cost limits
- asset lifecycle rules
- failure recovery
- user-facing render status

---

## Engine 4 — Marketplace / Campaign Engine

### Purpose
Turns generated content into jobs, campaigns, deliverables, opportunities, and marketplace activity.

### Existing areas
- `app/api/routes/marketplace.py`
- `app/api/routes/campaigns.py`
- `app/api/routes/campaign_export.py`
- `app/api/routes/opportunity_engine.py`
- `app/services/marketplace_core.py`
- `app/services/campaign_engine.py`
- `app/services/campaign_export_packager.py`
- `app/worlds/jobs/`

### Current status
Started, not production complete.

### Missing before launch
- real marketplace listing model
- creator submission flow
- campaign moderation
- admin review
- dispute/refund rules
- proof-to-campaign connection

---

## Engine 5 — Wallet / Entitlements / Money Engine

### Purpose
Controls access, credits, subscriptions, Whop/Stripe integrations, payout safety, ledgers, and monetization rules.

### Existing areas
- `app/api/routes/wallet.py`
- `app/api/routes/entitlements.py`
- `app/api/routes/whop_webhooks.py`
- `app/services/whop_service.py`
- `app/services/whop_entitlements.py`
- `app/services/entitlement_service.py`
- `app/worlds/ledger.py`
- `app/worlds/credits.py`
- `app/worlds/earnings.py`
- `app/worlds/stripe_connect.py`
- `app/worlds/whop.py`

### Current status
Started, but real payment/payout logic must be handled carefully.

### Missing before launch
- ledger source of truth
- credit spending rules
- entitlement tests
- payout locks
- legal review
- sandbox payment verification

---

## Engine 6 — Proof / History / Data Engine

### Purpose
Stores generated output, user behavior, proof events, audit trail, recovery, history, and long-term learning data.

### Existing areas
- `app/api/routes/proof_vault.py`
- `app/api/routes/proof_graph.py`
- `app/api/routes/events.py`
- `app/services/proof_events.py`
- `app/services/proof_core.py`
- `app/services/proof_graph.py`
- `app/services/event_log.py`
- `app/worlds/audit.py`

### Current status
Started.

### Missing before launch
- persistent storage confirmation
- complete event taxonomy
- proof/history UI connection
- recovery tests
- privacy/data retention rules

---

## Engine 7 — World / Game / Lee-Wuh Engine

### Purpose
Makes Lee-Wuh the living agent and connects quests, XP, relics, realms, game state, rewards, and the Signal Sprint game path.

### Existing areas
- `app/api/routes/game_world.py`
- `app/services/game_world_system.py`
- `app/services/signal_realms_core.py`
- `app/services/realms_catalog.py`
- `app/worlds/router.py`
- `app/worlds/quests.py`
- `app/worlds/xp.py`
- `app/worlds/relics.py`
- `app/worlds/ugc.py`
- `app/worlds/clipping/`
- `app/worlds/jobs/`

### Current status
Strong scaffold, not a full production game backend yet.

### Missing before launch
- real game loop persistence
- XP/reward ledger contract
- Lee-Wuh mission logic
- Godot integration plan implementation
- transparent reward rules
- no hidden mining behavior

---

## Engine 8 — Safety / Fraud / Compliance Engine

### Purpose
Prevents unsafe claims, fraud, bad marketplace jobs, payout abuse, risky crypto behavior, and illegal monetization flow.

### Existing areas
- `app/api/routes/safety.py`
- `app/worlds/safety.py`
- `app/worlds/fraud.py`
- `app/worlds/moderation.py`
- `app/worlds/rights.py`
- `app/worlds/gates.py`

### Current status
Started.

### Missing before launch
- claim-safety tests
- payout safety rules
- crypto/reward legal review
- marketplace moderation workflow
- user reporting flow

---

## Engine 9 — Social / Distribution Engine

### Purpose
Handles posting, social integrations, platform-specific packaging, export, and creator distribution.

### Existing areas
- `app/api/routes/posting.py`
- `app/services/social_integrations_core.py`
- `app/services/social_provider_catalog.py`
- `app/services/platform_signals.py`
- `app/services/platform_fit.py`
- `app/services/export_service.py`
- `app/services/export_bundle.py`

### Current status
Started.

### Missing before launch
- real OAuth/provider integrations
- posting queue
- platform error handling
- export reliability
- user permissions

---

## Engine 10 — Operator / Admin Engine

### Purpose
Gives the founder/admin team control over queues, moderation, campaigns, users, generated assets, jobs, and system health.

### Existing areas
- `app/api/routes/admin.py`
- `app/api/routes/command_center.py`
- `app/services/operator_dashboard_core.py`
- frontend `/command-center`
- frontend `/admin/marketplace`
- frontend `/admin/moderation`

### Current status
Started.

### Missing before launch
- real admin controls
- protected access
- queue inspection
- moderation actions
- metrics dashboard
- production monitoring

---

## Launch Rule

No engine is considered complete until it has:

1. API route or interface
2. service logic
3. storage/data model
4. frontend connection when relevant
5. validation/test coverage
6. fallback/error behavior
7. safety rules
8. deployment/env notes

## Current Architecture Decision

Keep LWA as one backend app for now with modular internal engines.

Split into separate deployable services only when one of these becomes true:

- security boundaries require it
- scaling requires it
- provider workloads require isolated queues
- payment/compliance requires isolation
- game backend requires separate realtime infrastructure
- render jobs require separate workers

