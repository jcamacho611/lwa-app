# Backend High-Volume Clipping

## Current truth

The backend now accepts optional `clip_count` requests and clamps them against:

- plan clip limits
- `LWA_MAX_CLIPS_PER_JOB`
- `LWA_MAX_CLIP_LIMIT`
- `LWA_HIGH_VOLUME_MAX_CLIPS` when high-volume mode is explicitly enabled

Current safe defaults:

- free: 3
- pro: 6
- scale: 12
- high-volume mode: disabled by default

## Enabled by default

- single-source generation
- plan-aware clip-count clamping
- requested / allowed / returned clip metadata in `processing_summary`
- event logging for high-volume requests and clamp events when event logging is enabled

## Disabled by default

- 20+ clip workflows
- true multi-source batch generation
- unlimited clip requests

## Env vars

```env
LWA_FREE_CLIP_LIMIT=3
LWA_PRO_CLIP_LIMIT=6
LWA_SCALE_CLIP_LIMIT=12
LWA_MAX_CLIP_LIMIT=12
LWA_MAX_CLIPS_PER_JOB=12
LWA_ENABLE_HIGH_VOLUME_CLIPS=false
LWA_HIGH_VOLUME_MAX_CLIPS=24
```

## Claim-safe language

Say:

- LWA supports plan-aware clip counts and can scale upward when explicitly configured.
- High-volume workflows are gated and operator-controlled.

Do not say:

- LWA returns 20 to 40 publishable clips by default.
- LWA supports unlimited clip generation.

## Future work

- true multi-source batch orchestration
- stronger duplicate suppression for very large clip packs
- scheduled heavy render workers for large jobs
