# Backend Video Output Contract

## Purpose
Describe the backend clip payload fields that distinguish playable media from strategy-only output.

## Clip Asset Fields
- `clip_url`
- `raw_clip_url`
- `edited_clip_url`
- `preview_url`
- `preview_image_url`
- `download_url`
- `thumbnail_url`

## Render Status Fields
- `render_status`
  - legacy internal state used by the current backend path
  - values may include `ready`, `pending`, or `failed`
- `rendered_status`
  - creator-facing compatibility alias
  - values:
    - `rendered`
    - `raw_only`
    - `strategy_only`
    - `render_failed`

## Related Clip Flags
- `is_rendered`
- `is_strategy_only`
- `fallback_reason`
- `render_error`
- `render_readiness_score`

## Processing Summary Fields
- `assets_created`
- `raw_assets_created`
- `edited_assets_created`
- `rendered_clip_count`
- `strategy_only_clip_count`
- `recommended_next_step`

## Behavioral Rules
- clips with playable or previewable media must not masquerade as strategy-only
- clips without usable media must be labeled strategy-only
- one failed render must not kill the whole batch if the rest of the pack is usable
- asset URLs must stay under the backend generated-assets contract

## Current Limits
- no full caption burn-in editor
- no Remotion pipeline
- no Cloudinary offload in the current shipping path

## Related Files
- `lwa-backend/app/services/clip_service.py`
- `lwa-backend/app/services/response_normalizer.py`
- `lwa-backend/app/processor.py`
- `lwa-backend/tests/test_output_contract.py`
