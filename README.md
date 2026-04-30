# LWA / IWA

LWA is an upload-first AI clipping engine for creator source material. It accepts supported uploads, prompt-only requests, and best-effort public URLs, then returns ranked short-form clip packages with hooks, captions, timestamps, score transparency, and rendered media when rendering is available.

The product keeps rendered output and strategy-only fallback separate. If a public platform blocks server access, an AI provider is unavailable, or rendering fails, LWA should still return a usable degraded package instead of exposing raw backend, yt-dlp, cookie, or bot-check errors.

## Live URLs

| Service | URL |
| --- | --- |
| Frontend | `https://lwa-the-god-app-production.up.railway.app` |
| Backend | `https://lwa-backend-production-c9cc.up.railway.app` |

## What It Does

- Upload-first source ingest for video, audio, and image files where supported by the backend.
- Prompt-only generation for strategy packages when no media source is provided.
- Best-effort public URL ingest with clean fallback messaging when external platforms block access.
- Retention-oriented clip ranking with non-flat fallback score distribution.
- Rendered clip fields only when playable media exists.
- Strategy-only clips with hooks, captions, packaging angle, posting order, and recovery guidance.
- Free launch mode for public testing without forcing sign-in.

## Architecture

```text
Browser / Next.js
  |
  |  upload, prompt, or public URL
  v
FastAPI backend
  |
  +-- source_ingest: uploads, prompt context, public URL best effort
  +-- generation: ranked clip package and fallback scoring
  +-- render/export: ffmpeg output when possible
  +-- job_store: /v1/jobs async status
  +-- generated assets volume: cleanup and retention guard
  |
  v
Response
  |
  +-- rendered clips: playable preview/download URLs
  +-- strategy-only clips: no media URL, explicit fallback reason
```

## Repository Layout

```text
lwa-app/
├── README.md
├── docs/
├── lwa-backend/
│   ├── app/
│   ├── requirements.txt
│   └── tests/
├── lwa-web/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── lwa-ios/
└── tools/
```

`lwa-ios/` is not part of Railway deploys and is not touched for backend/web hardening unless explicitly assigned.

## Local Dev

This repo does not currently ship a root `docker-compose.yml`. Run the backend and web app in separate terminals.

Backend:

```bash
cd /Users/bdm/LWA/lwa-app/lwa-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend:

```bash
cd /Users/bdm/LWA/lwa-app/lwa-web
npm install
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

## Required Env Vars

| Var | Service | Purpose |
| --- | --- | --- |
| `FREE_LAUNCH_MODE` | backend | Enables public launch mode without forcing auth on protected backend dependencies. |
| `RATE_LIMIT_GUEST_RPM` | backend | Requests per IP per minute for free-launch anonymous generate traffic. Default: `30`. |
| `NEXT_PUBLIC_FREE_LAUNCH_MODE` | web | Shows the free-launch banner and hides sign-in CTAs from the first-use flow. |
| `NEXT_PUBLIC_API_BASE_URL` | web | Backend base URL used by the browser app. |
| `LWA_GENERATED_ASSETS_DIR` | backend | Directory or Railway volume path for generated clips/assets. |
| `LWA_GENERATED_ASSETS_RETENTION_HOURS` | backend | Max age before generated asset cleanup removes old files. |
| `LWA_GENERATED_ASSETS_MAX_FILES` | backend | Max generated file count before oldest files are trimmed. |
| `LWA_ASSET_CLEANUP_ON_STARTUP` | backend | Runs nonfatal generated asset cleanup during startup when true. |
| `LWA_UPLOADS_DIR` | backend | Upload storage directory. |
| `LWA_USAGE_STORE_PATH` | backend | Local JSON quota store path for free/API-key usage. |
| `OPENAI_API_KEY` | backend | Optional AI provider key. Product must still degrade if unavailable. |
| `ANTHROPIC_API_KEY` | backend | Optional AI provider key. Product must still degrade if unavailable. |
| `FFMPEG_PATH` | backend | Optional ffmpeg binary path override. |
| `MAX_UPLOAD_MB` | backend | Upload size cap. Default: `500`. |

## API Surface

Health:

```bash
curl https://lwa-backend-production-c9cc.up.railway.app/health
```

Generate from a prompt:

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -H 'x-lwa-client-id: local-readme' \
  -d '{
    "prompt": "Create three short-form clip ideas for an upload-first creator tool.",
    "source_type": "prompt",
    "target_platform": "TikTok",
    "clip_count": 3
  }'
```

Generate from a public URL, best effort:

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -H 'x-lwa-client-id: local-readme' \
  -d '{
    "video_url": "https://example.com/source.mp4",
    "source_type": "url",
    "target_platform": "TikTok",
    "clip_count": 3
  }'
```

Create an async job:

```bash
curl -X POST http://127.0.0.1:8000/v1/jobs \
  -H 'Content-Type: application/json' \
  -H 'x-lwa-client-id: local-readme' \
  -d '{
    "prompt": "Rank clip opportunities for a creator talking about direct uploads.",
    "source_type": "prompt",
    "target_platform": "TikTok"
  }'
```

Upload a source file:

```bash
curl -X POST http://127.0.0.1:8000/v1/uploads \
  -H 'x-lwa-client-id: local-readme' \
  -F 'file=@/absolute/path/to/source.mp4'
```

Use the returned `file_id` as `upload_file_id` in `/generate`.

## Railway Deploy

Backend service:

- Root directory: `lwa-backend/`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Attach the generated-assets volume and set `LWA_GENERATED_ASSETS_DIR` to that mount path.
- Keep `FREE_LAUNCH_MODE=true` only while public launch testing is intended.

Frontend service:

- Root directory: `lwa-web/`
- Build command: `npm install && npm run build`
- Start command: `npm run start`
- Required env: `NEXT_PUBLIC_API_BASE_URL=https://lwa-backend-production-c9cc.up.railway.app`
- Set `NEXT_PUBLIC_FREE_LAUNCH_MODE=true` only when backend `FREE_LAUNCH_MODE=true`.

## Verification

Backend:

```bash
cd /Users/bdm/LWA/lwa-app
python3 -m compileall lwa-backend/app lwa-backend/scripts
cd lwa-backend && python3 -m unittest discover -s tests
```

Frontend:

```bash
cd /Users/bdm/LWA/lwa-app/lwa-web
npm run type-check
```

Whitespace:

```bash
cd /Users/bdm/LWA/lwa-app
git diff --check
```

## Claim Safety

Do not claim guaranteed virality, guaranteed views, guaranteed revenue, direct social posting, private-video bypass, automated Whop payouts, or full Twitch live ingestion unless those paths are implemented and verified. The safe claim is: LWA helps prepare ranked clip packages through an upload-first workflow with rendered output when possible and strategy-only fallback when needed.
