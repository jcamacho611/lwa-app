# LWA Marketplace Architecture Spec

## Source

Derived from the Master Council Report uploaded in the project thread.

## Status

Planning artifact. Do not treat this as shipped runtime.

## Goal

Build a marketplace for clip templates, hook packs, caption presets, brand kits, prompt packs, campaign work, and creator/operator services.

## V1 guardrail

The first marketplace implementation should be a dark/internal scaffold before live money movement.

## Core objects

- users
- seller accounts
- products/listings
- product assets
- orders
- payouts
- disputes
- ledger entries
- webhook events

## Backend route targets

- `POST /sellers/onboard`
- `GET /sellers/me`
- `POST /products`
- `PATCH /products/{id}`
- `GET /products/{id}`
- `GET /marketplace`
- `POST /orders`
- `GET /orders/{id}`
- `POST /webhooks/stripe`
- `POST /webhooks/whop`
- `POST /disputes`
- `GET /sellers/{id}/payouts`
- `POST /admin/takedown`

## Frontend route targets

- `/marketplace`
- `/marketplace/[id]`
- `/sell/onboard`
- `/sell/products`
- `/sell/products/new`
- `/disputes/new`
- `/disputes/[id]`
- `/admin/disputes`

## Safety requirements before live marketplace money

- signed provider webhooks
- idempotent event handling
- ledger/accounting record
- seller review or KYC plan
- payout hold logic
- refund policy
- dispute flow
- admin review/takedown queue
- banned category policy
- no guaranteed earnings copy

## Implementation order

1. Compatibility audit against actual repo persistence layer.
2. Dark marketplace browse shell.
3. Seller dashboard shell.
4. Admin review queue.
5. Webhook verification framework.
6. Ledger/account record.
7. Sandbox checkout.
8. Payout workflow only after review controls exist.

## Claim rule

Use: Earnings vary. No guarantee of income.

Do not claim payouts, verified payments, seller income, or marketplace availability until runtime proves it.
