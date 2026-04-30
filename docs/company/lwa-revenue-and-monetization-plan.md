# LWA Revenue And Monetization Plan

## Status

This is a planning and control document for revenue work. It does not claim any payment provider is live unless repo evidence proves it.

## Current foundation

The safest first layer is revenue-intent tracking.

Revenue-intent events are product analytics and operator signals. They are not payment verification.

They may track:

- upgrade clicks
- checkout starts
- demo requests
- affiliate or referral interest
- quota-blocked upgrade pressure
- booking or contact clicks

## Non-authoritative rule

Revenue-intent events must not unlock access, activate subscriptions, verify payment, trigger payout state, or confirm revenue.

Verified payment state must come later from signed provider webhooks.

## Safe funnel

1. User hits a generation, quota, or value wall.
2. App shows upgrade, demo, or contact CTA.
3. Frontend sends revenue-intent event if implemented.
4. Backend logs sanitized event if the endpoint exists.
5. User goes to checkout, demo, or contact path.
6. Future signed webhook verifies actual payment.
7. Entitlement changes only after verified payment or explicit admin grant.

## Future payment integrations

Future slices:

1. Stripe webhook verification.
2. Whop webhook verification.
3. Lemon Squeezy webhook verification.
4. Gumroad webhook verification.
5. PayPal verification if needed.
6. Entitlement reconciliation.
7. Billing audit view.

## Draft pricing direction

- Free Launch: limited public usage.
- Creator: core clipping.
- Pro: more clips and stronger controls.
- Scale: agency/operator workflow.
- Marketplace: future take rate after trust and payment controls exist.

## Required before live marketplace money

- verified webhooks
- idempotency
- ledger or equivalent account record
- seller review/KYC plan
- payout holds
- dispute process
- takedown/admin queue
- refund policy
- banned category policy
- claim safety copy

## Current verification rule

Codex must verify actual repo evidence before saying revenue-event tracking is installed.

If the route/logger exists, preserve it.

If it does not exist, do not add it unless the selected slice is monetization/revenue tracking.
