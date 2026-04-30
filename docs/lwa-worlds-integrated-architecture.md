# LWA Worlds Integrated Architecture

## Purpose

LWA Worlds is the long-range product architecture for extending the existing LWA clipping MVP into a unified creator-economy platform.

The existing clipping app remains the foundation. This document does **not** replace the current source-ingest, generation, frontend, backend, iOS, Railway, or Whop work. It defines the build direction so future marketplace, UGC, RPG, social intelligence, and blockchain/economy features are added safely and in sequence.

## Core Thesis

AI creates the media. Marketplace creates the money. UGC creates the supply. RPG progression creates identity and retention. Social intelligence creates relevance. Blockchain later creates proof.

## Non-Negotiable Safety Rules

- Preserve the existing clipping/generation flow.
- Add features in isolated slices.
- Do not touch `lwa-ios/` unless the task is explicitly iOS.
- Do not implement real crypto transactions in the MVP.
- Do not launch a token in the MVP.
- Do not implement staking, yield, gambling, betting, or Polymarket trading.
- Do not promise guaranteed earnings.
- Use `estimated earnings`, `pending approval`, `approved payout`, `paid`, `held`, `disputed`, and `refunded` states.
- Use original names, worlds, factions, characters, relics, and lore.
- Do not copy GTA, Roblox, Fortnite, RuneScape, Elden Ring, One Piece, Whop, OpusClip, Sony, Nintendo, Marvel, DC, or existing IP.
- Wallet, NFT, and blockchain features are future-facing, optional, and must receive legal/security review before launch.
- Users must own or have rights to submitted/uploaded content.
- Every money movement must be auditable.
- Every UGC flow must support moderation.
- Every payout flow must support dispute and fraud review.

## Platform Layers

1. **AI Clipping Engine**
   - Source ingest, uploads, transcription, moment detection, captions, render/export, clip scoring, packaging, recovery.

2. **Social Intelligence Engine**
   - YouTube, TikTok, Instagram, Twitch, Reddit/news/trend data, and Polymarket trend-only intelligence.
   - Used for content strategy, not trading or betting.

3. **Marketplace Engine**
   - Buyers post clipping/content jobs.
   - Clippers/editors/creators submit work.
   - Buyers/admins approve, reject, or request revision.
   - Earnings remain estimated/pending until approved and payable.

4. **UGC Engine**
   - Users create templates, hook packs, caption packs, prompt packs, quests, cosmetics, campaign formats, and world concepts.
   - UGC must have review/moderation status before selling or public exposure.

5. **RPG Progression Engine**
   - Users have profile identity, class, faction, XP, skills, badges, relics, titles, and quest progress.
   - Real app actions unlock progression.

6. **Internal Economy Ledger**
   - Tracks credits, generation usage, XP, reputation, pending earnings, approved earnings, paid earnings, platform fees, holds, disputes, refunds, badges, relics, and wallet-placeholder events.

7. **Future Blockchain / LWA Chain Layer**
   - Starts as wallet/proof placeholders only.
   - Later may support proof-of-creation, proof-of-campaign-completion, non-investment collectibles, cosmetic relics, founder badges, and reputation proof.
   - Appchain/rollup work is later-stage only after users, revenue, legal review, and security audits.

8. **Admin / Moderation / Fraud Layer**
   - Admin reviews campaigns, submissions, UGC, payouts, disputes, fraud flags, content rights claims, abuse reports, integrations, and system health.

## First Integrated Vertical Slice

The first build that proves the whole system should be:

1. User generates a clip pack.
2. Best clip is shown first.
3. User creates a marketplace campaign/job from the clip pack.
4. Clipper/editor submits work.
5. Buyer/admin approves, rejects, or requests revision.
6. Pending earnings are created.
7. XP/reputation event is awarded.
8. Badge/relic is unlocked.
9. RPG profile updates.
10. Economy ledger records all events.
11. Wallet/economy page shows future-proof placeholder only.
12. Admin overview shows review/moderation/payout state.

## Product Routes To Add Over Time

### Core

- `/command-center`
- `/generate`
- `/history`
- `/pricing`
- `/account`
- `/billing`
- `/support`

### Marketplace

- `/marketplace`
- `/marketplace/post-job`
- `/marketplace/campaigns`
- `/marketplace/campaigns/[id]`
- `/marketplace/submit/[campaignId]`
- `/marketplace/templates`
- `/marketplace/templates/[id]`
- `/marketplace/seller`
- `/marketplace/clipper/apply`

### Earnings / Referrals

