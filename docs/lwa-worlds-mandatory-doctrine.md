# LWA Worlds Mandatory Doctrine

## Status

This document is mandatory project doctrine for LWA / IWA / LWA Worlds.

It consolidates the ChatGPT chunk-thread direction into a repo-visible operating spec so Codex, ChatGPT, contractors, and future hires do not treat the vision as optional brainstorming.

This document does **not** mean every feature should be coded at once. It means every implementation slice must align with this system.

## Supreme Product Thesis

**LWA Worlds is a creator-economy operating system where AI creates media, marketplace creates money, UGC creates supply, RPG progression creates identity, social intelligence creates relevance, and blockchain later creates proof.**

LWA is not only a clipping app. The clipping engine is the foundation and money/content engine for a broader platform.

## Required Product Pillars

1. **AI Clipping Engine**
   - Ingest public URLs, uploads, streams, audio, files, and prompts over time.
   - Transcribe, detect moments, remove silence, crop vertical, caption, render, score, rank, package, export, and recover failed jobs.
   - Output must feel finished and usable, not theoretical.

2. **Social Intelligence Engine**
   - Integrate or scaffold YouTube, TikTok, Instagram, Twitch, Reddit/news/trends, Polymarket trend-only, OpenAI, Anthropic, Seedance, and Apple/App Store readiness.
   - Use social APIs for relevance, metadata, trend intelligence, distribution planning, and creator workflows.
   - Polymarket is trend intelligence only. No trading, betting, or gambling.

3. **Marketplace Engine**
   - Buyers post content/clipping/campaign jobs.
   - Clippers, editors, creators, template sellers, and UGC builders submit work or sell assets.
   - Buyers/admins approve, reject, request revision, dispute, or release payout.
   - All earnings language must use estimated, pending, approved, payable, paid, held, disputed, refunded.

4. **UGC Creation Engine**
   - Users create templates, hook packs, caption packs, prompt packs, quests, campaigns, cosmetics, character concepts, world assets, and creator services.
   - UGC must support review, moderation, licensing, ownership declarations, reports, and takedowns.

5. **RPG / World Engine**
   - Users have identities, avatars, classes, factions, XP, skills, quests, badges, relics, titles, ranks, and reputation.
   - Real platform actions create progression.
   - The world must be original. Do not copy GTA, Roblox, Fortnite, RuneScape, Elden Ring, One Piece, Sony, Nintendo, Marvel, DC, anime IP, or any existing franchise.

6. **Internal Economy Ledger**
   - Track credits, generation usage, XP, reputation, pending earnings, approved earnings, paid earnings, platform fees, holds, disputes, refunds, badges, relics, collectibles, referrals, and wallet placeholders.
   - Every money/reputation/progression event needs source, owner, status, timestamp, and auditability.

7. **Blockchain / NFT / Crypto Proof Layer**
   - Phase 1 is internal ledger and wallet/proof placeholders only.
   - Future chain use is proof-of-creation, proof-of-campaign-completion, optional cosmetics, badges, founder passes, and reputation proof.
   - No token launch, staking, yield, gambling, betting, crypto payouts, or investment language in MVP.
   - Legal/security review is required before any real NFT, wallet, token, or chain feature ships.

8. **Admin / Moderation / Fraud Layer**
   - Admin must be able to review campaigns, submissions, UGC, payouts, disputes, abuse, fraud, content rights, integrations, and system health.

## Mandatory Safety Rules

- Preserve the existing clipping/generation flow by default.
- Additive edits only unless there is a proven defect.
- Do not touch `lwa-ios/` unless the task is explicitly iOS.
- No guaranteed earnings claims.
- No gambling, betting, staking, yield, passive-income, or get-rich language.
- No Polymarket trading.
- No token launch in phase 1.
- No real crypto payouts in phase 1.
- NFTs/digital collectibles must be optional, cosmetic/proof/access only, and not investments.
- Users must own or have rights to submitted content.
- Every payout must support pending review, approved, payable, processing, paid, failed, held, disputed, refunded, cancelled.
- Every UGC item must support moderation/review status.
- Every money movement must be auditable.

