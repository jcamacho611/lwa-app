# LWA

Local MVP for an AI content repurposer aimed at short-form video creators.

LWA takes a video URL, sends it to a backend, and returns clip ideas with hooks and captions. This version is stronger than a bare scaffold: it includes a monetization-oriented iOS UI, saved run history, a configurable backend base URL, a configurable checkout link, and a Render-ready FastAPI deployment setup with Docker, FFmpeg, `yt-dlp`, and health checks.

## Project Structure

```text
LWA/
├── README.md
├── .gitignore
├── docs/
├── render.yaml
├── lwa-backend/
│   ├── .env.example
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── generate.py
│   │   ├── config.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── generation.py
│   │   ├── job_store.py
│   │   ├── main.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── mock_data.py
│   │   ├── processor.py
│   │   ├── schemas.py
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── caption_service.py
│   │   │   ├── clip_service.py
│   │   │   └── video_service.py
│   │   └── trends.py
│   │   └── utils/
│   │       ├── downloader.py
│   │       └── ffmpeg_utils.py
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── railway.toml
│   └── requirements.txt
└── lwa-ios/
    ├── LWA.xcodeproj/
    └── LWA/
        ├── Assets.xcassets/
        ├── ContentView.swift
        ├── Info.plist
        ├── LWAApp.swift
        ├── Models/
        │   └── ClipResult.swift
        ├── Services/
        │   └── APIClient.swift
        └── ViewModels/
            └── ContentViewModel.swift
```

## Backend Layout

- `lwa-backend/app/main.py`: FastAPI app factory that mounts static generated assets and attaches the API router.
- `lwa-backend/app/api/routes/generate.py`: HTTP surface for `/generate`, `/process`, `/v1/generate`, async jobs, trends, and health.
- `lwa-backend/app/core/config.py`: Canonical environment-based settings with Railway detection and Homebrew/local FFmpeg auto-detection.
- `lwa-backend/app/models/schemas.py`: Canonical request and response models.
- `lwa-backend/app/services/clip_service.py`: Orchestration layer that builds clip responses, runs jobs, and exposes dependency health.
- `lwa-backend/app/services/video_service.py`: Source processing and social-export wrappers around the lower-level pipeline.
- `lwa-backend/app/services/ai_service.py`: Hook/caption generation wrapper for OpenAI, Ollama, or heuristic fallback.
- `lwa-backend/app/services/caption_service.py`: Fallback copy generation helpers.
- `lwa-backend/app/utils/downloader.py`: Download wrapper for video ingestion.
- `lwa-backend/app/utils/ffmpeg_utils.py`: FFmpeg-facing helpers for clip cutting and social export.

## What Each Part Does

- `lwa-backend/app/config.py`: Backward-compatible import shim for the canonical settings module.
- `lwa-backend/app/generation.py`: Hook, caption, and angle generation with OpenAI, Ollama, or heuristic fallback.
- `lwa-backend/app/job_store.py`: In-memory async job tracking for long-running clip generation.
- `lwa-backend/app/schemas.py`: Backward-compatible import shim for the canonical schema module.
- `lwa-backend/app/mock_data.py`: Fallback clip copy when real generation is unavailable.
- `lwa-backend/app/processor.py`: Real `yt-dlp` plus `ffmpeg` pipeline that downloads a source video, reads captions when available, and cuts MP4 clips.
- `lwa-backend/app/trends.py`: Public trend aggregation from Google Trends, Reddit, and Hacker News.
- `lwa-backend/.env.example`: Copyable backend environment template for local, Railway, or Render deploys.
- `lwa-backend/scripts/smoke_test.py`: End-to-end backend smoke test for local or deployed environments.
- `lwa-backend/requirements.txt`: Python dependencies, including `yt-dlp` and deployment-ready HTTP and AI packages.
- `lwa-backend/Dockerfile`: Render-friendly container image with `ffmpeg`, `curl`, and a Docker health check.
- `lwa-backend/railway.toml`: Railway config-as-code file for Docker deploys from the backend subdirectory.
- `render.yaml`: One-file Render blueprint for deploying the backend with a persistent disk and prompted secrets.
- `docs/final-launch-checklist.md`: Final manual checklist for Railway, Whop, and iOS launch work.
- `lwa-ios/LWA/LWAApp.swift`: SwiftUI app entry point.
- `lwa-ios/LWA/ContentView.swift`: Main dark UI, pricing sheet, settings sheet, results, and saved history.
- `lwa-ios/LWA/Models/ClipResult.swift`: Codable API and local persistence models.
- `lwa-ios/LWA/Services/APIClient.swift`: Local network call plus runtime configuration for API base URL and checkout URL.
- `lwa-ios/LWA/ViewModels/ContentViewModel.swift`: State management, local history persistence, and export/share text generation.
- `lwa-ios/LWA/Info.plist`: App config, including debug and production API defaults plus checkout URL.
- `lwa-ios/LWA.xcodeproj`: Xcode project you can open and run in the iOS Simulator.

