# Backend Whop Verification Foundation

## Current truth

Whop verification remains foundation-only.

The backend can report whether Whop verification is:

- disabled
- missing config
- configured

Free mode and API-key plan mode continue to work without Whop.

## Env vars

```env
LWA_ENABLE_WHOP_VERIFICATION=false
WHOP_API_KEY=
WHOP_COMPANY_ID=
WHOP_PRODUCT_ID=
WHOP_WEBHOOK_SECRET=
```

## Behavior

- Disabled by default.
- If disabled, the backend uses existing free / pro / scale entitlement logic.
- If enabled but missing required config, health reporting reflects that state.
- Client-side plan claims are never trusted.

## What is not implemented

- real membership verification against Whop
- webhook-driven entitlement sync
- campaign import or submission flows

## Safe claims

Say:

- Whop verification foundation exists on the backend.

Do not say:

- Whop verification is fully live
- campaign submission is wired