- `/earnings`
- `/earnings/pending`
- `/earnings/approved`
- `/earnings/payouts`
- `/referrals`
- `/referrals/dashboard`

### UGC

- `/ugc`
- `/ugc/create`
- `/ugc/assets`
- `/ugc/assets/[id]`
- `/ugc/quests`
- `/ugc/quests/create`
- `/ugc/world-builder`
- `/ugc/templates`

### Worlds / RPG

- `/worlds`
- `/worlds/profile`
- `/worlds/map`
- `/worlds/quests`
- `/worlds/factions`
- `/worlds/relics`
- `/worlds/classes`
- `/worlds/events`
- `/worlds/leaderboard`

### Economy / Future Chain

- `/economy`
- `/economy/ledger`
- `/economy/badges`
- `/economy/wallet`
- `/economy/collectibles`
- `/economy/lwa-chain`

### Integrations

- `/integrations`
- `/integrations/youtube`
- `/integrations/tiktok`
- `/integrations/instagram`
- `/integrations/twitch`
- `/integrations/polymarket`
- `/integrations/openai`
- `/integrations/anthropic`
- `/integrations/seedance`
- `/integrations/apple`

### Admin

- `/admin`
- `/admin/users`
- `/admin/jobs`
- `/admin/clips`
- `/admin/marketplace`
- `/admin/submissions`
- `/admin/payouts`
- `/admin/disputes`
- `/admin/moderation`
- `/admin/fraud`
- `/admin/integrations`
- `/admin/economy`
- `/admin/worlds`

## Backend Services To Add Over Time

- `auth_service`
- `user_service`
- `clip_generation_service`
- `transcription_service`
- `caption_render_service`
- `video_render_service`
- `social_intelligence_service`
- `marketplace_service`
- `campaign_service`
- `submission_service`
- `template_marketplace_service`
- `ugc_service`
- `quest_service`
- `reputation_service`
- `xp_service`
- `ledger_service`
- `wallet_service_placeholder`
- `badge_service`
- `payout_service`
- `affiliate_service`
- `admin_service`
- `moderation_service`
- `fraud_detection_service`
- `notification_service`
- `storage_service`
- `analytics_service`
- `integration_status_service`

## Database Areas

### User / Account

- `users`
- `user_profiles`
- `user_settings`
- `teams`
- `team_members`
- `roles`
- `permissions`
- `sessions`
- `api_keys`

### AI Clipping

- `source_videos`
- `clip_jobs`
- `clip_results`
- `clip_assets`
- `clip_transcripts`
- `clip_scores`
- `clip_packages`
- `caption_styles`
- `render_jobs`
- `render_failures`
- `generation_events`

### Marketplace

- `marketplace_profiles`
- `clipper_profiles`
- `buyer_profiles`
- `campaigns`
- `campaign_requirements`
- `campaign_assets`
- `campaign_submissions`
- `submission_reviews`
- `submission_revisions`
- `campaign_deliverables`
- `marketplace_orders`
- `marketplace_fees`
- `disputes`
- `ratings`
- `reviews`

### Earnings / Payouts

- `earnings_accounts`
- `earning_events`
- `pending_earnings`
- `approved_earnings`
- `payouts`
- `payout_methods`
- `payout_holds`
- `refunds`
- `chargebacks`
- `tax_profiles`
- `platform_fee_events`

### UGC

- `ugc_assets`
- `ugc_asset_versions`
- `ugc_asset_categories`
- `ugc_submissions`
- `ugc_reviews`
- `ugc_sales`
- `ugc_licenses`
- `ugc_reports`
- `ugc_moderation_events`
- `world_templates`
- `quest_templates`
- `cosmetic_assets`

### RPG / World

- `world_profiles`
- `avatar_profiles`
- `classes`
- `user_classes`
- `factions`
- `user_factions`
- `quests`
- `quest_steps`
- `quest_completions`
- `xp_events`
- `skill_tracks`
- `user_skills`
- `badges`
- `user_badges`
- `relics`
- `user_relics`
- `titles`
- `user_titles`
- `leaderboards`
- `world_events`

### Economy Ledger

- `internal_ledger_entries`
- `credit_balances`
- `credit_transactions`
- `reputation_events`
- `creator_reputation`
- `clipper_reputation`
- `marketplace_reputation`
- `wallet_connections`
- `collectible_placeholders`
- `chain_proof_placeholders`

### Integrations

