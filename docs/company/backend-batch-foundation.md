# Backend Batch Foundation

## Purpose
Prepare the backend response contract for future batch workflows without breaking the current single-source generation flow.

## Implemented
- optional batch-ready fields in `ProcessingSummary`
- optional source/batch metadata on each `ClipResult`
- request-side `clip_count` support with plan-aware clamping
- `generation_mode` and `workflow_stage` metadata
- `batch_mode=false` by default for current single-source runs

## Current Truth
- the shipping product still generates from one source at a time
- `/v1/batches` exists as foundation work, but multi-source generation is not yet the default product path
- clients can safely ignore all new batch metadata fields

## Env Vars
- `LWA_FREE_CLIP_LIMIT`
- `LWA_PRO_CLIP_LIMIT`
- `LWA_SCALE_CLIP_LIMIT`
- `LWA_MAX_CLIP_LIMIT`

## Safe Claims
- batch-ready foundation exists
- clip count is plan-aware
- response metadata is ready for future batch UI

## Unsafe Claims
- true multi-source batch generation is fully shipped
- agency-scale automation is complete

## Future Work
- connect `/v1/batches` to multi-source generation orchestration
- durable batch progress analytics
- operator views for batch-level retry and export
