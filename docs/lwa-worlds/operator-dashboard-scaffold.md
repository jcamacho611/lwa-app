# Operator Dashboard Scaffold

## Status

This is a backend scaffold for a future operator dashboard. It summarizes existing LWA run data only.

It does not create fake social analytics, fake posting status, fake marketplace payouts, or unverified external metrics.

## Current files

- `lwa-backend/app/services/operator_dashboard_core.py`
- `lwa-backend/tests/test_operator_dashboard_core.py`

## Current primitives

- run summary helper
- rendered versus strategy-only counts
- best-score summary
- attention-needed card builder
- operator disclosure helper

## Rules

- Use real LWA run/result data only.
- Do not invent external social performance.
- Do not imply direct social posting is live.
- Do not imply marketplace payouts are live.
- Empty states must be honest.

## Future order

1. Connect to durable run history.
2. Add read-only dashboard route.
3. Add frontend operator page.
4. Add admin gating.
5. Add social metrics only after verified integrations are live.
6. Add trust and safety queue after marketplace routes exist.

## Claim boundary

Do not describe the operator dashboard as a full multi-account social dashboard until social integrations, durable account links, scheduled posts, and real metrics exist.
