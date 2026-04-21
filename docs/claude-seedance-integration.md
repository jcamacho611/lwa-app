# Claude And Seedance Integration

This document describes the optional Seedance adapter layer in LWA. Seedance is not the LWA product, not the core clipping engine, and not required for normal clip generation.

## Core Rule

- LWA-owned clipping, analysis, preview, and export flows continue when Seedance is disabled.
- Seedance secrets stay backend-only.
- Seedance is isolated behind `app/services/seedance_service.py`.
- Frontend surfaces must treat Seedance as an optional enhancement, never as a blocking dependency.

## What Is Live Now

- `/generate`, `/process`, `/v1/generate`, and `/v1/jobs` remain the normal clipping/runtime spine.
- `/v1/seedance/background` submits optional background/visual jobs through the adapter.
- `/v1/seedance/jobs/{job_id}` polls optional Seedance jobs through the adapter.
- Seedance job state is stored under the existing generated-assets tree:
  - `generated/seedance/jobs/*.json`
  - `generated/seedance/assets/*` when downloadable assets are localized
- Generated assets continue to use the existing `/generated/...` static mount.

## Environment Variables

Required to enable the adapter:

- `SEEDANCE_ENABLED=true`
- `SEEDANCE_API_KEY=...`
- `SEEDANCE_BASE_URL=...`

Optional:

- `SEEDANCE_MODEL=seedance-2.0`
- `SEEDANCE_TIMEOUT_SECONDS=180`
- `SEEDANCE_POLL_INTERVAL_SECONDS=3`

Do not expose these values to the frontend.

## Provider Routing Behavior

Normal LWA generation does not route through Seedance.

Current routing:

- Video clipping: internal LWA clipping/runtime flow
- Upload/analyze/export: internal LWA flow
- Image/Idea generation: generation provider flow with clean disabled behavior
- Seedance background/enhancement: explicit `/v1/seedance/*` routes only

If Seedance is disabled or misconfigured, the Seedance routes return controlled `503` responses and the rest of LWA keeps working.

## Fallback Behavior

When Seedance is unavailable:

- normal clip generation still works
- first-upload flow still works
- export bundle flow still works
- frontend should preserve the existing UI and skip optional enhancement controls
- provider health reports Seedance as disabled or misconfigured

## Adapter Contract

The adapter currently isolates the provider HTTP contract in `seedance_service.py`.

Default assumptions:

- submit: `POST {SEEDANCE_BASE_URL}/jobs`
- poll: `GET {SEEDANCE_BASE_URL}/jobs/{provider_job_id}`
- accepted job ids can be returned as `job_id`, `id`, `task_id`, or `generation_id`
- assets can be returned as `asset_url`, `output_url`, `video_url`, `url`, `download_url`, or nested asset fields

If the final Seedance vendor contract differs, update only `seedance_service.py`. Do not spread provider-specific code through routes, frontend components, or normal generation services.

## Normalized Job Shape

Seedance jobs normalize to:

- `job_id`
- `provider_job_id`
- `provider`
- `job_kind`
- `status`
- `message`
- `created_at`
- `updated_at`
- `asset`
- `error`

Asset records normalize to:

- `asset_id`
- `provider`
- `status`
- `asset_url`
- `thumbnail_url`
- `public_url`
- `local_path`
- `content_type`
- `duration_seconds`
- `aspect_ratio`
- `metadata`

## How To Enable Safely

1. Set `SEEDANCE_ENABLED=true`.
2. Set `SEEDANCE_API_KEY`.
3. Set `SEEDANCE_BASE_URL`.
4. Smoke test `/health` and confirm Seedance status is configured.
5. Smoke test `POST /v1/seedance/background`.
6. Smoke test `GET /v1/seedance/jobs/{job_id}`.
7. Only then expose optional frontend enhancement controls.

## What Remains Pending

- Confirm the exact Seedance vendor submit/poll endpoint shape.
- Confirm whether asset URLs need signed download headers.
- Confirm final provider statuses and terminal states.
- Add frontend enhancement controls only where they are non-blocking.
