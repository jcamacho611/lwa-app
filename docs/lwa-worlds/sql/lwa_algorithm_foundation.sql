-- LWA Algorithm Foundation SQL
-- Source: LWA Worlds Master Algorithm + Database Stack
-- Status: planning / migration blueprint
--
-- This file is intentionally under docs because the current repo uses an MVP SQLite PlatformStore.
-- Do not apply directly to production until the backend database strategy is confirmed.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

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
