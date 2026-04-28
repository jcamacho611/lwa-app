# LWA Intelligence Table Map

## Purpose
This document maps the unified backend intelligence layer that powers LWA's retention-weighted clipping system.

## Data Sources
- `lwa-backend/app/data/intelligence_seed/*`
- `lwa-backend/app/data/viral_intelligence/*`
- `lwa-backend/app/data/twitch_seed/*` when present
- runtime JSONL logs under `lwa-backend/app/data/intelligence_runtime/*`
- capability data in `lwa-backend/app/data/capabilities/lwa_capabilities.json`

## Seed Tables
- `viral_signal_rules.json`
- `platform_rules.json`
- `platform_modifiers.json`
- `content_category_rules.json`
- `hook_formula_library.json`
- `caption_style_presets.json`
- `thumbnail_rules.json`
- `clip_scoring_weights.json`
- `frontend_badge_rules.json`
- `competitor_matrix.json`
- `sales_positioning_matrix.json`
- `twitch_signal_mapping.json`
- `campaign_readiness_rules.json`

## Runtime Logs
- `feedback.jsonl`
- `performance.jsonl`
- `events.jsonl`

These are learning inputs only. They do not overwrite seed tables automatically.

## Registry Layer
- `lwa-backend/app/services/intelligence_registry.py`

This layer:
- loads product, viral, Twitch, capability, and runtime summaries
- validates signal weights and references
- builds unified platform profiles
- builds unified category profiles
- produces clip intelligence context for scoring
- guards public claims
- suggests future weight adjustments without mutating seed files

## Attention Compiler Layer
- `lwa-backend/app/services/attention_compiler.py`

This layer:
- derives fallback signals
- normalizes platform weights
- scores clips on a 0-100 scale
- produces `ScoreBreakdown`
- assigns rank and post rank
- generates hook variants
- resolves caption presets
- determines platform compatibility
- determines frontend badges

## Generation Integration
- `lwa-backend/app/services/clip_service.py`

Attention compilation runs after clip candidates are created and before final clip packages are returned.

## API Surface
- `GET /v1/intelligence`
- `GET /v1/intelligence/viral-signals`
- `GET /v1/intelligence/platform-profiles`
- `GET /v1/intelligence/platform-profiles/{platform}`
- `GET /v1/intelligence/category-profiles`
- `GET /v1/intelligence/category-profiles/{category}`
- `GET /v1/intelligence/hook-formulas`
- `GET /v1/intelligence/caption-styles`
- `GET /v1/intelligence/frontend-badges`
- `GET /v1/intelligence/sales-positioning`
- `POST /v1/intelligence/claim-check`

## Frontend / iOS Future Use
These backend fields are now available for later surfacing:
- `signals`
- `score_breakdown`
- `rank`
- `post_rank`
- `is_best_clip`
- `frontend_badges`
- `platform_compatibility`
- `caption_preset`
- `hooks`
- `detected_category`
- `target_platform`

## Claim Safety Guard
Public copy must not claim:
- guaranteed viral
- guaranteed views
- guaranteed revenue
- guaranteed payout
- direct posting
- Whop automation that is not implemented
- private/login-gated bypass
- full Twitch live ingestion
- full workspace/team support

The registry keeps those checks internal through `public_claim_guard(...)`.

## Twitch Mapping
`twitch_signal_mapping.json` connects Twitch-first signals such as chat spikes, repeated phrases, clip markers, and topic shifts to the viral signal framework.

## Campaign / Whop Mapping
`campaign_readiness_rules.json` marks the conditions for campaign-ready clips without claiming Whop submission automation.

## What Is Live Now
- seed tables load
- unified registry loads
- validation runs
- intelligence endpoints respond
- Attention Compiler uses the unified layer
- fallback scoring stays distributed

## What Is Future-Ready Only
- frontend score panel
- iOS score transparency UI
- automated feedback-driven weight tuning
- full Twitch ingestion
- full campaign submission automation

## Verification Commands
```bash
cd /Users/bdm/LWA/lwa-app
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend
python3 -m unittest discover -s tests
cd ..
git diff --check
```
