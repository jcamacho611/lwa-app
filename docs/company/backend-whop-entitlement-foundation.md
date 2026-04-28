# Backend Whop Entitlement Foundation

## Purpose
Document the current backend entitlement truth and the disabled-by-default Whop verification foundation.

## Implemented Today
- free / pro / scale plan resolution
- API-key based pro and scale upgrades
- usage reservation and release
- structured quota-exceeded responses
- `plan_code`, `plan_name`, `credits_remaining`, and `feature_flags` in backend responses
- disabled-by-default Whop verification state reporting

## Not Implemented Yet
- live Whop membership verification
- webhook-driven entitlement sync
- billing-grade workspace or organization entitlements

## Required Env Vars
- `LWA_CLIENT_ID_HEADER_NAME`
- `LWA_FREE_DAILY_LIMIT`
- `LWA_PRO_DAILY_LIMIT`
- `LWA_SCALE_DAILY_LIMIT`
- `LWA_PRO_API_KEYS`
- `LWA_SCALE_API_KEYS`
- `LWA_USAGE_STORE_PATH`

## Whop Foundation Env Vars
- `WHOP_API_KEY`
- `WHOP_COMPANY_ID`
- `WHOP_PRODUCT_ID`
- `WHOP_WEBHOOK_SECRET`
- `LWA_ENABLE_WHOP_VERIFICATION=false`

## Feature Flag Truth
Free:
- clip access is limited
- premium exports false
- campaign mode false
- posting queue false

Pro:
- richer packaging fields are enabled
- premium exports true
- campaign mode false
- posting queue false
- priority processing false until a real priority queue exists

Scale:
- higher limits than Pro
- richer packaging fields are enabled
- premium exports true
- campaign mode false until a real campaign workflow is shipped
- posting queue false until a real posting queue is shipped
- priority processing false until a real priority queue exists

## Safety Rules
- do not trust client-only premium claims
- do not log Whop secrets
- do not require Whop to be configured for generation to work

## Related Files
- `lwa-backend/app/services/entitlements.py`
- `lwa-backend/app/services/whop_service.py`
- `lwa-backend/tests/test_entitlements.py`
- `lwa-backend/tests/test_whop_service.py`
