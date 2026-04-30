# LWA Marketplace Scaffold

## Status

This is a backend scaffold for future marketplace work. It is not a live seller marketplace.

## Current files

- `lwa-backend/app/services/marketplace_core.py`
- `lwa-backend/tests/test_marketplace_core.py`

## Engineering rules

- Use integer cents for money values.
- Keep listing validation explicit.
- Keep restricted categories blocked.
- Keep public disclosure text attached to listing output.
- Keep checkout, transfers, webhooks, disputes, and ledger work in later dedicated PRs.

## Future order

1. Database schema.
2. Listing routes.
3. Order routes.
4. Webhook inbox.
5. Ledger records.
6. Dispute records.
7. Stripe Connect integration.
8. Whop rail later.

## Claim boundary

Do not describe this scaffold as a live marketplace until the actual routes, storage, checkout, webhook, ledger, and operator review flows are implemented and verified.