## Original World Direction

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

## User Money Loops

Users may make money through:

- approved clip jobs
- campaign submissions
- template sales
- UGC asset sales
- creator services
- managed clipping work
- affiliate/referral commissions
- optional future cosmetic/access collectibles after legal review

LWA may make money through:

- clipping subscriptions
- generation credits
- marketplace platform fees
- template/UGC sales fees
- managed campaigns
- agency/team plans
- premium cosmetics
- enterprise/API access
- future appchain/proof services after review

## Required Routes Over Time

### Core

- `/command-center`
- `/generate`
- `/results/[jobId]`
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

### Economy / Chain

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

## Required Backend Areas Over Time

- auth
- users/profiles
- clipping/generation
- transcription
- captions/rendering
- social intelligence
- marketplace
- campaigns
- submissions/reviews
- templates
- UGC
- quests
- XP/reputation
- badges/relics
- ledger
- wallet placeholder/proof placeholder
- payouts placeholder then Stripe Connect after review
- affiliates/referrals
- admin
- moderation
- fraud detection
- notifications
- storage
- analytics
- integrations

## Required Integration Clients

Scaffold isolated integration clients under the backend without hardcoded secrets:

- YouTube Data API
- TikTok API
- Instagram Graph API
- Twitch API
- Polymarket public/trend-only APIs
- OpenAI
- Anthropic Claude
- Seedance / BytePlus ModelArk
- Apple App Store Connect
- Whop
- Stripe/Stripe Connect later

## Required Database Areas Over Time

### Account

- users
- user_profiles
- teams
- team_members
- roles
- permissions
- sessions
- api_keys

### Clipping

- source_videos
- clip_jobs
- clip_results
- clip_assets
- clip_transcripts
- clip_scores
- clip_packages
- caption_styles
- render_jobs
- render_failures
- generation_events

### Marketplace

- marketplace_profiles
- clipper_profiles
- buyer_profiles
- campaigns
- campaign_requirements
- campaign_assets
- campaign_submissions
- submission_reviews
- submission_revisions
- campaign_deliverables
- marketplace_orders
- marketplace_fees
- disputes
- ratings
- reviews

### Earnings / Payouts

- earnings_accounts
- earning_events
- pending_earnings
- approved_earnings
- payouts
- payout_methods
- payout_holds
- refunds
- chargebacks
- tax_profiles
- platform_fee_events

### UGC

- ugc_assets
- ugc_asset_versions
- ugc_asset_categories
- ugc_submissions
- ugc_reviews
- ugc_sales
- ugc_licenses
- ugc_reports
- ugc_moderation_events
- world_templates
- quest_templates
- cosmetic_assets

### RPG / Worlds

- world_profiles
- avatar_profiles
- classes
- user_classes
- factions
- user_factions
- quests
- quest_steps
- quest_completions
- xp_events
- skill_tracks
- user_skills
- badges
- user_badges
- relics
- user_relics
- titles
- user_titles
- leaderboards
- world_events

### Economy Ledger

- internal_ledger_entries
- credit_balances
- credit_transactions
- reputation_events
- creator_reputation
- clipper_reputation
- marketplace_reputation
- wallet_connections
- collectible_placeholders
- chain_proof_placeholders

### Integrations / Admin / Security

- api_integrations
- integration_tokens
- integration_status
- youtube_sources
- tiktok_sources
- instagram_sources
- twitch_sources
- polymarket_trends
- openai_usage_events
- anthropic_usage_events
- seedance_jobs
- apple_connect_events
- admin_actions
- audit_logs
- moderation_queue
- fraud_flags
- abuse_reports
- content_rights_claims
- dmca_requests
- security_events
- webhook_events
- system_health_events

## Real-World Talent Archetypes To Study / Recruit Near

These are not instructions to copy IP or personalities. They are public-reference talent archetypes that explain the kind of expertise LWA needs.