## MVP Features Included

- Video URL input and end-to-end backend call.
- Async backend jobs with polling for longer video processing.
- Real source download via `yt-dlp`.
- Real MP4 clip cutting via `ffmpeg`.
- Transcript-aware clip window selection when subtitles or auto-captions are available.
- Live trend radar from Google Trends, Reddit, and Hacker News.
- Hooks, captions, clip score, and clip format generation with heuristic or AI provider fallback.
- Processing summary with plan name and remaining credits.
- Saved run history stored locally on-device.
- Copy and share actions for the latest clip pack.
- Configurable API base URL for local or hosted backend use.
- Configurable checkout URL so you can attach a real payment link.
- Pricing/paywall screen to give beta users an upgrade path.

## Backend: Local Run

From the repository root:

```bash
cd lwa-backend
source .venv/bin/activate
pip install -r requirements.txt
./scripts/dev_local.sh
```

This Mac-first launcher keeps local port `8000` predictable, excludes `.venv` and generated assets from reload watching, and uses the current backend package directly.

If you want a local env template first:

```bash
cd lwa-backend
cp .env.example .env
```

The backend will start at:

```text
http://127.0.0.1:8000
```

Useful endpoints:

- `GET /`
- `GET /health`
- `GET /v1/status/health`
- `GET /v1/trends`
- `POST /generate`
- `POST /v1/jobs`
- `GET /v1/jobs/{job_id}`
- `POST /process`
- `POST /v1/generate`

Useful environment variables:

```bash
export ENVIRONMENT="production"
export LWA_APP_NAME="LWA Backend"
export LWA_DEFAULT_PLAN_NAME="Starter Trial"
export LWA_DEFAULT_CREDITS_REMAINING="2"
export LWA_DEFAULT_TURNAROUND="45 seconds"
export OPENAI_API_KEY="your_key_here"
export FFMPEG_PATH="/opt/homebrew/bin/ffmpeg"
export LWA_VIDEO_ENCODER="auto"
export YT_DLP_TEMP_DIR="/tmp"
export LWA_GENERATED_ASSETS_DIR="/absolute/path/to/generated"
export API_BASE_URL="https://your-render-service.onrender.com"
export ALLOWED_ORIGINS="*"
export LOG_LEVEL="info"
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/process \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://www.youtube.com/watch?v=example"}'
```

Synchronous `/generate` example:

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://www.youtube.com/watch?v=example","target_platform":"TikTok"}'
```

Lightweight local verification:

```bash
cd /Users/bdm/LWA/lwa-backend
source .venv/bin/activate
python scripts/smoke_test.py http://127.0.0.1:8000
```

On Apple Silicon Macs, `LWA_VIDEO_ENCODER=auto` will prefer `h264_videotoolbox` when the local FFmpeg build supports it and fall back to `libx264` everywhere else.

Async job example:

```bash
curl -X POST http://127.0.0.1:8000/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://www.youtube.com/watch?v=example","target_platform":"TikTok"}'
```

## Backend: Docker Run

From the repository root:

```bash
cd lwa-backend
docker build -t lwa-backend .
docker run --rm -p 8000:8000 lwa-backend
```

To test with production-like env vars:

```bash
cd lwa-backend
docker build -t lwa-backend .
docker run --rm -p 8000:8000 \
  -e ENVIRONMENT=local \
  -e OPENAI_API_KEY=test_key \
  -e API_BASE_URL=http://127.0.0.1:8000 \
  lwa-backend
