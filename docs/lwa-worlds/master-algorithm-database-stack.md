# LWA Master Algorithm + Database Stack

## Purpose

This document captures the full LWA algorithm stack, SQL/database direction, and backend build order from the planning thread.

It is not a claim that all systems are implemented. It is the engineering blueprint for what the repo should build in safe slices.

## Master build goal

LWA must become a system that does this:

```text
One source URL or upload
→ understand the content
→ find the best moments
→ rank clips by viral value + sales value
→ recommend platform
→ generate hooks/captions/thumbnails/CTA
→ render what can be rendered
→ honestly label what cannot be rendered
→ learn from user behavior
→ help creators turn one source into a campaign
```

Not just:

```text
Upload video → get random clips
```

The product must feel like:

> A director, editor, strategist, campaign planner, and growth operator inside one machine.

## Full algorithm list

### Core clipping algorithms

1. Source Validation Algorithm
2. Source Normalization Algorithm
3. Source Metadata Extraction Algorithm
4. Generation Job Lifecycle Algorithm
5. Transcript Acquisition Algorithm
6. Transcript Cleanup Algorithm
7. Transcript Segmentation Algorithm
8. Segment Signal Extraction Algorithm
9. Moment Candidate Detection Algorithm
10. Candidate Window Expansion Algorithm
11. Candidate Deduplication Algorithm
12. Director Brain Final Scoring Algorithm
13. Platform Fit Scoring Algorithm
14. Offer / Revenue Moment Detection Algorithm
15. Hook Generation Algorithm
16. Caption Packaging Algorithm
17. Caption Style Selection Algorithm
18. Thumbnail Text Algorithm
19. CTA Suggestion Algorithm
20. Post Order Ranking Algorithm

### Media / rendering algorithms

21. Render Readiness Algorithm
22. Aspect Ratio Decision Algorithm
23. 9:16 Crop Strategy Algorithm
24. Audio Normalization Algorithm
25. Burned-In Caption Layout Algorithm
26. Clip Asset Persistence Algorithm
27. Quality Gate Algorithm
28. Render Failure Recovery Algorithm
29. Raw-Only Classification Algorithm
30. Strategy-Only Classification Algorithm

### Campaign / business algorithms

31. Campaign Mode Role Assignment Algorithm
32. Funnel Stage Classification Algorithm
33. Creator Profile Personalization Algorithm
34. Brand Voice Matching Algorithm
35. Target Customer Matching Algorithm
36. Medspa / Local Business Sales Clip Algorithm
37. Agency Batch Output Algorithm
38. Whop Seller Offer Clip Algorithm
39. Podcast Network Clip Stack Algorithm
40. Coach / Educator Authority Clip Algorithm

### Learning / intelligence algorithms

41. User Behavior Tracking Algorithm
42. Clip Feedback Learning Algorithm
43. Hook Performance Learning Algorithm
44. Caption Performance Learning Algorithm
45. Platform Performance Learning Algorithm
46. Creator Preference Memory Algorithm
47. Source-Type Performance Algorithm
48. Re-Rank After Feedback Algorithm
49. Trend Match Algorithm
50. Trend Decay Algorithm

### Product / monetization algorithms

51. Free Launch Mode Algorithm
52. Guest User Fallback Algorithm
53. Usage Ledger Algorithm
54. Credit Balance Algorithm
55. Abuse Prevention Algorithm
56. IP Rate Limit Algorithm
57. Whop Entitlement Algorithm
58. Stripe Idempotency Algorithm
59. Webhook Event Deduplication Algorithm
60. Plan Feature Gate Algorithm

### Operator / admin algorithms

61. Failed Job Priority Algorithm
62. Render Failure Rate Algorithm
63. Best User Lead Algorithm
64. Power User Detection Algorithm
65. Support Triage Algorithm
66. Investor Demo Health Algorithm
67. Sales Demo Readiness Algorithm
68. System Reliability Score Algorithm
69. Cost Per Generation Algorithm
70. Margin Per User Algorithm

### Later algorithms

71. Marketplace Product Ranking Algorithm
72. Seller Trust Algorithm
73. Refund Risk Algorithm
74. Dispute Risk Algorithm
75. Marketplace Fraud Detection Algorithm
76. RPG XP Award Algorithm
77. Quest Assignment Algorithm
78. Badge Award Algorithm
79. Cosmetic Relic Algorithm
80. Off-Chain Proof Algorithm
81. Merkle Batch Algorithm
82. Blockchain Publish Eligibility Algorithm

## Build order

Use this order:

