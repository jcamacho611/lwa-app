# LWA Railway Service Plan

## Purpose
This Issue #21 control document prevents Railway service sprawl. LWA should run only the services that current capabilities require. Future services are allowed only when a capability has moved beyond docs, seed data, or UI ambition into real runtime need.

## Claim Safety

Allowed public claims:

- helps prepare clips
- helps rank moments
- returns hooks, captions, timestamps, packaging copy, and score context
- rendered clips when available
- strategy-only fallback when rendering is unavailable
- creator-ready clip packages
- manual campaign preparation
- upgrade/access through Whop where configured

Forbidden public claims:

- guaranteed viral performance, views, revenue, or payout
- auto-posting to TikTok, Instagram, YouTube, or any social platform
- Whop campaign submission automation
- private video bypass
- full editor replacement
- unlimited clips
- automatic payout tracking
- Redis, Postgres, worker fleet, scheduler, webhooks, Cloudinary/R2, or other infrastructure as live unless implemented and verified

## Current Services

| Service | Status | Purpose | Should own | Should not own | Capabilities served |
| --- | --- | --- | --- | --- | --- |
| frontend | CURRENT | Customer-facing web app, clip studio UI, source input, result display, upgrade CTA. | Web UI, static/Next app behavior, source form, rendered/strategy presentation, upgrade links. | FFmpeg, yt-dlp, OpenAI secrets, Whop secret verification, generated media storage decisions, entitlement truth. | Source input, rendered lane, strategy lane, lead best clip, packaging rail, upload UI, score transparency surface. |
| backend | CURRENT | FastAPI API for job creation, AI/clip generation, video processing, generated asset serving, quotas/entitlements, and retention cleanup. | `/health`, `/generate`, `/v1/jobs`, `/v1/trends` if present, `/generated` serving, upload endpoint if implemented, asset retention, entitlement logic, fallback generation. | Unlimited long-running render jobs, permanent media library, massive batch queues, high-volume scheduled jobs, webhook fanout at scale. | Public URL clipping, upload-first clipping, Attention Compiler scoring, strategy fallback, rendered assets, export metadata, quotas, generated asset cleanup. |

Current services only: `frontend` and `backend`.

Do not add services for appearance. Service creation must be tied to a capability trigger below.

## Future Service Rules

### `lwa-worker-render`

Purpose:

- heavy FFmpeg rendering
- caption burn-in
- thumbnail generation
- multi-clip exports
- batch rendering

Create when:

- render jobs block API responsiveness
- queue wait time becomes a user problem
- multiple users generate clips concurrently enough to spike backend CPU/memory
- render failure/retry needs isolation
- batch exports or caption burn-in profiles become real user workflows

Capabilities supported:

- high-volume clipping
- edited clip assets
- caption burn-in profiles
- export profiles
- thumbnail generation
- batch exports

Why it should not exist yet:

- current MVP can keep basic rendering/fallback paths on the backend
- no external queue is established for render dispatch
- render volume is not proven enough to split runtime

Required env vars / dependencies:

- generated asset directory or shared object storage path
- queue/broker dependency if async dispatch is needed
- FFmpeg path and render profile config
- backend callback or shared job store

Risks:

- duplicate render state between API and worker
- orphaned assets if retention is not shared
- queue failures hiding strategy-only fallback

Owner role:

- Video Processing Lead

Go/no-go rule:

- Go only when render work measurably harms backend responsiveness or retry isolation is required. No-go while backend handles render volume safely.

### `lwa-worker-ingest`

Purpose:

- source download and ingestion
- yt-dlp heavy operations
- upload preparation
- source validation
- future authorized connector ingest

Create when:

- source downloading blocks backend responsiveness
- multiple long sources queue up
- uploads or source ingest need retry isolation
- platform-specific ingest grows complex
- authorized import flows require connector-specific workers

Capabilities supported:

- public URL clipping at higher volume
- upload-first source normalization
- authorized imports
- future live Twitch ingestion

Why it should not exist yet:

- URL ingest remains simple enough for the backend
- no proven queue pressure exists
- private/login-gated bypass must not be built

Required env vars / dependencies:

- temp/source directory
- upload/generated storage paths
- yt-dlp/FFmpeg paths where needed
- queue/broker dependency if async dispatch is needed
- source validation policy