```

## Render Deployment

This repo now includes a ready-to-use [`render.yaml`](/Users/bdm/LWA/render.yaml) blueprint.

Fastest path:

1. In Render, create a new Blueprint service from this repository
2. Let Render read `render.yaml`
3. Fill in the `sync: false` secrets when prompted
4. Deploy

Manual fallback:

1. Create a new `Web Service`
2. Connect this GitHub repository
3. Set `Root Directory` to `lwa-backend`
4. Set `Language` to `Docker`
5. Leave the Docker command empty so Render uses the Dockerfile `CMD`
6. Set `Health Check Path` to `/health`
7. Attach a disk so generated clip assets persist between deploys

## Railway Deployment

This repo is also compatible with Railway using the existing backend Dockerfile plus a Railway config file at [`lwa-backend/railway.toml`](/Users/bdm/LWA/lwa-backend/railway.toml).

For this monorepo, Railway’s official monorepo docs say you should:

1. Create a new Railway service from this GitHub repo
2. Set the service `Root Directory` to `lwa-backend`
3. Set the config-as-code file path to `/lwa-backend/railway.toml`
4. Let Railway build from the `Dockerfile` in that directory
5. Attach a volume so generated clip assets persist

Recommended Railway volume mount path:

```text
/data
```

The backend now auto-detects these Railway-provided values when available:

- `RAILWAY_PUBLIC_DOMAIN` to derive the public API base URL if `API_BASE_URL` is unset
- `RAILWAY_VOLUME_MOUNT_PATH` to store generated clip assets if `LWA_GENERATED_ASSETS_DIR` is unset
- `RAILWAY_GIT_COMMIT_SHA` for the service version if no Render commit SHA exists

Suggested Railway variables:

```text
ENVIRONMENT=production
LWA_APP_NAME=LWA Backend
LWA_DEFAULT_PLAN_NAME=Starter Trial
LWA_DEFAULT_CREDITS_REMAINING=2
LWA_DEFAULT_TURNAROUND=45 seconds
FFMPEG_PATH=/usr/bin/ffmpeg
YT_DLP_TEMP_DIR=/tmp
ALLOWED_ORIGINS=*
LOG_LEVEL=info
OPENAI_API_KEY=your_real_key
OPENAI_MODEL=gpt-4.1-mini
LWA_API_KEY_HEADER_NAME=x-api-key
LWA_API_KEY_SECRET=your_optional_secret
```

Optional but useful:

```text
API_BASE_URL=https://your-custom-domain.com
LWA_GENERATED_ASSETS_DIR=/data/lwa-generated
```

If you do not set `API_BASE_URL`, the app will use `https://${RAILWAY_PUBLIC_DOMAIN}` automatically on Railway.

Local CLI deploy path:

```bash
brew install railway
cd /Users/bdm/LWA/lwa-backend
railway login
railway link
railway up
```

## Final Launch Checklist

Use this file for the last manual platform steps:

- [docs/final-launch-checklist.md](/Users/bdm/LWA/docs/final-launch-checklist.md)
- [docs/whop-railway-connection.md](/Users/bdm/LWA/docs/whop-railway-connection.md)

Required env vars in Render:

```text
ENVIRONMENT=production
OPENAI_API_KEY=your_real_key
API_BASE_URL=https://your-service.onrender.com
ALLOWED_ORIGINS=*
FFMPEG_PATH=/usr/bin/ffmpeg
YT_DLP_TEMP_DIR=/tmp
LWA_GENERATED_ASSETS_DIR=/tmp/lwa-generated
LOG_LEVEL=info
```

Recommended checks after the first deploy:

```text
https://your-service.onrender.com/health
https://your-service.onrender.com/docs
```

The health response now reports:

- service name
- environment
- version
- whether a working `ffmpeg` binary exists
- whether `yt-dlp` exists
- whether `OPENAI_API_KEY` is present
- whether Whop, Google, TikTok, and Meta credentials are present

## iOS App Run

1. Open the project:

```bash
open lwa-ios/LWA.xcodeproj
```

2. In Xcode, choose the `LWA` scheme.
3. Run the app in an iPhone Simulator.
4. Paste a public video URL and tap `Generate Clips`.
5. Open `Pricing` or `Settings` inside the app to change the checkout link or backend base URL.

Default local API target:

```text
http://127.0.0.1:8000
```

Default production API target:

```text
https://lwa-backend.onrender.com
```

Important note:

- `127.0.0.1` is correct for the local backend flow when using the iOS Simulator on your Mac.
- If you later run the app on a physical iPhone, change the API base URL inside the app settings to your Mac's LAN IP or your deployed backend URL.
- The Release iOS build now points at the live Railway backend by default.
- The iOS app’s web storefront URL now points at the live Whop product by default.
- App Store launch notes live in `docs/app-store-device-launch.md`.

## What Still Blocks Real Revenue

This repo is now a usable MVP, but it is not a finished SaaS business yet. Before charging real customers, add:

- Authentication and user accounts.
- Real App Store billing with StoreKit, or a strictly web-only monetization flow that avoids in-app purchase prompts.
- Persistent job storage instead of in-memory job tracking.
- Analytics, error monitoring, and support flows.
- Social publishing and export delivery beyond direct clip asset URLs.
- Whop entitlement or access gating in the app instead of an external checkout link alone.

## Exact Commands To Run Next

Start the backend first:

```bash
cd /Users/bdm/LWA/lwa-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second Terminal window, open the iOS project:

```bash
cd /Users/bdm/LWA
open lwa-ios/LWA.xcodeproj
```

Then in Xcode:

1. Pick an iPhone Simulator.
2. Press Run.
3. Paste a video URL.
4. Tap `Generate Clips`.
5. Open `Settings` and switch the API URL only if you want to test against a different backend.

## Render Commands You’ll Actually Use

Local smoke test:

```bash
cd /Users/bdm/LWA/lwa-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Container smoke test:

```bash
cd /Users/bdm/LWA/lwa-backend
docker build -t lwa-backend .
docker run --rm -p 8000:8000 -e OPENAI_API_KEY=test_key lwa-backend
```
