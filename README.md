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

### Core Configuration
| Var | Service | Purpose | Default |
| --- | --- | --- | --- |
| `FREE_LAUNCH_MODE` | backend | Enables public launch mode without forcing auth. Set to `true` for public testing. | `false` |
| `RATE_LIMIT_GUEST_RPM` | backend | Requests per IP per minute for free-launch anonymous traffic. | `30` |
| `NEXT_PUBLIC_FREE_LAUNCH_MODE` | web | Shows free-launch banner and hides sign-in CTAs. | `false` |
| `NEXT_PUBLIC_API_BASE_URL` | web | Backend base URL used by the browser app. | Required |

### Storage & Processing
| Var | Service | Purpose | Default |
| --- | --- | --- | --- |
| `LWA_GENERATED_ASSETS_DIR` | backend | Directory or Railway volume path for generated clips/assets. | Auto-detected |
| `LWA_GENERATED_ASSETS_RETENTION_HOURS` | backend | Max age before generated asset cleanup removes old files. | `24` |
| `LWA_GENERATED_ASSETS_MAX_FILES` | backend | Max generated file count before oldest files are trimmed. | `300` |
| `LWA_ASSET_CLEANUP_ON_STARTUP` | backend | Runs nonfatal generated asset cleanup during startup. | `true` |
| `LWA_UPLOADS_DIR` | backend | Upload storage directory. | Auto-detected |
| `LWA_USAGE_STORE_PATH` | backend | Local JSON quota store path for free/API-key usage. | Auto-detected |
| `MAX_UPLOAD_MB` | backend | Upload size cap in megabytes. | `500` |

### AI Providers (Optional)
| Var | Service | Purpose | Default |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | backend | OpenAI API key. Product degrades gracefully if unavailable. | Optional |
| `ANTHROPIC_API_KEY` | backend | Anthropic API key. Product degrades gracefully if unavailable. | Optional |
| `LWA_AI_PROVIDER` | backend | Preferred AI provider (`auto`, `openai`, `anthropic`). | `auto` |

### Media Processing
| Var | Service | Purpose | Default |
| --- | --- | --- | --- |
| `FFMPEG_PATH` | backend | FFmpeg binary path override. | Auto-detected |
| `LWA_VIDEO_ENCODER` | backend | Video encoder for rendering. | `libx264` |
| `YT_COOKIES_B64` | backend | Base64-encoded YouTube cookies for improved access. | Optional |

### Rate Limiting & Quotas
| Var | Service | Purpose | Default |
| --- | --- | --- | --- |
| `LWA_FREE_DAILY_LIMIT` | backend | Daily generation limit for free users. | `10` |
| `LWA_PRO_DAILY_LIMIT` | backend | Daily generation limit for pro users. | `25` |
| `LWA_SCALE_DAILY_LIMIT` | backend | Daily generation limit for scale users. | `100` |
| `LWA_FREE_CLIP_LIMIT` | backend | Max clips per request for free users. | `3` |
| `LWA_PRO_CLIP_LIMIT` | backend | Max clips per request for pro users. | `6` |
| `LWA_SCALE_CLIP_LIMIT` | backend | Max clips per request for scale users. | `12` |

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

### Backend Service
- **Root directory:** `lwa-backend/`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Volume:** Attach generated-assets volume and set `LWA_GENERATED_ASSETS_DIR` to mount path
- **Environment:**
  - `FREE_LAUNCH_MODE=true` for public testing (set to `false` for production)
  - `RATE_LIMIT_GUEST_RPM=30` (adjust based on traffic needs)
  - `OPENAI_API_KEY` and/or `ANTHROPIC_API_KEY` for AI processing
  - `MAX_UPLOAD_MB=500` (adjust based on storage limits)

### Frontend Service
- **Root directory:** `lwa-web/`
- **Build command:** `npm install && npm run build`
- **Start command:** `npm run start`
- **Required environment:**
  - `NEXT_PUBLIC_API_BASE_URL=https://lwa-backend-production-c9cc.up.railway.app`
  - `NEXT_PUBLIC_FREE_LAUNCH_MODE=true` (match backend setting)

### Production Deployment Notes
1. **FREE_LAUNCH_MODE:** Set to `false` for production with authentication, `true` for public testing
2. **Rate Limiting:** Adjust `RATE_LIMIT_GUEST_RPM` based on expected traffic and server capacity
3. **AI Keys:** Ensure at least one AI provider key is configured for optimal performance
4. **Storage:** Monitor generated-assets volume usage and adjust retention settings as needed
5. **Monitoring:** Check `/health` endpoint regularly to verify system status

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