- `api_integrations`
- `integration_tokens`
- `integration_status`
- `youtube_sources`
- `tiktok_sources`
- `instagram_sources`
- `twitch_sources`
- `polymarket_trends`
- `openai_usage_events`
- `anthropic_usage_events`
- `seedance_jobs`
- `apple_connect_events`

### Admin / Security

- `admin_actions`
- `audit_logs`
- `moderation_queue`
- `fraud_flags`
- `abuse_reports`
- `content_rights_claims`
- `dmca_requests`
- `security_events`
- `webhook_events`
- `system_health_events`

## Original RPG Direction

Working world name: **The Signal Realms**.

### Classes

- Signalwright
- Clipforger
- Trendseer
- Render Mage
- Campaign Hunter
- Relic Broker
- Loreblade
- Vault Runner
- Echo Smith
- Myth Editor
- Worldbinder
- Algorithm Knight

### Factions

- The Signalwrights
- The Clipforged
- The Gold Thread Guild
- The Void Editors
- The Renderborn
- The Mythstream Order
- The Echo Court
- The Relic Cartel
- The Campaign Houses
- The Black Frame Syndicate
- The Algorithm Priests
- The Vault Runners
- The Aether Court
- The Proofbound

### Skill Tracks

- Clipping
- Captioning
- Trendseeing
- Rendering
- Campaign Craft
- UGC Building
- Lore Craft
- Marketplace Trade
- Reputation
- Social Distribution
- Worldbuilding
- Relic Forging
- Signal Reading
- Audience Alchemy

### Quest Examples

- Generate first clip pack
- Submit first marketplace clip
- Complete first campaign
- Sell first template
- Create first UGC quest
- Refer first creator
- Unlock first badge
- Join first faction
- Reach 1,000 XP
- Earn first approved payout

## Implementation Phases

### Phase 1 — Source and Clip Engine Hardening

- Keep source POC runner active.
- Harden upload/source format support.
- Improve public URL fallback messaging.
- Validate upload media types.
- Preserve existing generation flow.

### Phase 2 — Marketplace Skeleton

- Add marketplace landing/page shell.
- Add campaign/job schema.
- Add submission schema.
- Add review states.
- Add estimated/pending earnings language.
- Add admin overview placeholder.

### Phase 3 — Internal Economy and Reputation

- Add ledger events.
- Add XP/reputation event records.
- Add badges/relic placeholders.
- Tie app actions to safe progression events.

### Phase 4 — RPG Profile / Worlds Shell

- Add profile, class, faction, badges, XP, quest board.
- Keep this as app identity/progression first, not a full game engine.

### Phase 5 — UGC Foundation

- Add template/quest/asset submission models.
- Add moderation/review statuses.
- Add seller license and content-rights language.

### Phase 6 — Social Integration Skeletons

- Add isolated integration clients/status pages for YouTube, Twitch, TikTok, Instagram, Polymarket trend-only, OpenAI, Anthropic, Seedance, and Apple Connect.
- No secrets in code.
- No trading.
- No posting until platform app review and permissions are handled.

### Phase 7 — Wallet / Proof Placeholder

- Add wallet placeholder page/status only.
- Add future proof roadmap.
- No token, staking, yield, betting, gambling, or crypto payouts.

## Immediate Next Codex Slice

After source format hardening is verified, the next safe implementation slice is:

**Marketplace skeleton + internal economy placeholders**

Scope:

- Add route/page shells only.
- Add data models or JSON-store-safe placeholders based on existing persistence pattern.
- Add no-guaranteed-earnings language.
- Add estimated/pending/approved payout states.
- Do not add Stripe Connect yet.
- Do not add real crypto.
- Do not touch iOS.

## Safe Customer-Facing Language

Use:

- Earn from approved clipping jobs.
- Estimated earnings.
- Pending approval.
- Approved payout.
- Platform fee applies.
- Payouts require review.
- Digital collectibles are optional future features and are not investments.

Avoid:

- Guaranteed income.
- Passive income.
- Get rich.
- Risk-free earnings.
- Invest and earn.
- Stake/yield.
- Bet/win.
- Token profit.

## Team Needed

1. Founding Systems Architect / Creative Technical Director
2. Full-Stack Platform Engineer
3. AI/Media Pipeline Engineer
4. Game Systems Designer
5. Marketplace Product Lead
6. UI/UX Product Designer
7. Blockchain/Game Economy Engineer
8. Legal/Compliance Advisor
9. Technical Producer / Operator
10. Trust & Safety Lead

The first key hire is the systems architect who can connect clipping, marketplace, UGC, RPG identity, internal ledger, social intelligence, future chain readiness, and compliance into one buildable machine.
