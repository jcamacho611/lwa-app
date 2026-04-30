# LWA Worlds Billing And Entitlements

## Purpose

This foundation tracks plans, entitlements, credits, earnings, and payout placeholders without processing real payments.

## Phase 1 Objects

- billing plans
- user entitlements
- credit balances
- credit transactions
- usage events
- earnings accounts
- earning events
- payout placeholders
- webhook event records

## Safety Rules

- Do not process real payouts.
- Do not activate Stripe Connect transfers.
- Do not process Whop webhooks without signature verification.
- Do not promise guaranteed earnings.
- Do not treat approved earnings as paid.
- Audit entitlement grants, credit grants, credit spend, earning approval, and payout placeholder requests.

## Plan Keys

- free
- creator
- pro
- agency
- enterprise
- founder

## Credits

Credits are a usage-control foundation for AI and generation workflows.

Credits can be:

- granted by plan
- granted manually by admin
- spent by a feature route
- refunded later
- audited through ledger and credit transactions

## Earnings

Marketplace earnings are tracked as states:

- estimated
- pending review
- approved
- payable
- processing
- paid
- failed
- held
- disputed
- refunded
- cancelled

Approved earnings are not payouts. Payout eligibility remains blocked until payout controls are production-ready.

## Payout Placeholders

Payout placeholders show future payout intent without moving money.

They are blocked until:

- Stripe Connect is implemented
- KYC/tax controls exist
- dispute holds exist
- fraud holds exist
- payout idempotency exists
- reconciliation exists
