# LWA Revenue And Monetization Plan

## Current monetization foundation

The safe first layer is revenue-intent tracking.

Revenue-intent events are not payment verification.

They help track:

- upgrade clicks
- checkout starts
- demo requests
- affiliate/referral interest
- quota-blocked upgrade pressure
- booking/contact clicks

## Non-authoritative rule

Revenue events must remain non-authoritative.

They must not:

- unlock paid access
- activate subscriptions
- verify payment
- trigger payouts
- confirm revenue

Verified payment state must come later from signed provider webhooks.

## Safe funnel

1. User hits a generation/quota/value wall.
2. App shows upgrade/demo/contact CTA.
3. Frontend sends revenue-intent event if implemented.
4. Backend logs sanitized non-authoritative event if the endpoint exists.
5. User goes to checkout/demo/contact path.
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

## Pricing direction

Draft only:

- Free Launch: limited public usage.
- Creator: core clipping.
- Pro: more clips, stronger captions/render controls.
- Scale: agencies/operators.
- Marketplace: future take rate.

## Required before live marketplace money

- verified webhooks
- idempotency
- ledger
- seller KYC
- payout holds
- dispute system
- takedown/admin queue
- refund policy
- banned category policy
- claim safety copy

## Current verification rule

Codex must verify actual repo evidence before saying revenue-event tracking is installed.

If the route/logger exists, preserve it.

If it does not exist, do not add it unless the selected slice is monetization/revenue tracking.
