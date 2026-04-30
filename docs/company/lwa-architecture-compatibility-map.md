# LWA Architecture Compatibility Map

## Purpose

This document keeps future implementation aligned with the real repo instead of blindly copying assumptions from planning files.

The existing repository is the source of truth. Planning documents are requirements and strategy, not proof that a module already exists.

## Repo path compatibility

Some planning docs mention:

- `apps/backend`
- `apps/web`

Current repo work has used:

- `lwa-backend`
- `lwa-web`
- `lwa-ios`
- `tools`
- `docs/company`

Codex must adapt master prompts to the real paths. Do not create duplicate app folders unless a repo audit proves the structure changed intentionally.

## Backend compatibility checklist

Before backend edits, inspect:

- app entrypoint
- route registration
- schema/model locations
- config/settings style
- auth/dependency style
- test runner style
- database/store pattern
- storage/log path style
- entitlement/quota behavior
- asset retention behavior
- source ingestion behavior
- generated asset URL behavior

## Frontend compatibility checklist

Before frontend edits, inspect:

- Next.js app router structure
- layout files
- route names and navigation
- type definitions
- API client utilities
- global CSS/design tokens
- component naming style
- generate/workspace surface
- homepage/generate/dashboard split

## Database compatibility checklist

Do not assume SQLAlchemy, SQLModel, Alembic, JSON store, Postgres, SQLite, or Redis.

Audit first.

If the repo does not already use Alembic, do not create migrations without a dedicated migration task.

Marketplace, Realms, ledger, and payout schemas in planning docs are target architecture. They must be adapted to the existing persistence path.

## Payment compatibility checklist

Do not implement live money movement until the needed safety layers exist.

Required before live marketplace money:

- marketplace model/store
- verified signed webhooks
- idempotency by provider event id
- append-only ledger or equivalent
- admin takedown/dispute flow
- refund policy
- banned category policy
- claim safety copy
- payout holds/fraud review

## Revenue event compatibility checklist

Revenue intent tracking, if present, is not payment verification.

It may track upgrade interest, checkout starts, demo requests, referral interest, quota-blocked upgrade pressure, and contact/booking clicks.

It must not unlock access, activate subscriptions, verify payment, trigger payouts, or confirm revenue.

## Social API compatibility checklist

Do not store provider tokens unless encryption, revocation, OAuth state verification, scope docs, and provider status are clear.

Do not implement direct posting until platform permissions/review are confirmed.

## Polymarket compatibility checklist

Polymarket may only be used as read-only cultural trend metadata. No betting, trading, wagering UI, or financial advice.

## Blockchain compatibility checklist

Early work is limited to optional provenance planning and off-chain proof records.

Do not add live chain features until off-chain issuance, proof format, legal copy, user consent, and explicit approval exist.

## iOS compatibility checklist

Do not touch `lwa-ios/` unless the active task explicitly approves iOS.

## Runtime safety rule

Docs may be broad. Code must be narrow.

One implementation slice at a time:

1. audit
2. plan
3. implement smallest compatible change
4. test
5. commit
6. update implementation status map
