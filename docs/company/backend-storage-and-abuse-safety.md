# Backend Storage And Abuse Safety

## Storage safety

Generated asset cleanup remains path-contained and nonfatal.

The backend deletes only old generated output files inside the configured generated assets directory.

It does not delete:

- source code
- docs
- tests
- configs
- uploads outside the generated-assets directory
- arbitrary Railway volume files

## Required Railway env vars

```env
LWA_GENERATED_ASSETS_DIR=/data/lwa-generated
LWA_GENERATED_ASSETS_RETENTION_HOURS=24
LWA_GENERATED_ASSETS_MAX_FILES=300
LWA_ASSET_CLEANUP_ON_STARTUP=true
```

Aggressive temporary values:

```env
LWA_GENERATED_ASSETS_RETENTION_HOURS=6
LWA_GENERATED_ASSETS_MAX_FILES=150
LWA_ASSET_CLEANUP_ON_STARTUP=true
```

## Abuse controls now present

- server-side daily quota reservation and release
- plan-aware clip-count clamping
- request throttle per subject
- safe event-log redaction and URL hashing

## Optional env vars for clipping safety

```env
LWA_EVENT_LOG_ENABLED=true
LWA_EVENT_LOG_PATH=/data/lwa-events.jsonl
LWA_EVENT_LOG_MAX_BYTES=10485760
LWA_MAX_CLIPS_PER_JOB=12
LWA_ENABLE_HIGH_VOLUME_CLIPS=false
LWA_HIGH_VOLUME_MAX_CLIPS=24
```

## What still remains

- production verification of Railway volume stabilization
- stronger source-duration policy if long-running abuse becomes real
- distributed rate limiting if the service becomes multi-instance