1. Source validation
2. Metadata extraction
3. Transcript segmentation
4. Moment detection
5. Director Brain scoring
6. Platform fit
7. Hook engine
8. Offer / money moment detection
9. Caption style engine
10. Quality gate
11. Render readiness
12. Fallback engine
13. Post order
14. Campaign mode
15. Frontend rendered/strategy split
16. Learning loop
17. Creator profile memory
18. Trend matching
19. Whop/entitlement
20. Operator dashboard

## Database design principles

Use these principles for the future production database foundation:

- Use UUID primary keys.
- Use Postgres when moving beyond current SQLite MVP storage.
- Use JSONB for flexible algorithm output.
- Use explicit columns for important searchable/rankable values.
- Do not use floating point for money.
- Use integer cents for money.
- Webhook events must be idempotent.
- Jobs must be retryable.
- User actions must be logged.
- Clip render state must be explicit.
- Strategy-only clips must never pretend to be playable.
- Rendered clips must have at least one asset URL.
- Every generated clip should be traceable back to source, job, candidate, score, package, and assets.

## Core database table map

Core tables:

- users
- creator_profiles
- source_assets
- generation_jobs
- transcript_segments
- segment_signals
- moment_candidates
- platform_fit_scores
- offer_detection_scores
- algorithm_scores
- clip_packages
- caption_style_results
- quality_gate_results
- clip_results
- clip_assets
- campaigns
- campaign_items
- user_clip_events
- fallback_results
- usage_ledger
- entitlements
- webhook_events
- operator_events

Later tables:

- marketplace_products
- marketplace_orders
- marketplace_payouts
- seller_profiles
- seller_disputes
- realms_profiles
- realms_xp_events
- realms_quests
- realms_badges
- proof_events
- merkle_batches

## SQL foundation

### Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### users

```sql
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NULL,
    display_name TEXT NULL,
    whop_user_id TEXT UNIQUE NULL,
    stripe_customer_id TEXT UNIQUE NULL,
    plan_code TEXT NOT NULL DEFAULT 'guest',
    plan_name TEXT NOT NULL DEFAULT 'Guest',
    is_guest BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_whop_user_id ON users(whop_user_id);
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer_id ON users(stripe_customer_id);
```

### creator_profiles

```sql
CREATE TABLE IF NOT EXISTS creator_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL REFERENCES users(id) ON DELETE CASCADE,
    creator_type TEXT NOT NULL DEFAULT 'general',
    brand_voice TEXT NOT NULL DEFAULT 'creator_native',
    business_name TEXT NULL,
    offer_name TEXT NULL,
    offer_description TEXT NULL,
    target_customer TEXT NULL,
    preferred_platforms JSONB NOT NULL DEFAULT '[]'::jsonb,
    banned_words JSONB NOT NULL DEFAULT '[]'::jsonb,
    winning_hooks JSONB NOT NULL DEFAULT '[]'::jsonb,
    bad_outputs JSONB NOT NULL DEFAULT '[]'::jsonb,
    profile_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_creator_profiles_user ON creator_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_creator_profiles_type ON creator_profiles(creator_type);
CREATE INDEX IF NOT EXISTS idx_creator_profiles_profile_json ON creator_profiles USING GIN(profile_json);
```

Creator types include:

- general
- creator
- podcaster
- agency
- coach
- educator
- streamer
- rapper
- medspa
- local_business
- whop_seller
- real_estate
- fitness
- beauty
- restaurant
- law_firm
- financial_educator

Brand voices include:

- luxury
- aggressive
- educational
- funny
- professional
- chaotic
- premium_dark
- gen_z
- corporate_clean
- founder_authority
- local_trust
- whop_money

### source_assets

```sql
CREATE TABLE IF NOT EXISTS source_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
    creator_profile_id UUID NULL REFERENCES creator_profiles(id) ON DELETE SET NULL,
    source_url TEXT NOT NULL,
    normalized_url TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'unknown',
    source_platform TEXT NOT NULL DEFAULT 'unknown',
    source_title TEXT NULL,
    source_creator TEXT NULL,
    source_description TEXT NULL,
    source_thumbnail_url TEXT NULL,
    duration_seconds INTEGER NULL,
    language_code TEXT NULL,
    public_access_likely BOOLEAN NOT NULL DEFAULT TRUE,
    validation_status TEXT NOT NULL DEFAULT 'pending',
    validation_reason TEXT NULL,
    metadata_confidence INTEGER NOT NULL DEFAULT 0 CHECK (metadata_confidence BETWEEN 0 AND 100),
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_source_assets_user ON source_assets(user_id);
CREATE INDEX IF NOT EXISTS idx_source_assets_creator_profile ON source_assets(creator_profile_id);
CREATE INDEX IF NOT EXISTS idx_source_assets_normalized_url ON source_assets(normalized_url);
CREATE INDEX IF NOT EXISTS idx_source_assets_platform ON source_assets(source_platform);
CREATE INDEX IF NOT EXISTS idx_source_assets_created ON source_assets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_source_assets_metadata_json ON source_assets USING GIN(metadata_json);
```

