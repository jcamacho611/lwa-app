# LWA CHUNK 4 — SQL MIGRATIONS AND REPOSITORY LAYER

This chunk continues the LWA algorithm stack with database migration order, repository responsibilities, guard queries, and implementation prompts. It is additive planning only and does not mark unfinished systems as live.

## Current product truth

- LWA has a working clipping MVP.
- Public URL generation and clip packs exist.
- Director Brain metadata and rendered-vs-strategy-only flow are part of the product direction.
- Upload pipeline, full editor, direct social posting, marketplace, Signal Realms, blockchain provenance, and full iOS rebuild require separate feature-flagged implementation.

## Core database rules

```text
- Use UUID primary keys.
- Use integer cents for all money fields.
- Use JSONB for flexible algorithm details.
- Keep important searchable fields as normal columns.
- Webhook/event ingestion must be idempotent.
- Strategy-only clips must not have playable asset URLs.
- Rendered clips must have real playable/downloadable asset records.
- Long media processing should not hold open database transactions.
```

## Migration order

```text
001_feature_flags.sql
002_upload_assets.sql
003_generation_core.sql
004_director_brain_scores.sql
005_clip_results_assets.sql
006_campaigns.sql
007_learning_usage_webhooks.sql
008_editor_tables.sql
009_social_tables.sql
010_marketplace_tables.sql
011_realms_tables.sql
012_proof_tables.sql
013_operator_indexes.sql
014_rls_policies.sql
```

## Repository structure

```text
lwa-backend/app/db/repositories/
  feature_flags_repo.py
  source_assets_repo.py
  upload_assets_repo.py
  generation_jobs_repo.py
  transcript_repo.py
  moment_candidates_repo.py
  scores_repo.py
  clip_results_repo.py
  campaign_repo.py
  learning_repo.py
  usage_repo.py
  webhook_events_repo.py
  editor_repo.py
  social_repo.py
  marketplace_repo.py
  realms_repo.py
  proof_repo.py
  operator_repo.py
```

## Repository rules

Repositories should only read and write data. Algorithm services should make decisions.

```python
async def create_record(session, payload):
    ...

async def get_record(session, record_id):
    ...

async def update_record(session, record_id, patch):
    ...

async def list_records_for_user(session, user_id, limit=50):
    ...
```

## Transaction boundaries

```text
Generation phase 1: create source asset and job.
Generation phase 2: save transcript and segment signals.
Generation phase 3: save moment candidates and scores.
Generation phase 4: save packages and clip results.
Generation phase 5: save assets and quality gate results.
Generation phase 6: update final job summary.
```

Media rendering should happen outside a long database transaction. Persist state, process media, then reopen a transaction for result updates.

## Feature flags table

```sql
CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feature_key TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned',
    is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    visible_to_users BOOLEAN NOT NULL DEFAULT FALSE,
    visible_to_admins BOOLEAN NOT NULL DEFAULT TRUE,
    visible_to_beta_users BOOLEAN NOT NULL DEFAULT FALSE,
    rollout_percent INTEGER NOT NULL DEFAULT 0 CHECK (rollout_percent BETWEEN 0 AND 100),
    description TEXT NULL,
    user_facing_label TEXT NULL,
    internal_notes TEXT NULL,
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_feature_flags_key ON feature_flags(feature_key);
CREATE INDEX IF NOT EXISTS idx_feature_flags_status ON feature_flags(status);
```

## Feature flag seed

