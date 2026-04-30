# LWA Whop / Entitlement Audit

Last updated: 2026-04-30

## Purpose

This audit protects the launch path by separating three different concepts:

1. **Checkout intent** — a user clicks Whop, Stripe, PayPal, Gumroad, Lemon Squeezy, demo, booking, or contact.
2. **Revenue intent tracking** — the app records a non-authoritative sales signal.
3. **Verified entitlement** — the backend receives and verifies a signed payment/membership webhook, then unlocks access.

LWA must not treat checkout clicks as verified payment.

## Current repo evidence

### Whop checkout URL

`lwa-web/lib/money-links.ts` defines:

- `DEFAULT_WHOP_URL = "https://whop.com/lwa-app/lwa-ai-content-repurposer/"`
- `NEXT_PUBLIC_LWA_WHOP_URL` override support
- `getPrimaryMoneyLink()` fallback to Whop
- UTM tagging through `buildUtmUrl(...)`

This means the frontend can direct users to Whop.

### Other external money links

`lwa-web/lib/money-links.ts` also supports optional public env links for:

- Stripe payment link
- PayPal URL
- Gumroad URL
- Lemon Squeezy URL
- demo form
- affiliate form
- booking URL
- contact URL

These are CTA links only.

### Verified entitlement status

Repo search did not find a clear server-side Whop webhook implementation or authoritative revenue-event handler in this audit pass.

Until verified webhook code exists, LWA should describe the Whop flow as:

> External checkout / access path configured.

Do **not** describe it as:

> Verified subscription enforcement.

## Current safe claim

Allowed:

- LWA can send buyers to the configured Whop checkout/access page.
- LWA can use Whop as the sales/access layer.
- The live app can be used as the customer-facing product URL from Whop when the Railway frontend/backend are healthy.

Not allowed yet unless backend evidence is added:

- Whop payment verified in-app.
- Whop membership automatically unlocks paid access.
- Subscription active.
- Paid entitlement enforced from Whop webhook.
- Payout-ready marketplace.

## Required before verified paid access

Before the app can enforce paid access from Whop, add:

1. Whop webhook endpoint in backend.
2. Webhook signature verification.
3. Idempotent webhook event storage.
4. Membership/payment status mapping.
5. Entitlement reconciliation function.
6. Clear plan/credit update rules.
7. Tests for valid webhook, invalid signature, replayed event, membership invalidated, and entitlement downgrade.
8. Admin/debug view or log path for webhook delivery failures.

## Required before marketplace payouts

Do not add live seller payouts until all of the following exist:

- verified payment webhooks
- idempotency table/store
- append-only ledger
- seller KYC plan
- payout holds
- dispute process
- refund policy
- admin takedown/review queue
- fraud review rules
- no guaranteed income copy

## Recommended next implementation slice

### Slice: Whop webhook audit-only PR

Before writing code, inspect:

- backend route registration
- config/env pattern
- auth/entitlement modules
- existing plan/credit logic
- frontend money CTA flow
- Railway env docs

Output:

- exact files involved
- minimum webhook shape
- required env vars
- entitlement mapping
- test plan

### Slice after audit: Whop verified webhook MVP

Add only:

- `WHOP_WEBHOOK_SECRET` config
- backend route for signed webhook events
- idempotency guard
- entitlement update function
- tests

Do not add marketplace payouts in the same PR.

## Launch stance

For public launch, keep `FREE_LAUNCH_MODE` and external Whop CTA compatible:

- Free launch lets users try the product.
- Whop CTA lets buyers purchase or join access.
- Verified paid gating comes after signed webhook implementation.

This keeps sales moving without lying to users or breaking the MVP.