Duplicate source check:

```sql
SELECT id, created_at
FROM source_assets
WHERE normalized_url = $1
  AND created_at > now() - interval '10 minutes'
ORDER BY created_at DESC
LIMIT 5;
```

### generation_jobs

```sql
CREATE TABLE IF NOT EXISTS generation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
    creator_profile_id UUID NULL REFERENCES creator_profiles(id) ON DELETE SET NULL,
    source_asset_id UUID NULL REFERENCES source_assets(id) ON DELETE SET NULL,
    request_id TEXT NOT NULL UNIQUE,
    source_url TEXT NOT NULL,
    target_platform TEXT NOT NULL DEFAULT 'auto',
    trend_angle TEXT NULL,
    user_context TEXT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    algorithm_version TEXT NOT NULL DEFAULT 'LWA_DIRECTOR_BRAIN_V0',
    requested_max_clips INTEGER NOT NULL DEFAULT 12,
    rendered_clip_count INTEGER NOT NULL DEFAULT 0,
    raw_only_clip_count INTEGER NOT NULL DEFAULT 0,
    strategy_only_clip_count INTEGER NOT NULL DEFAULT 0,
    failed_clip_count INTEGER NOT NULL DEFAULT 0,
    recommended_platform TEXT NULL,
    recommended_content_type TEXT NULL,
    recommended_output_style TEXT NULL,
    platform_recommendation_reason TEXT NULL,
    recommended_next_step TEXT NULL,
    error_code TEXT NULL,
    error_message TEXT NULL,
    processing_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_generation_jobs_user_created ON generation_jobs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_generation_jobs_status ON generation_jobs(status);
CREATE INDEX IF NOT EXISTS idx_generation_jobs_source_asset ON generation_jobs(source_asset_id);
CREATE INDEX IF NOT EXISTS idx_generation_jobs_algorithm_version ON generation_jobs(algorithm_version);
CREATE INDEX IF NOT EXISTS idx_generation_jobs_processing_summary ON generation_jobs USING GIN(processing_summary);
```

Job states:

- queued
- validating_source
- extracting_metadata
- downloading_source
- extracting_audio
- transcribing
- segmenting_transcript
- extracting_signals
- detecting_moments
- scoring_candidates
- packaging_clips
- rendering_clips
- quality_checking
- completed
- partial
- fallback
- failed
- cancelled

### transcript_segments

```sql
CREATE TABLE IF NOT EXISTS transcript_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    source_asset_id UUID NULL REFERENCES source_assets(id) ON DELETE SET NULL,
    segment_index INTEGER NOT NULL,
    start_seconds NUMERIC(10,3) NOT NULL,
    end_seconds NUMERIC(10,3) NOT NULL,
    duration_seconds NUMERIC(10,3) GENERATED ALWAYS AS (end_seconds - start_seconds) STORED,
    text TEXT NOT NULL,
    cleaned_text TEXT NULL,
    speaker_label TEXT NULL,
    confidence NUMERIC(5,4) NULL,
    token_count INTEGER NULL,
    word_count INTEGER NULL,
    segment_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT transcript_segment_time_valid CHECK (end_seconds > start_seconds)
);

CREATE INDEX IF NOT EXISTS idx_transcript_segments_job_time ON transcript_segments(job_id, start_seconds, end_seconds);
CREATE INDEX IF NOT EXISTS idx_transcript_segments_source ON transcript_segments(source_asset_id);
CREATE INDEX IF NOT EXISTS idx_transcript_segments_text_search ON transcript_segments USING GIN(to_tsvector('english', text));
```

### segment_signals