Risks:

- accidental private-source bypass claims
- duplicated upload retention behavior
- source downloads consuming volume unexpectedly

Owner role:

- Backend Systems Lead

Go/no-go rule:

- Go only when ingest blocks API requests or authorized imports need isolated retries. No-go for simple beta URL/upload handling.

### `lwa-scheduler`

Purpose:

- recurring cleanup
- scheduled generated/upload retention
- timed retries
- provider health checks
- periodic analytics summarization
- future scheduled reminders only if implemented

Create when:

- startup cleanup is not enough
- cleanup needs predictable cadence
- jobs need timed retries
- analytics/event rollups need scheduled execution
- provider health summaries need recurring checks

Capabilities supported:

- generated asset retention
- upload retention
- analytics performance feedback
- AI provider reliability

Why it should not exist yet:

- startup cleanup covers the immediate generated asset retention path
- no recurring workflow has been verified as required
- a scheduler without ownership creates operational noise

Required env vars / dependencies:

- retention windows
- generated/upload directories
- event log paths
- database path or Postgres if rollups become durable
- scheduler interval config

Risks:

- deleting the wrong files if paths are misconfigured
- running duplicate cleanup jobs
- scheduled jobs masking startup failures

Owner role:

- Backend Systems Lead

Go/no-go rule:

- Go only when timed cleanup or recurring jobs are required in production. No-go if startup cleanup and manual checks are sufficient.

### `lwa-webhooks`

Purpose:

- Whop webhook receiver
- Stripe webhook receiver if Stripe is used
- async entitlement updates
- payment/access events
- future social/campaign event ingestion

Create when:

- real Whop or Stripe webhook verification is implemented
- entitlement state must update asynchronously
- webhook retry/signature handling needs isolation
- audit trails are required for access/campaign events

Capabilities supported:

- Whop membership verification
- Whop webhooks
- quota/entitlement sync
- future campaign submission automation only after real APIs and review states exist
- future direct posting callbacks only after platform integrations exist

Why it should not exist yet:

- no claim-safe webhook automation exists today
- backend can expose foundation status without a separate service
- creating it early encourages fake Whop/social automation claims

Required env vars / dependencies:

- Whop/Stripe signing secrets
- webhook event store
- entitlement database
- replay protection
- audit logging

Risks:

- secret leakage in logs
- replay or duplicate entitlement updates
- public copy implying campaign automation before implementation

Owner role:

- Monetization / Whop Lead

Go/no-go rule:

- Go only when signed webhook verification and durable entitlement updates are implemented. No-go for placeholder endpoints.

### Postgres

Purpose:

- persistent users
- workspaces
- jobs
- clip history
- entitlements
- campaign records
- uploaded media records
- analytics

Create when:

- local JSON, SQLite, or in-memory state is insufficient
- users need cloud history
- plan access must be durable across instances
- multiple workers need shared state
- batch/campaign systems become real
- workspace/team support moves beyond future planning

Capabilities supported:

- account/workspace/team system
- cloud history
- durable entitlements
- campaign records
- analytics feedback
- worker job coordination when paired with a queue

Why it should not exist yet:

- core MVP can operate without a full account platform
- adding Postgres early creates schema and migration ownership before product need is clear
- "real apps need databases" is not a sufficient trigger

Required env vars / dependencies:

- database URL
- migration command/process
- backup policy
- data retention policy
- PII/security review

Risks:

- migrations blocking deploys
- partial account system creating broken expectations
- durable PII without policy

Owner role:

- Chief Product Architect

Go/no-go rule:

- Go when cloud history, durable entitlements, workspaces, campaigns, or worker-shared job state require relational persistence. No-go for docs-only or seed-data needs.

### Redis

Purpose:

- job queue
- worker coordination
- rate limiting
- cache
- distributed locks

Create when:

- render or ingest workers exist
- job queue needs external broker
- rate limiting must work across instances
- backend scales beyond one process
- short-lived provider status/cache must be shared

Capabilities supported:

- render worker
- ingest worker
- batch queue
- quota abuse hardening
- provider health cache
- distributed job locks

Why it should not exist yet:

- no worker split exists yet
- no external queue need is proven
- single-process/backend-local flow can remain simpler for MVP

Required env vars / dependencies:

