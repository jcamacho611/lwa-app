# Claude And Seedance Integration

This document describes how Seedance is used inside LWA as an optional provider adapter. Seedance is not the LWA product, not the core clipping engine, and not required for normal clip generation.

## Purpose

Seedance can support:

- image enhancement flows
- idea-to-asset generation flows
- optional background generation
- optional clip enhancement

Core LWA clipping remains:

- FastAPI orchestration
- FFmpeg pipeline
- yt-dlp ingest
- clip analysis
- render queue
- export bundle flow

## Core Rule

- LWA-owned clipping, analysis, preview, and export flows continue when Seedance is disabled.
- Seedance secrets stay backend-only.
- Seedance HTTP details stay isolated behind `app/services/seedance_service.py`.
- Frontend surfaces must treat Seedance as an optional enhancement, never as a blocking dependency.
- Do not make Seedance a hard dependency of first-upload, clip generation, preview rendering, or exports.

## Environment Variables

Required to enable the adapter:

- `SEEDANCE_ENABLED=true`
- `SEEDANCE_API_KEY=...`
- `SEEDANCE_BASE_URL=...`

Optional:

- `SEEDANCE_MODEL=seedance-2.0`
- `SEEDANCE_TIMEOUT_SECONDS=180`
- `SEEDANCE_POLL_INTERVAL_SECONDS=3`
- `LWA_GENERATED_ASSETS_DIR=...`
- `LWA_GENERATED_ASSET_STORE_PATH=...`

Do not expose these values to the frontend.

## Provider Routing Behavior

Normal LWA clipping does not route through Seedance.

Current routing:

- Video clipping: internal LWA clipping/runtime flow through `/generate`, `/process`, and `/v1/generate`
- First-upload analyze/export: internal LWA flow
- Image/Idea generation: provider generation flow with clean disabled behavior
- Seedance background/enhancement: explicit `/v1/seedance/*` routes only

If Seedance is disabled or misconfigured, Seedance-specific routes return controlled `503` responses and the rest of LWA keeps working.

## Routes

### `POST /v1/seedance/background`

Submits an optional Seedance background generation job.

### `GET /v1/seedance/jobs/{job_id}`

Polls Seedance job state through the LWA adapter and updates generated asset persistence when a matching asset exists.

### `POST /v1/seedance/jobs/{job_id}/download`

Downloads a completed provider asset into LWA-managed generated storage when a downloadable asset URL exists.

## Request Normalization

LWA owns the canonical generation contract. Requests normalize around:

- `mode`
- `prompt`
- `text_prompt`
- `image_url`
- `reference_image_url`
- `source_clip_url`
- `source_asset_id`
- `style_preset`
- `motion_profile`
- `duration_seconds`
- `aspect_ratio`
- `provider`

Video mode belongs to the clipping flow. Image and Idea mode belong to the provider generation flow.

## Generated Asset Normalization

Generated assets normalize around:

- `id`
- `provider`
- `asset_type`
- `status`
- `prompt`
- `preview_url`
- `video_url`
- `thumbnail_url`
- `source_refs`
- `local_path`
- `provider_job_id`
- `request_id`
- `created_at`
- `updated_at`
- `error`

Generated asset records are persisted in the generated asset store configured by `LWA_GENERATED_ASSET_STORE_PATH`.

## Adapter Contract

The adapter currently isolates the provider HTTP contract in `seedance_service.py`.

Default assumptions:

- submit: `POST {SEEDANCE_BASE_URL}/jobs`
- poll: `GET {SEEDANCE_BASE_URL}/jobs/{provider_job_id}`
- accepted job ids can be returned as `job_id`, `id`, `task_id`, or `generation_id`
- assets can be returned as `asset_url`, `output_url`, `video_url`, `url`, `download_url`, or nested asset fields

If the final Seedance vendor contract differs, update only `seedance_service.py`. Do not spread provider-specific code through routes, frontend components, or normal clipping services.

## Safe Fallback Behavior

When Seedance is unavailable:

- startup remains healthy
- `/health` remains healthy
- normal clip generation still works
- first-upload flow still works
- export bundle flow still works
- multimodal provider generation returns a clear provider-disabled response
- optional frontend enhancement controls should be hidden or disabled

## What Is Live Now

Live or intended:

- clipping pipeline
- first-upload no-signup path
- export bundle flow
- provider-disabled safe handling
- generated asset persistence
- image / idea generation routing
- explicit Seedance background and job polling routes

Adapter-only or pending exact contract confirmation:

- provider-specific model tuning
- advanced background enhancement presets
- provider-specific high-fidelity asset variants
- final Seedance vendor status map and terminal state names
- final signed asset download requirements

## How To Enable Safely

1. Set `SEEDANCE_ENABLED=true`.
2. Set `SEEDANCE_API_KEY`.
3. Set `SEEDANCE_BASE_URL`.
4. Smoke test `/health` and confirm Seedance status is configured.
5. Smoke test `POST /v1/seedance/background`.
6. Smoke test `GET /v1/seedance/jobs/{job_id}`.
7. Smoke test `POST /v1/seedance/jobs/{job_id}/download` after a completed asset exists.
8. Only then expose optional frontend enhancement controls.

## Future Work Rules

- no duplicate generation schemas
- no duplicate provider systems
- no provider secrets in frontend
- no making Seedance a hard dependency of clipping
- no broad rewrites just to support one provider
- keep first-upload no-signup clipping and export available even when Seedance is off