```sql
CREATE TABLE IF NOT EXISTS segment_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transcript_segment_id UUID NOT NULL REFERENCES transcript_segments(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    hook_density INTEGER NOT NULL DEFAULT 0 CHECK (hook_density BETWEEN 0 AND 100),
    payoff_density INTEGER NOT NULL DEFAULT 0 CHECK (payoff_density BETWEEN 0 AND 100),
    emotional_energy INTEGER NOT NULL DEFAULT 0 CHECK (emotional_energy BETWEEN 0 AND 100),
    clarity INTEGER NOT NULL DEFAULT 0 CHECK (clarity BETWEEN 0 AND 100),
    controversy INTEGER NOT NULL DEFAULT 0 CHECK (controversy BETWEEN 0 AND 100),
    educational_value INTEGER NOT NULL DEFAULT 0 CHECK (educational_value BETWEEN 0 AND 100),
    story_value INTEGER NOT NULL DEFAULT 0 CHECK (story_value BETWEEN 0 AND 100),
    quote_strength INTEGER NOT NULL DEFAULT 0 CHECK (quote_strength BETWEEN 0 AND 100),
    authority_signal INTEGER NOT NULL DEFAULT 0 CHECK (authority_signal BETWEEN 0 AND 100),
    offer_signal INTEGER NOT NULL DEFAULT 0 CHECK (offer_signal BETWEEN 0 AND 100),
    objection_signal INTEGER NOT NULL DEFAULT 0 CHECK (objection_signal BETWEEN 0 AND 100),
    transformation_signal INTEGER NOT NULL DEFAULT 0 CHECK (transformation_signal BETWEEN 0 AND 100),
    dead_air_risk INTEGER NOT NULL DEFAULT 0 CHECK (dead_air_risk BETWEEN 0 AND 100),
    brand_safety_risk INTEGER NOT NULL DEFAULT 0 CHECK (brand_safety_risk BETWEEN 0 AND 100),
    signal_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_segment_signals_job ON segment_signals(job_id);
CREATE INDEX IF NOT EXISTS idx_segment_signals_high_hook ON segment_signals(job_id, hook_density DESC);
CREATE INDEX IF NOT EXISTS idx_segment_signals_offer ON segment_signals(job_id, offer_signal DESC, objection_signal DESC, transformation_signal DESC);
```

### moment_candidates

```sql
CREATE TABLE IF NOT EXISTS moment_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    source_asset_id UUID NULL REFERENCES source_assets(id) ON DELETE SET NULL,
    candidate_index INTEGER NOT NULL,
    start_seconds NUMERIC(10,3) NOT NULL,
    end_seconds NUMERIC(10,3) NOT NULL,
    duration_seconds NUMERIC(10,3) NOT NULL,
    opening_line TEXT NULL,
    payoff_line TEXT NULL,
    transcript_text TEXT NOT NULL,
    candidate_type TEXT NOT NULL DEFAULT 'general',
    detection_reason TEXT NULL,
    raw_signal_score INTEGER NOT NULL DEFAULT 0 CHECK (raw_signal_score BETWEEN 0 AND 100),
    candidate_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_moment_candidates_job_score ON moment_candidates(job_id, raw_signal_score DESC);
CREATE INDEX IF NOT EXISTS idx_moment_candidates_time ON moment_candidates(job_id, start_seconds, end_seconds);
CREATE INDEX IF NOT EXISTS idx_moment_candidates_type ON moment_candidates(candidate_type);
```

Candidate types:

- viral_hook
- educational
- authority
- sales
- objection
- transformation
- story
- controversy
- community
- quote

### platform_fit_scores

```sql
CREATE TABLE IF NOT EXISTS platform_fit_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES moment_candidates(id) ON DELETE CASCADE,
    tiktok_score INTEGER NOT NULL DEFAULT 0 CHECK (tiktok_score BETWEEN 0 AND 100),
    instagram_reels_score INTEGER NOT NULL DEFAULT 0 CHECK (instagram_reels_score BETWEEN 0 AND 100),
    youtube_shorts_score INTEGER NOT NULL DEFAULT 0 CHECK (youtube_shorts_score BETWEEN 0 AND 100),
    linkedin_score INTEGER NOT NULL DEFAULT 0 CHECK (linkedin_score BETWEEN 0 AND 100),
    facebook_reels_score INTEGER NOT NULL DEFAULT 0 CHECK (facebook_reels_score BETWEEN 0 AND 100),
    x_score INTEGER NOT NULL DEFAULT 0 CHECK (x_score BETWEEN 0 AND 100),
    twitch_score INTEGER NOT NULL DEFAULT 0 CHECK (twitch_score BETWEEN 0 AND 100),
    whop_score INTEGER NOT NULL DEFAULT 0 CHECK (whop_score BETWEEN 0 AND 100),
    recommended_platform TEXT NOT NULL DEFAULT 'auto',
    recommendation_reason TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_platform_fit_job_candidate ON platform_fit_scores(job_id, candidate_id);
CREATE INDEX IF NOT EXISTS idx_platform_fit_recommended ON platform_fit_scores(recommended_platform);
```

### offer_detection_scores

