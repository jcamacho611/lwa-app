# LWA Worlds Fraud Policy Draft

## Purpose

Track and review behavior that could manipulate campaign outcomes, payouts, credits, referrals, or marketplace trust.

## Review Targets

- duplicate submissions
- fake buyer or seller activity
- suspicious referrals
- chargeback abuse
- payout manipulation
- copied UGC
- coordinated review abuse
- rights claim evasion

## Fraud States

- open
- in_review
- cleared
- confirmed
- escalated

## Payout Safety

Confirmed fraud flags and unresolved disputes must block payout movement. MVP payout records remain placeholders and must not be described as paid unless a real payout rail is implemented and verified.

## Audit Rule

Every fraud flag creation and review action must create an admin audit entry.
