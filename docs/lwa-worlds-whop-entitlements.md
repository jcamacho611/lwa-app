# LWA Worlds Whop Entitlements

## Purpose

Whop can become the source of paid access and founder passes, but live entitlement changes must wait for verified webhook signatures.

## Plan Keys

| Whop Product | LWA Plan |
| --- | --- |
| Free/demo | free |
| Creator | creator |
| Pro | pro |
| Agency | agency |
| Enterprise/manual | enterprise |
| Founder pass | founder |

## Expected Webhook Events

- membership.created
- membership.updated
- membership.cancelled
- payment.succeeded
- payment.failed
- refund.created

## Rules

- Do not process real Whop webhooks without `WHOP_WEBHOOK_SECRET`.
- Do not trust plan keys from the frontend.
- Store webhook event IDs for idempotency.
- Audit entitlement grants and revokes.
- Keep demo entitlement fallback separate from live Whop access.

## Launch Blockers

- signature verification
- product-to-plan mapping
- webhook replay protection
- entitlement expiration handling
- refund/cancel downgrade behavior