```sql
CREATE TABLE IF NOT EXISTS offer_detection_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES moment_candidates(id) ON DELETE CASCADE,
    revenue_intent_score INTEGER NOT NULL DEFAULT 0 CHECK (revenue_intent_score BETWEEN 0 AND 100),
    offer_fit_score INTEGER NOT NULL DEFAULT 0 CHECK (offer_fit_score BETWEEN 0 AND 100),
    proof_score INTEGER NOT NULL DEFAULT 0 CHECK (proof_score BETWEEN 0 AND 100),
    objection_handling_score INTEGER NOT NULL DEFAULT 0 CHECK (objection_handling_score BETWEEN 0 AND 100),
    transformation_score INTEGER NOT NULL DEFAULT 0 CHECK (transformation_score BETWEEN 0 AND 100),
    cta_readiness_score INTEGER NOT NULL DEFAULT 0 CHECK (cta_readiness_score BETWEEN 0 AND 100),
    detected_offer_type TEXT NULL,
    offer_reason TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_offer_detection_job_revenue ON offer_detection_scores(job_id, revenue_intent_score DESC);
CREATE INDEX IF NOT EXISTS idx_offer_detection_candidate ON offer_detection_scores(candidate_id);
```

Offer types:

- service_offer
- product_offer
- lead_magnet
- consultation
- booking
- course
- community
- subscription
- event
- testimonial
- case_study
- before_after
- objection_response

### algorithm_scores

```sql
CREATE TABLE IF NOT EXISTS algorithm_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES moment_candidates(id) ON DELETE CASCADE,
    algorithm_version TEXT NOT NULL DEFAULT 'LWA_DIRECTOR_BRAIN_V0',
    hook_strength INTEGER NOT NULL DEFAULT 0 CHECK (hook_strength BETWEEN 0 AND 100),
    payoff_strength INTEGER NOT NULL DEFAULT 0 CHECK (payoff_strength BETWEEN 0 AND 100),
    platform_fit INTEGER NOT NULL DEFAULT 0 CHECK (platform_fit BETWEEN 0 AND 100),
    clarity INTEGER NOT NULL DEFAULT 0 CHECK (clarity BETWEEN 0 AND 100),
    emotional_energy INTEGER NOT NULL DEFAULT 0 CHECK (emotional_energy BETWEEN 0 AND 100),
    shareability INTEGER NOT NULL DEFAULT 0 CHECK (shareability BETWEEN 0 AND 100),
    novelty INTEGER NOT NULL DEFAULT 0 CHECK (novelty BETWEEN 0 AND 100),
    visual_audio_quality INTEGER NOT NULL DEFAULT 0 CHECK (visual_audio_quality BETWEEN 0 AND 100),
    captionability INTEGER NOT NULL DEFAULT 0 CHECK (captionability BETWEEN 0 AND 100),
    trend_fit INTEGER NOT NULL DEFAULT 0 CHECK (trend_fit BETWEEN 0 AND 100),
    creator_brand_fit INTEGER NOT NULL DEFAULT 0 CHECK (creator_brand_fit BETWEEN 0 AND 100),
    risk_penalty INTEGER NOT NULL DEFAULT 0 CHECK (risk_penalty BETWEEN 0 AND 100),
    final_score INTEGER NOT NULL DEFAULT 0 CHECK (final_score BETWEEN 0 AND 100),
    confidence_score INTEGER NOT NULL DEFAULT 0 CHECK (confidence_score BETWEEN 0 AND 100),
    score_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_algorithm_scores_job_final ON algorithm_scores(job_id, final_score DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_algorithm_scores_candidate_version ON algorithm_scores(candidate_id, algorithm_version);
```

Top candidate query:

```sql
SELECT
    mc.id AS candidate_id,
    mc.start_seconds,
    mc.end_seconds,
    mc.duration_seconds,
    mc.candidate_type,
    mc.transcript_text,
    s.final_score,
    s.confidence_score
FROM moment_candidates mc
JOIN algorithm_scores s
    ON s.candidate_id = mc.id
WHERE mc.job_id = $1
ORDER BY s.final_score DESC, s.confidence_score DESC
LIMIT $2;
```

### clip_packages

```sql
CREATE TABLE IF NOT EXISTS clip_packages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    candidate_id UUID NULL REFERENCES moment_candidates(id) ON DELETE SET NULL,
    primary_hook TEXT NOT NULL,
    hook_variants JSONB NOT NULL DEFAULT '[]'::jsonb,
    caption TEXT NULL,
    caption_variants JSONB NOT NULL DEFAULT '{}'::jsonb,
    caption_style TEXT NULL,
    thumbnail_text TEXT NULL,
    cta_suggestion TEXT NULL,
    packaging_angle TEXT NULL,
    why_this_matters TEXT NULL,
    recommended_platform TEXT NULL,
    package_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_clip_packages_job ON clip_packages(job_id);
CREATE INDEX IF NOT EXISTS idx_clip_packages_platform ON clip_packages(recommended_platform);
```

### caption_style_results