```sql
INSERT INTO feature_flags (feature_key, display_name, status, is_enabled, visible_to_users, visible_to_admins, visible_to_beta_users, user_facing_label)
VALUES
('ai_clipping', 'AI Clipping Engine', 'live', TRUE, TRUE, TRUE, TRUE, 'Live'),
('director_brain', 'Director Brain', 'beta', TRUE, TRUE, TRUE, TRUE, 'Beta'),
('upload_pipeline', 'Upload Pipeline', 'planned', FALSE, FALSE, TRUE, FALSE, 'Planned'),
('full_editor', 'Full Editor', 'planned', FALSE, FALSE, TRUE, FALSE, 'Planned'),
('campaign_manager', 'Campaign Manager', 'scaffolded', FALSE, FALSE, TRUE, TRUE, 'Beta soon'),
('direct_social_posting', 'Direct Social Posting', 'planned', FALSE, FALSE, TRUE, FALSE, 'Planned'),
('marketplace', 'Creator Marketplace', 'planned', FALSE, FALSE, TRUE, FALSE, 'Planned'),
('rpg_realms', 'Signal Realms RPG', 'planned', FALSE, FALSE, TRUE, FALSE, 'Planned'),
('blockchain_provenance', 'Proof of Creation', 'planned', FALSE, FALSE, TRUE, FALSE, 'Optional future'),
('ios_rebuild', 'Full iOS Rebuild', 'planned', FALSE, FALSE, TRUE, FALSE, 'Planned')
ON CONFLICT (feature_key) DO NOTHING;
```

## Upload assets table

```sql
CREATE TABLE IF NOT EXISTS upload_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL,
    creator_profile_id UUID NULL,
    upload_source TEXT NOT NULL DEFAULT 'local_file',
    original_filename TEXT NOT NULL,
    storage_bucket TEXT NOT NULL,
    storage_key TEXT NOT NULL UNIQUE,
    public_url TEXT NULL,
    signed_url_expires_at TIMESTAMPTZ NULL,
    mime_type TEXT NULL,
    file_size_bytes BIGINT NULL,
    duration_seconds INTEGER NULL,
    width INTEGER NULL,
    height INTEGER NULL,
    frame_rate NUMERIC(8,3) NULL,
    upload_status TEXT NOT NULL DEFAULT 'requested',
    scan_status TEXT NOT NULL DEFAULT 'pending',
    checksum_sha256 TEXT NULL,
    source_asset_id UUID NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_message TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_upload_assets_user ON upload_assets(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_upload_assets_status ON upload_assets(upload_status);
CREATE INDEX IF NOT EXISTS idx_upload_assets_checksum ON upload_assets(checksum_sha256);
```

## Generation job update query

```sql
UPDATE generation_jobs
SET status = $2,
    processing_summary = processing_summary || $3::jsonb,
    updated_at = now()
WHERE id = $1
RETURNING *;
```

## Clip result guard query: rendered clips require assets

```sql
SELECT cr.id
FROM clip_results cr
LEFT JOIN clip_assets ca ON ca.clip_result_id = cr.id
WHERE cr.render_status = 'rendered'
GROUP BY cr.id
HAVING COUNT(ca.id) FILTER (WHERE ca.asset_type IN ('edited_clip', 'preview')) = 0;
```

Expected result: zero rows.

## Clip result guard query: strategy-only has no playable asset

```sql
SELECT cr.id
FROM clip_results cr
JOIN clip_assets ca ON ca.clip_result_id = cr.id
WHERE cr.strategy_only = TRUE
  AND cr.render_status = 'strategy_only'
  AND ca.asset_type IN ('edited_clip', 'preview', 'raw_clip');
```

Expected result: zero rows.

## Operator queries

Failed or partial jobs:

```sql
SELECT id, request_id, source_url, status, error_code, error_message, created_at
FROM generation_jobs
WHERE status IN ('failed', 'fallback', 'partial')
ORDER BY created_at DESC
LIMIT 100;
```

Render state report:

```sql
SELECT
    date_trunc('day', created_at) AS day,
    COUNT(*) AS total_clips,
    COUNT(*) FILTER (WHERE render_status = 'rendered') AS rendered,
    COUNT(*) FILTER (WHERE render_status = 'raw_only') AS raw_only,
    COUNT(*) FILTER (WHERE render_status = 'strategy_only') AS strategy_only,
    COUNT(*) FILTER (WHERE render_status = 'failed') AS failed
FROM clip_results
GROUP BY day
ORDER BY day DESC;
```

## Codex prompt

```text
Implement Chunk 4 only.

Task:
Add safe SQL migration files and repository scaffolds for feature flags, upload assets, generation lifecycle, clip result guards, and operator queries.

Rules:
- Preserve existing backend routes.
- Additive changes only.
- Do not touch lwa-web.
- Do not touch lwa-ios.
- Do not mark planned features as live.
- Do not create playable URLs without real assets.

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant backend tests
```
