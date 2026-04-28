# Railway Generated Assets Retention

## Objective
Keep Railway volume usage under control without touching uploads, source code, configs, logs, or non-generated platform data.

## Connected Files
- `lwa-backend/app/services/asset_retention.py`
- `lwa-backend/app/services/clip_service.py`
- `lwa-backend/app/core/config.py`
- `lwa-backend/app/main.py`
- `lwa-backend/tests/test_asset_retention.py`

## Generated Asset Directory
`Settings.generated_assets_dir` resolves in this order:

1. `LWA_GENERATED_ASSETS_DIR`
2. `RAILWAY_VOLUME_MOUNT_PATH/lwa-generated`
3. local fallback: `<repo>/generated`

Uploads remain separate through `LWA_UPLOADS_DIR` or `RAILWAY_VOLUME_MOUNT_PATH/lwa-uploads`.

## What Cleanup Does
- scans only inside the configured generated assets directory
- deletes generated files older than the retention window
- trims the oldest remaining generated files when total generated file count exceeds the max
- removes empty generated subdirectories after file cleanup
- runs nonfatally on startup when enabled
- prunes stale `generated_assets` store records that reference removed files
- emits cleanup summary fields including scanned count, deleted count, retained count, bytes deleted, and store rows removed

## What Cleanup Must Not Delete
- anything outside `LWA_GENERATED_ASSETS_DIR`
- uploads under `LWA_UPLOADS_DIR`
- source code, docs, configs, tests, or logs outside the generated assets directory
- protected files inside the generated directory such as:
  - `LWA_GENERATED_ASSET_STORE_PATH`
  - `LWA_USAGE_STORE_PATH`
  - `LWA_PLATFORM_DB_PATH`
  - `LWA_CLIPPING_DB_PATH`
  - `LWA_EVENT_LOG_PATH`

## Required Railway Variables
- `LWA_GENERATED_ASSETS_DIR`
- `LWA_GENERATED_ASSETS_RETENTION_HOURS`
- `LWA_GENERATED_ASSETS_MAX_FILES`
- `LWA_ASSET_CLEANUP_ON_STARTUP`

## Recommended Railway Values
```env
LWA_GENERATED_ASSETS_DIR=/data/lwa-generated
LWA_GENERATED_ASSETS_RETENTION_HOURS=24
LWA_GENERATED_ASSETS_MAX_FILES=300
LWA_ASSET_CLEANUP_ON_STARTUP=true
```

## Aggressive Temporary Values
Use these if Railway volume pressure stays high while monitoring usage:

```env
LWA_GENERATED_ASSETS_DIR=/data/lwa-generated
LWA_GENERATED_ASSETS_RETENTION_HOURS=6
LWA_GENERATED_ASSETS_MAX_FILES=150
LWA_ASSET_CLEANUP_ON_STARTUP=true
```

## Safety Notes
- Cleanup resolves the base directory before deletion.
- Each candidate file is resolved and must stay inside the resolved base directory.
- Symlinked files that resolve outside the base directory are skipped.
- Directories are only removed when empty.
- Cleanup failure must not block app startup.

## Verification
```bash
cd /Users/bdm/LWA/lwa-app
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend
python3 -m unittest discover -s tests
cd ..
git diff --check
```
