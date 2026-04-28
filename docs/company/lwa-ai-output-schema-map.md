# LWA AI Output Schema Map

## Purpose
This document defines the expected AI-facing output contract for any-source package generation.

It is the schema target that backend, frontend, iOS, tests, and fallback logic should share.

## 1. Clip Package Schema

```text
clip_id: string
source_type: video | audio | music | prompt | twitch | stream | campaign | upload | url | unknown
title: string
hook: string
hook_variants: string[]
caption: string
caption_variants: object
caption_style: string
thumbnail_text: string
cta_suggestion: string
why_this_matters: string
score: number
confidence_score: number
post_rank: number
score_breakdown: object
platform_fit: string
retention_reason: string
first_three_seconds_assessment: string
visual_generation_prompt: string
rendered_status: rendered | strategy_only | render_limited | failed | unknown
fallback_reason: string | null
strategy_package: object | null
clip_url: string | null
preview_url: string | null
download_url: string | null
start_time: string | null
end_time: string | null
```

## 2. Score Breakdown Schema

```text
hook_strength: 0-100
first_three_seconds: 0-100
emotional_spike: 0-100
curiosity_gap: 0-100
clarity: 0-100
conflict_tension: 0-100
payoff: 0-100
shareability: 0-100
platform_fit: 0-100
visual_audio_strength: 0-100
caption_usefulness: 0-100
campaign_fit: 0-100
render_readiness: 0-100
```

## 3. Fallback Schema

```text
fallback_type: platform_block | render_failed | transcript_missing | unsupported_format | provider_unavailable | unknown
user_message: string
technical_summary: string
safe_next_steps: string[]
strategy_only_package: object
can_retry: boolean
recommended_retry_mode: upload | audio | prompt | different_source | later
```

## 4. Required Truth Labels

The output contract must always preserve clear state:

- `rendered`
- `strategy_only`
- `render_limited`
- `platform_blocked`
- `manual_review_required`
- `fallback_package`

## 5. Field Rules

### Always required for useful creator output

- `title`
- `hook`
- `caption`
- `thumbnail_text`
- `cta_suggestion`
- `why_this_matters`
- `rendered_status`

### Required for ranked output

- `score`
- `confidence_score`
- `post_rank`
- `score_breakdown`

### Optional when context supports them

- `start_time`
- `end_time`
- `visual_generation_prompt`
- `clip_url`
- `preview_url`
- `download_url`
- `caption_variants`
- `hook_variants`

### Must stay nullable

- `clip_url`
- `preview_url`
- `download_url`
- `fallback_reason`
- `strategy_package`
- `start_time`
- `end_time`

## 6. Current Repo Alignment

Current backend/frontend alignment already includes many of these fields in some form:

- hooks
- captions
- thumbnail text
- CTA suggestions
- score
- confidence score
- why-this-matters
- score breakdown
- rendered status
- fallback reason
- package text
- export metadata

Still incomplete:

- one canonical any-source `source_type` contract across every path
- richer prompt-only and audio/music strategy package consistency
- standardized fallback payload shape across every failure case
- iOS-safe display of the broader any-source output surface

## 7. Backward Compatibility Rules

- New fields must be optional first.
- Older clients must survive missing fields.
- Frontend and iOS must treat missing render URLs as non-playable.
- Thumbnail URLs must not be treated as video proof.
- Strategy-only output must remain useful without timestamps or media links.

## 8. Testing Expectations

Every schema change should be tested against:

- video source
- audio source
- music source
- prompt-only source
- Twitch/stream source
- campaign/objective source
- fallback source

Each test should verify:

- JSON shape
- nullable handling
- truthful `rendered_status`
- no fake media URLs
- no forbidden claims

