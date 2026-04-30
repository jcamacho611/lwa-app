# LWA Worlds Schema Plan

## Purpose

This schema supports the LWA Worlds vertical slice:

AI clip -> marketplace campaign -> submission -> review -> earnings -> XP -> badge -> ledger -> admin.

## Current Migration Status

This repo does not currently include Alembic or SQLModel. LWA Worlds is wired through the existing local SQLite store pattern used by the backend. The database path is `LWA_WORLDS_DB_PATH`, defaulting to `generated/lwa-worlds.sqlite3` locally or the Railway volume when `RAILWAY_VOLUME_MOUNT_PATH` is set.

## Tables

### marketplace_campaigns

- public_id
- title
- description
- buyer_user_id
- target_platform
- source_type
- budget_amount
- currency
- platform_fee_percent
- clip_count
- deadline
- status
- rights_required
- created_at
- updated_at

### campaign_submissions

- public_id
- campaign_public_id
- clipper_user_id
- title
- hook
- caption
- asset_url
- status
- estimated_earnings_amount
- currency
- review_note
- rights_confirmed
- created_at
- updated_at

### user_world_profiles

- user_id
- display_name
- class_name
- faction
- level
- xp
- next_level_xp
- creator_reputation
- clipper_reputation
- marketplace_reputation
- created_at
- updated_at

### badges

- public_id
- name
- tier
- description
- lore
- created_at

### user_badges

- user_id
- badge_public_id
- unlocked_at

### internal_ledger_entries

- public_id
- user_id
- event_type
- label
- amount
- currency
- xp
- reputation
- status
- reference_id
- created_at

### admin_audit_actions

- public_id
- actor_user_id
- action_type
- target_type
- target_public_id
- before_state
- after_state
- note
- created_at

### api_integration_statuses

- integration_key
- name
- category
- status
- description
- admin_only
- updated_at

### reputation_events

- public_id
- user_id
- source_type
- source_public_id
- xp
- creator_reputation
- clipper_reputation
- marketplace_reputation
- reason
- created_at

## Required Indexes

- public_id primary keys
- user_id indexes where read paths need them
- campaign_public_id index for submissions
- created_at ordering support for campaigns, ledger, and audits
- target_public_id index for audits

## Production Notes

- Replace `demo_user` with authenticated user IDs.
- Add foreign keys after confirming existing user and campaign ownership rules.
- Keep ledger append-only.
- Keep admin audit logs append-only.
- Add moderation before enabling public UGC.
- Do not apply a production migration until reviewed against the active database.
