# Backend Event Log

## Purpose
Provide lightweight backend-local operator analytics without adding a heavy analytics platform.

## Implemented
- JSONL event logging through `lwa-backend/app/services/event_log.py`
- metadata redaction for secret-like keys
- URL hashing instead of raw URL storage by default
- nonfatal logging failures
- size trimming when the log exceeds the configured max bytes

## Env Vars
- `LWA_EVENT_LOG_ENABLED`
- `LWA_EVENT_LOG_PATH`
- `LWA_EVENT_LOG_MAX_BYTES`
- `LWA_EVENT_LOG_MAX_METADATA_CHARS`

## Events In Use
- `generation_requested`
- `generation_completed`
- `generation_failed`
- `quota_reserved`
- `quota_released`
- `quota_exceeded`
- `rendered_asset_created`
- `strategy_package_created`
- `campaign_pack_requested`

## Privacy Safety
- do not log API keys
- do not log Whop secrets
- do not log full source URLs by default
- keep metadata small and sanitized

## Current Truth
- this is an operator log foundation
- it is not a full user analytics dashboard
- it is not yet a feedback API or performance insights product

## Future Work
- structured feedback endpoint
- internal summaries
- performance/posted-result joins