```sql
CREATE TABLE IF NOT EXISTS caption_style_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES moment_candidates(id) ON DELETE CASCADE,
    caption_style TEXT NOT NULL,
    caption_style_reason TEXT NULL,
    emphasis_words JSONB NOT NULL DEFAULT '[]'::jsonb,
    suggested_caption_position TEXT NOT NULL DEFAULT 'center_lower',
    font_weight TEXT NOT NULL DEFAULT 'bold',
    max_words_per_line INTEGER NOT NULL DEFAULT 5,
    style_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_caption_style_job ON caption_style_results(job_id);
CREATE INDEX IF NOT EXISTS idx_caption_style_style ON caption_style_results(caption_style);
```

Caption styles:

- luxury_clean
- aggressive_creator
- podcast_bold
- educational_highlight
- meme_punch
- documentary_premium
- local_business_clear
- coach_authority
- streamer_chaos
- whop_money

### quality_gate_results

```sql
CREATE TABLE IF NOT EXISTS quality_gate_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    clip_result_id UUID NULL,
    candidate_id UUID NULL REFERENCES moment_candidates(id) ON DELETE SET NULL,
    quality_gate_status TEXT NOT NULL DEFAULT 'warning',
    render_readiness_score INTEGER NOT NULL DEFAULT 0 CHECK (render_readiness_score BETWEEN 0 AND 100),
    warnings JSONB NOT NULL DEFAULT '[]'::jsonb,
    failures JSONB NOT NULL DEFAULT '[]'::jsonb,
    checked_fields JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_quality_gate_job ON quality_gate_results(job_id);
CREATE INDEX IF NOT EXISTS idx_quality_gate_status ON quality_gate_results(quality_gate_status);
```

### clip_results

```sql
CREATE TABLE IF NOT EXISTS clip_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    candidate_id UUID NULL REFERENCES moment_candidates(id) ON DELETE SET NULL,
    package_id UUID NULL REFERENCES clip_packages(id) ON DELETE SET NULL,
    rank INTEGER NOT NULL,
    post_rank INTEGER NOT NULL,
    start_seconds NUMERIC(10,3) NOT NULL,
    end_seconds NUMERIC(10,3) NOT NULL,
    duration_seconds NUMERIC(10,3) NOT NULL,
    title TEXT NOT NULL,
    hook TEXT NOT NULL,
    caption TEXT NULL,
    score INTEGER NOT NULL DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
    confidence_score INTEGER NOT NULL DEFAULT 0 CHECK (confidence_score BETWEEN 0 AND 100),
    recommended_platform TEXT NULL,
    render_status TEXT NOT NULL DEFAULT 'strategy_only',
    strategy_only BOOLEAN NOT NULL DEFAULT FALSE,
    reason_not_rendered TEXT NULL,
    quality_gate_status TEXT NOT NULL DEFAULT 'warning',
    revenue_intent_score INTEGER NULL CHECK (revenue_intent_score BETWEEN 0 AND 100),
    offer_fit_score INTEGER NULL CHECK (offer_fit_score BETWEEN 0 AND 100),
    campaign_role TEXT NULL,
    campaign_reason TEXT NULL,
    funnel_stage TEXT NULL,
    suggested_post_order INTEGER NULL,
    clip_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_clip_results_job_rank ON clip_results(job_id, rank ASC);
CREATE INDEX IF NOT EXISTS idx_clip_results_job_post_rank ON clip_results(job_id, post_rank ASC);
CREATE INDEX IF NOT EXISTS idx_clip_results_render_status ON clip_results(render_status);
CREATE INDEX IF NOT EXISTS idx_clip_results_campaign_role ON clip_results(campaign_role);
```

### clip_assets

```sql
CREATE TABLE IF NOT EXISTS clip_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clip_result_id UUID NOT NULL REFERENCES clip_results(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    asset_type TEXT NOT NULL,
    asset_url TEXT NOT NULL,
    storage_key TEXT NULL,
    mime_type TEXT NULL,
    width INTEGER NULL,
    height INTEGER NULL,
    duration_seconds NUMERIC(10,3) NULL,
    file_size_bytes BIGINT NULL,
    asset_status TEXT NOT NULL DEFAULT 'available',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_clip_assets_clip ON clip_assets(clip_result_id);
CREATE INDEX IF NOT EXISTS idx_clip_assets_job ON clip_assets(job_id);
CREATE INDEX IF NOT EXISTS idx_clip_assets_type ON clip_assets(asset_type);
```

Asset types:

- raw_clip
- edited_clip
- preview
- thumbnail
- caption_file
- export_bundle

### campaigns and campaign_items