- Redis URL
- queue names
- lock TTLs
- retry/dead-letter policy
- rate-limit policy

Risks:

- lost jobs without durable queue discipline
- stale locks blocking renders
- rate-limit behavior differing from entitlement truth

Owner role:

- Backend Systems Lead

Go/no-go rule:

- Go only with a worker split, external queue need, or multi-instance rate limiting. No-go before workers or scale pressure.

## Service Decision Matrix

| Capability | Current service | Future service needed? | Trigger | Do now? |
| --- | --- | --- | --- | --- |
| Public URL clipping | backend | no | Current backend sufficient while ingest is simple. | no |
| yt-dlp source download | backend | `lwa-worker-ingest` later | Downloads block API or require retry isolation. | no |
| Upload source ingestion | backend | `lwa-worker-ingest` later | Upload prep/source validation blocks API. | no |
| FFmpeg clip cutting | backend | `lwa-worker-render` later | CPU/memory spikes or long jobs hurt API. | no |
| Heavy caption rendering | backend now | `lwa-worker-render` later | Burn-in/profile rendering blocks API. | not yet |
| Thumbnail generation | backend/foundation | `lwa-worker-render` later | Generated thumbnail files become a real workflow. | not yet |
| Export bundle metadata | backend | no initially | Existing backend can assemble metadata. | no |
| ZIP/batch exports | backend/foundation | `lwa-worker-render` plus Redis later | Large bundles require async jobs. | not yet |
| Strategy-only fallback | backend | no | Must remain available even if workers/providers fail. | no |
| Attention Compiler scoring | backend | no | Scoring is request/result logic, not a separate service. | no |
| Score transparency UI | frontend + backend | no | Current services can display score fields. | no |
| Generated asset cleanup | backend startup cleanup | `lwa-scheduler` later | Startup cleanup is insufficient or timed cleanup is required. | not yet |
| Upload retention | backend | `lwa-scheduler` later | Upload cleanup needs predictable recurring cadence. | not yet |
| AI provider health checks | backend | `lwa-scheduler` plus Redis later | Periodic health/cache required across instances. | later |
| Whop verification | backend foundation | `lwa-webhooks` later | Real webhook sync and durable entitlement updates. | not yet |
| Whop campaign browsing | none/foundation | `lwa-webhooks` plus Postgres later | Whop API import, access mapping, and audit records exist. | no |
| Campaign submission automation | none | `lwa-webhooks`, Postgres, Redis later | Submission API, review states, queue, audit trail. | no |
| Campaign payout tracking | none | Postgres plus `lwa-webhooks` later | Verified payout data source and reconciliation model. | no |
| Cloud user history | none/local | Postgres | Users need cloud history across sessions/devices. | later |
| Account/workspace/team | none | Postgres | Durable auth, roles, shared workspace state. | later |
| Daily quotas | backend | Redis/Postgres later | Multi-instance or durable paid entitlement needs. | not yet |
| Batch queue | backend now | Redis plus workers | Concurrent job volume exceeds backend process. | later |
| Live Twitch ingestion | none | `lwa-worker-ingest`, `lwa-webhooks`, Redis, Postgres | EventSub/chat/stream-state ingest is implemented. | no |
| Direct social posting | none | `lwa-webhooks`, Redis, Postgres | Platform auth, compliance, queues, callbacks. | no |
| Monitoring/Sentry | none/unverified | no separate Railway service | Alerts and instrumentation are selected and configured. | later |
| Cloudinary/R2 media offload | none | external storage, not a Railway service | Railway volume no longer fits asset lifecycle. | later |

## Current Railway Env Notes

Backend generated asset retention stays on the backend service unless scheduled cleanup becomes necessary:

```env
LWA_GENERATED_ASSETS_DIR=/data/lwa-generated
LWA_GENERATED_ASSETS_RETENTION_HOURS=24
LWA_GENERATED_ASSETS_MAX_FILES=300
LWA_ASSET_CLEANUP_ON_STARTUP=true
```

Frontend should use only public browser-safe variables, such as a public API base URL. It must not hold OpenAI, Whop, Stripe, database, Redis, or storage secrets.

Future services must not make AI providers, FFmpeg success, Whop, social posting, or Twitch ingestion mandatory for strategy-only clipping output.
