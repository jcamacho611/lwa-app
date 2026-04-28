# Backend Launch Readiness

## Purpose

This is the backend go/no-go checklist for the current LWA / IWA MVP.

It is intentionally narrower than the broader product launch checklist. It focuses on the live API, Railway runtime, quota safety, generated-asset retention, and operator verification.

## Live Endpoints To Check

After deploy, open:

- `/`
- `/health`
- `/docs`
- `/generate`
- `/v1/jobs`
- `/v1/trends` if enabled in the current deploy

## Required Railway Setup

Repository settings:

- repo: `jcamacho611/lwa-app`
- root directory: `lwa-backend`
- Railway volume mounted at `/data`

Current repo truth:

- backend deploy uses [nixpacks.toml](/Users/bdm/LWA/lwa-app/lwa-backend/nixpacks.toml)
- there is no backend `railway.toml` in the current repo
- there is no root `render.yaml` in the current repo

## Required Env Vars

```env
ENVIRONMENT=production
LWA_APP_NAME=LWA Backend
OPENAI_API_KEY=YOUR_REAL_OPENAI_KEY
ALLOWED_ORIGINS=*
FFMPEG_PATH=/usr/bin/ffmpeg
YT_DLP_TEMP_DIR=/tmp
LWA_GENERATED_ASSETS_DIR=/data/lwa-generated
LWA_GENERATED_ASSETS_RETENTION_HOURS=24
LWA_GENERATED_ASSETS_MAX_FILES=300
LWA_ASSET_CLEANUP_ON_STARTUP=true
LWA_USAGE_STORE_PATH=/data/lwa-usage.json
```

Recommended quota / access vars:

```env
LWA_CLIENT_ID_HEADER_NAME=x-lwa-client-id
LWA_FREE_DAILY_LIMIT=2
LWA_PRO_DAILY_LIMIT=25
LWA_SCALE_DAILY_LIMIT=100
LWA_DEFAULT_PLAN_NAME=Starter Trial
LWA_DEFAULT_TURNAROUND=45 seconds
```

Optional:

```env
API_BASE_URL=https://lwa-backend-production-c9cc.up.railway.app
OPENAI_MODEL=gpt-4.1-mini
LWA_API_KEY_SECRET=YOUR_OPTIONAL_SHARED_SECRET
LWA_ENABLE_WHOP_VERIFICATION=false
WHOP_API_KEY=
WHOP_COMPANY_ID=
WHOP_PRODUCT_ID=
WHOP_WEBHOOK_SECRET=
```

## Go / No-Go Checklist

Go only if all are true:

- `/health` returns `status=ok`
- `ffmpeg` is available
- `yt_dlp` is available
- generated asset directories mount correctly
- startup cleanup does not crash app boot
- quota-exceeded responses remain structured
- `/generate` returns a usable clip pack or useful fallback output
- `/v1/jobs` can queue and report status

## Common Failure States

### 1. Generated Asset Volume Keeps Growing

Check:

- `LWA_GENERATED_ASSETS_DIR`
- `LWA_GENERATED_ASSETS_RETENTION_HOURS`
- `LWA_GENERATED_ASSETS_MAX_FILES`
- `LWA_ASSET_CLEANUP_ON_STARTUP`

Expected startup log:

- `generated_asset_startup_cleanup ...`

### 2. OpenAI Missing

Expected behavior:

- health shows missing key
- backend still returns fallback packaging output
- no hard crash should occur just because OpenAI is unavailable

### 3. Quota Complaints Or Free-Tier Abuse

Check:

- `LWA_USAGE_STORE_PATH`
- `LWA_FREE_DAILY_LIMIT`
- `LWA_PRO_API_KEYS`
- `LWA_SCALE_API_KEYS`

### 4. Whop Verification Confusion

Current truth:

- Whop verification is not live by default
- if enabled without config, health should show `missing-config`
- production must still fall back safely to free/API-key plan resolution

## Operator Verification Commands

```bash
cd /Users/bdm/LWA/lwa-app
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend
python3 -m unittest discover -s tests
cd ..
git diff --check
```

## Launch Rule

Do not block launch on:

- full Whop verification
- team/workspace support
- campaign browsing automation
- direct social posting

Do block launch on:

- broken `/health`
- broken `/generate`
- broken `/v1/jobs`
- generated-asset retention not understood
- quota abuse wide open
- backend failing compile or tests locally