```sql
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL,
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    campaign_name TEXT NOT NULL,
    campaign_goal TEXT NOT NULL DEFAULT 'content_distribution',
    target_platforms JSONB NOT NULL DEFAULT '[]'::jsonb,
    campaign_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS campaign_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    clip_result_id UUID NOT NULL REFERENCES clip_results(id) ON DELETE CASCADE,
    campaign_role TEXT NOT NULL,
    funnel_stage TEXT NOT NULL,
    suggested_post_order INTEGER NOT NULL,
    suggested_platform TEXT NULL,
    suggested_caption_style TEXT NULL,
    suggested_cta TEXT NULL,
    campaign_reason TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_campaign_items_campaign_order ON campaign_items(campaign_id, suggested_post_order ASC);
CREATE INDEX IF NOT EXISTS idx_campaign_items_role ON campaign_items(campaign_role);
```

Campaign roles:

- lead_clip
- trust_clip
- sales_clip
- educational_clip
- controversy_clip
- retargeting_clip
- community_clip

### user_clip_events

```sql
CREATE TABLE IF NOT EXISTS user_clip_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL,
    job_id UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE,
    clip_result_id UUID NOT NULL REFERENCES clip_results(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_value INTEGER NULL,
    event_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_clip_events_user ON user_clip_events(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_clip_events_clip ON user_clip_events(clip_result_id);
CREATE INDEX IF NOT EXISTS idx_user_clip_events_type ON user_clip_events(event_type);
```

Events:

- clip_played
- clip_downloaded
- hook_copied
- caption_copied
- package_copied
- clip_rejected
- clip_regenerated
- render_retried
- strategy_exported
- external_post_confirmed

### usage_ledger

```sql
CREATE TABLE IF NOT EXISTS usage_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL,
    job_id UUID NULL REFERENCES generation_jobs(id) ON DELETE SET NULL,
    ledger_type TEXT NOT NULL,
    credit_delta INTEGER NOT NULL,
    reason TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usage_ledger_user ON usage_ledger(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_ledger_job ON usage_ledger(job_id);
```

Credit balance query:

```sql
SELECT
    user_id,
    COALESCE(SUM(credit_delta), 0) AS credit_balance
FROM usage_ledger
WHERE user_id = $1
GROUP BY user_id;
```

### webhook_events

```sql
CREATE TABLE IF NOT EXISTS webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider TEXT NOT NULL,
    provider_event_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMPTZ NULL,
    error_message TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(provider, provider_event_id)
);

CREATE INDEX IF NOT EXISTS idx_webhook_events_processed ON webhook_events(processed, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_webhook_events_type ON webhook_events(provider, event_type);
```

Idempotent insert:

```sql
INSERT INTO webhook_events (
    provider,
    provider_event_id,
    event_type,
    payload
)
VALUES ($1, $2, $3, $4::jsonb)
ON CONFLICT (provider, provider_event_id)
DO NOTHING
RETURNING *;
```

## Key queries

### Frontend result classification

```sql
SELECT
    cr.id,
    cr.rank,
    cr.post_rank,
    cr.title,
    cr.hook,
    cr.caption,
    cr.score,
    cr.confidence_score,
    cr.recommended_platform,
    cr.render_status,
    cr.strategy_only,
    cr.reason_not_rendered,
    cr.quality_gate_status,
    cr.revenue_intent_score,
    cr.offer_fit_score,
    cr.campaign_role,
    cr.campaign_reason,
    cr.funnel_stage,
    cr.suggested_post_order,
    COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'asset_type', ca.asset_type,
                'asset_url', ca.asset_url,
                'width', ca.width,
                'height', ca.height,
                'duration_seconds', ca.duration_seconds
            )
        ) FILTER (WHERE ca.id IS NOT NULL),
        '[]'::jsonb
    ) AS assets
FROM clip_results cr
LEFT JOIN clip_assets ca
    ON ca.clip_result_id = cr.id
WHERE cr.job_id = $1
GROUP BY cr.id
ORDER BY cr.post_rank ASC, cr.rank ASC;
```

### Learning score query

```sql
SELECT
    cr.id AS clip_result_id,
    cr.title,
    cr.score AS algorithm_score,
    COUNT(*) FILTER (WHERE e.event_type = 'clip_played') AS plays,
    COUNT(*) FILTER (WHERE e.event_type = 'clip_downloaded') AS downloads,
    COUNT(*) FILTER (WHERE e.event_type = 'hook_copied') AS hook_copies,
    COUNT(*) FILTER (WHERE e.event_type = 'caption_copied') AS caption_copies,
    COUNT(*) FILTER (WHERE e.event_type = 'clip_rejected') AS rejects,
    (
        COUNT(*) FILTER (WHERE e.event_type = 'clip_downloaded') * 5
      + COUNT(*) FILTER (WHERE e.event_type = 'package_copied') * 4
      + COUNT(*) FILTER (WHERE e.event_type = 'hook_copied') * 2
      + COUNT(*) FILTER (WHERE e.event_type = 'clip_played') * 1
      - COUNT(*) FILTER (WHERE e.event_type = 'clip_rejected') * 5
    ) AS behavior_score
FROM clip_results cr
LEFT JOIN user_clip_events e
    ON e.clip_result_id = cr.id
WHERE cr.job_id = $1
GROUP BY cr.id
ORDER BY behavior_score DESC;
```

