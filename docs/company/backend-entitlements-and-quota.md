# Backend Entitlements And Quota

## Purpose

This document describes the backend plan, quota, and entitlement behavior that is actually implemented today.

It is the operator source of truth for:

- free access
- API-key upgrades
- authenticated user plan handling
- quota exhaustion behavior
- Whop verification foundation status

## Current State

Implemented now:

- server-side quota reservation and release
- free / pro / scale plan definitions
- API-key based plan unlocks
- authenticated user plan resolution
- structured quota-exceeded responses
- credits remaining in processing summary
- feature flags returned from the backend

Future-ready, not complete:

- server-side Whop membership verification
- durable billing-grade entitlement sync
- workspace/team entitlements
- campaign-linked usage billing

## Resolution Order

The backend resolves plan access in this order:

1. valid Scale API key
2. valid Pro API key
3. authenticated user plan
4. stable client ID header
5. remote IP fallback

## Current Plan Defaults

These are the current backend defaults unless overridden by env vars:

- Free:
  - daily limit: `LWA_FREE_DAILY_LIMIT`
  - default fallback if no paid key or authenticated paid user exists
- Pro:
  - daily limit: `LWA_PRO_DAILY_LIMIT`
- Scale:
  - daily limit: `LWA_SCALE_DAILY_LIMIT`

Current default env-backed values:

- `LWA_FREE_DAILY_LIMIT=2` or the current deployed override
- `LWA_PRO_DAILY_LIMIT=25`
- `LWA_SCALE_DAILY_LIMIT=100`

## Current Feature Flags

Feature flags are returned by the backend and should be treated as backend truth.

Examples currently used:

- `clip_limit`
- `alt_hooks`
- `campaign_mode`
- `packaging_profiles`
- `history_limit`
- `caption_editor`
- `timeline_editor`
- `wallet_view`
- `posting_queue`
- `max_uploads_per_day`
- `max_generations_per_day`
- `premium_exports`
- `priority_processing`

Operator note:

- do not turn a flag on in docs or client copy unless the backend behavior tied to it is actually present
- some flags represent controlled access to partially shipped surfaces rather than fully mature product categories

## Structured Quota Errors

When the current plan is exhausted, the backend raises a structured `402` response with:

- `code`
- `message`
- `plan`
- `plan_code`
- `credits_remaining`
- `upgrade_hint`

This is designed so web and iOS can handle quota exhaustion without parsing free-form strings.

## Usage Store

Usage tracking is file-backed today.

Env var:

- `LWA_USAGE_STORE_PATH`

Recommended Railway path:

```env
LWA_USAGE_STORE_PATH=/data/lwa-usage.json
```

## Required / Useful Env Vars

```env
LWA_CLIENT_ID_HEADER_NAME=x-lwa-client-id
LWA_FREE_DAILY_LIMIT=2
LWA_PRO_DAILY_LIMIT=25
LWA_SCALE_DAILY_LIMIT=100
LWA_PRO_API_KEYS=comma,separated,keys
LWA_SCALE_API_KEYS=comma,separated,keys
LWA_USAGE_STORE_PATH=/data/lwa-usage.json
```

## Whop Verification Foundation

Current truth:

- Whop verification is foundation-only
- it is disabled by default
- free mode and API-key mode remain the safe fallback

Current env vars:

```env
LWA_ENABLE_WHOP_VERIFICATION=false
WHOP_API_KEY=
WHOP_COMPANY_ID=
WHOP_PRODUCT_ID=
WHOP_WEBHOOK_SECRET=
```

Current behavior:

- if `LWA_ENABLE_WHOP_VERIFICATION=false`, backend continues using free/API-key entitlements
- if `LWA_ENABLE_WHOP_VERIFICATION=true` but required Whop vars are missing, health status reports `missing-config`
- no live Whop membership verification is claimed until the API integration is tested end-to-end

## What Is Not Implemented Yet

- no live Whop membership token verification flow
- no webhook-driven entitlement sync
- no billing dispute/reconciliation flow
- no persistent organization/workspace entitlement model

## Operator Guidance

- keep free access limited enough to avoid runaway cost
- keep paid API keys server-side only
- do not trust client-only premium claims
- do not market Whop verification as live until a real verification path is wired and tested
