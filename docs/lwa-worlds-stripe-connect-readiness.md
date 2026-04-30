# LWA Worlds Stripe Connect Readiness

## Current State

Stripe Connect is not enabled in the MVP. The app exposes readiness status only and does not create transfers.

## Required Before Enabling

- Stripe Connect platform setup
- connected account onboarding
- KYC/tax requirements
- webhook verification
- payout idempotency
- dispute holds
- fraud holds
- refund/chargeback process
- reconciliation reports
- admin payout review
- legal and finance review

## Required Env Vars

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_CONNECT_CLIENT_ID`

## Payout States

- requested
- pending_review
- blocked
- held
- cancelled

## Forbidden Transitions

- approved earnings directly to paid
- disputed earnings to payable
- held earnings to paid
- payout placeholder to real transfer

## User-Facing Copy

Allowed:

- "Payouts are not enabled yet."
- "Approved earnings remain under review until payout controls are complete."
- "Payout eligibility may be blocked by disputes, refunds, fraud checks, rights claims, or policy review."

Not allowed:

- "Instant payout"
- "Guaranteed payout"
- "Automatic payout"
- "Guaranteed earnings"