- Roblox / David Baszucki archetype: UGC platform economy, creator marketplaces, digital goods, payments/fraud.
- Epic / Tim Sweeney archetype: engine-first thinking, creator tools, app/storefront ecosystems, UGC publishing.
- OpusClip / Young Zhao and CTO-style archetype: AI clipping product and media infrastructure.
- Whop founder archetype: creator commerce, digital products, subscriptions, app-like storefronts.
- Stripe / Collison archetype: serious money movement, marketplace payouts, ledger discipline, fraud/disputes.
- FromSoftware / Hidetaka Miyazaki archetype: mythic RPG identity, mystery, earned progression, lore through relics.
- Rockstar / Dan Houser archetype: transmedia worldbuilding, characters, culture, satire, dialogue, long-form IP.
- Jagex / RuneScape archetype: skills, progression, grind loops, economy balance, long-term player trust.
- thirdweb/OpenZeppelin archetype: wallet/proof tooling and smart-contract/security discipline.

## Mandatory Team Roles

1. Founding Systems Architect / Creative Technical Director
2. Full-Stack Platform Engineer
3. AI / Media Pipeline Engineer
4. AI Orchestration Engineer
5. Game Systems Designer
6. Marketplace Product Lead
7. UI/UX Product Designer
8. Blockchain / Game Economy Engineer
9. Legal / Compliance Advisor
10. Technical Producer / Operator
11. Trust & Safety Lead
12. Creator Partnerships / Marketplace Ops Lead
13. Community Director
14. Investor / Fundraising Lead

The first mission of this team is not to code the entire fantasy. It is to build the vertical slice that proves all pillars connect.

## Contest / Investor Vertical Slice

The first demo that proves the platform:

1. User signs in.
2. User enters command center.
3. User generates clips from a source.
4. Best clip appears first with hooks/captions/package.
5. User creates marketplace campaign from the clip pack.
6. Clipper submits improved work.
7. Buyer/admin approves or requests revision.
8. Clipper receives pending/approved earnings state.
9. XP/reputation event is awarded.
10. Badge/relic unlocks.
11. World profile updates.
12. Economy ledger records events.
13. Wallet/proof page shows future chain readiness only.
14. Admin dashboard shows moderation/payout/dispute state.

## Build Order

1. Protect and harden the clipping engine.
2. Add source/upload support and rendered-proof-first UX.
3. Add marketplace skeleton and post-job/submission/review states.
4. Add internal economy ledger with estimated/pending/approved earnings.
5. Add RPG profile/progression/quests/badges tied to real app actions.
6. Add UGC creation/review/sales placeholders.
7. Add integrations dashboard and isolated API clients.
8. Add admin/moderation/fraud overview.
9. Add wallet/proof placeholder only.
10. Add real payouts, NFTs, or chain only after legal/security review.

## Immediate Codex Rule

Before implementation, Codex must read this document and report:

1. What existing work must be preserved.
2. Which pillar the next task belongs to.
3. Which files will be touched.
4. Which files will not be touched.
5. What will remain mocked/stubbed.
6. What verification will run.

## Immediate Next Implementation Slice

After source hardening and route separation are stable, the next safe slice is:

**Marketplace skeleton + internal economy placeholders + RPG profile shell.**

Scope:

- Add frontend pages/shells.
- Add backend models/routes only if they fit existing persistence patterns.
- Use safe statuses and disclaimers.
- No real payouts.
- No real crypto.
- No token.
- No iOS changes.

## Canonical Safety Copy

Use:

- Earnings are estimated until reviewed and approved.
- Payouts require approval and may be held during review, dispute, or fraud checks.
- Platform fee may apply.
- Users must own or have rights to submitted content.
- Digital collectibles and wallet features are optional future features and are not investments.

Avoid:

- Guaranteed income.
- Passive income.
- Get rich.
- Risk-free money.
- Stake/yield.
- Bet/win.
- Token profit.
- NFT investment.

## Definition Of Done For Doctrine Sync

This doctrine is synced when:

- It exists in the repo.
- Future prompts point Codex to it first.
- Roadmap/docs/tasks reference these pillars.
- Implementation slices preserve existing working clipping flows.
- Marketplace/RPG/UGC/blockchain work follows this order and safety model.