### Failed jobs

```sql
SELECT
    id,
    request_id,
    source_url,
    status,
    error_code,
    error_message,
    created_at
FROM generation_jobs
WHERE status IN ('failed', 'fallback', 'partial')
ORDER BY created_at DESC
LIMIT 100;
```

### Render failure rate

```sql
SELECT
    date_trunc('day', created_at) AS day,
    COUNT(*) AS total_clips,
    COUNT(*) FILTER (WHERE render_status = 'rendered') AS rendered,
    COUNT(*) FILTER (WHERE render_status = 'raw_only') AS raw_only,
    COUNT(*) FILTER (WHERE render_status = 'strategy_only') AS strategy_only,
    COUNT(*) FILTER (WHERE render_status = 'failed') AS failed
FROM clip_results
GROUP BY day
ORDER BY day DESC;
```

### Best-performing hook types

```sql
SELECT
    cp.packaging_angle,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE e.event_type = 'clip_downloaded') AS downloads,
    COUNT(*) FILTER (WHERE e.event_type = 'hook_copied') AS hook_copies
FROM clip_packages cp
JOIN clip_results cr
    ON cr.package_id = cp.id
LEFT JOIN user_clip_events e
    ON e.clip_result_id = cr.id
GROUP BY cp.packaging_angle
ORDER BY downloads DESC, hook_copies DESC;
```

### Top users by generation activity

```sql
SELECT
    user_id,
    COUNT(*) AS total_jobs,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_jobs,
    COUNT(*) FILTER (WHERE status = 'fallback') AS fallback_jobs,
    MAX(created_at) AS last_seen
FROM generation_jobs
WHERE user_id IS NOT NULL
GROUP BY user_id
ORDER BY total_jobs DESC
LIMIT 100;
```

## Codex prompt — build algorithm database foundation

```text
You are the LWA backend systems architect.

Task:
Build the first production-safe version of the LWA algorithm and database foundation.

Implement or scaffold these systems:

1. source validation
2. source metadata storage
3. generation job tracking
4. transcript segment storage
5. segment signal scoring
6. moment candidate detection
7. Director Brain scoring
8. platform fit scoring
9. offer / money moment scoring
10. hook packaging
11. caption style metadata
12. quality gate
13. clip result storage
14. clip asset storage
15. campaign mode scaffold
16. user learning events
17. usage ledger
18. webhook idempotency table
19. operator dashboard queries

Rules:
- Preserve existing backend routes.
- Add optional fields only.
- Do not break current clip generation.
- Do not touch lwa-web unless explicitly required.
- Do not touch lwa-ios.
- Do not fake direct social posting.
- Do not fake playable asset URLs.
- Strategy-only clips must be clearly marked.
- Rendered clips must have a playable or downloadable asset URL.
- Money must use integer cents only.
- Webhook processing must be idempotent.
- Keep all outputs JSON-safe.
- Add database migrations if the repo has migrations.
- If the repo does not have migrations, create SQL files under docs or backend database setup according to existing repo structure.

Required database objects:
- source_assets
- generation_jobs
- transcript_segments
- segment_signals
- moment_candidates
- algorithm_scores
- platform_fit_scores
- offer_detection_scores
- clip_packages
- caption_style_results
- quality_gate_results
- clip_results
- clip_assets
- campaigns
- campaign_items
- user_clip_events
- usage_ledger
- webhook_events

Required backend modules, if structure allows:
- source_validation.py
- source_metadata.py
- transcript_segments.py
- signal_extraction.py
- moment_detection.py
- director_brain.py
- platform_signals.py
- offer_detector.py
- hook_engine.py
- caption_style_engine.py
- quality_gate.py
- clip_results.py
- campaign_engine.py
- learning_loop.py
- usage_ledger.py
- webhook_idempotency.py

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant backend tests
- verify migrations or SQL are syntactically valid
- confirm no lwa-ios files changed
- confirm no frontend files changed unless explicitly necessary

Expected output:
1. exact files changed
2. tables/migrations added
3. modules added
4. algorithm functions added
5. tests added
6. verification results
7. risks or follow-up work
8. commit message
```

## Do not build yet

Do not let this work jump into:

- NFT/blockchain implementation
- RPG layer implementation
- marketplace money movement
- full editor
- direct social posting
- full iOS rebuild
- fake upload pipeline
- fake campaign manager

Those are future phases after clipping quality, frontend proof, entitlement verification, and launch hardening.
