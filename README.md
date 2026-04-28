# LWA / IWA

LWA turns one source into ranked short-form clips with Director Brain shot plans, fallback-safe hook variants, and an honest rendered-vs-strategy-only workflow. The system is designed to stay useful even when paid AI providers are unavailable: the app still returns a structured clip pack, ranking, packaging guidance, and recovery states instead of a dead end.

## What LWA ships today

- Ranked clip packs with **Best clip first** ordering
- Director Brain metadata on each clip:
  - `shot_plan`
  - `rendered_by`
  - `visual_engine_status`
  - `strategy_only_reason`
  - `recovery_recommendation`
- Strategy-only fallback that still returns:
  - usable hooks
  - packaging angle
  - thumbnail text
  - CTA suggestion
  - posting order
- Rendered-first UI with a separate strategy-only lane
- Recovery actions that preserve useful output when rendering is unavailable

## Quick demo flow

1. Open `https://lwa-the-god-app-production.up.railway.app/generate`
2. Paste a public source URL or upload a source file
3. Generate the clip pack
4. Confirm the lead card shows:
   - `Best clip first`
   - `Shot plan ready`
   - either `Rendered by LWA` / `Visual render ready` or `Strategy only`
5. Expand a clip and review the `hook`, `context`, `payoff`, and `loop_end` shot plan

## Tech stack

- **Backend:** FastAPI, ffmpeg, yt-dlp, SQLite-backed persistence
- **Frontend:** Next.js, TypeScript, Tailwind + design tokens
- **Intelligence layers:** LWA Director Brain, attention compiler, fallback packaging heuristics
- **Deployment:** Railway

## Demo and submission docs

- `docs/lwa-omega-visual-engine.md`
- `docs/lwa-codex-creator-challenge-submission.md`

## Repo Layout

```text
LWA/
├── README.md
├── docs/
├── lwa-backend/
│   ├── README.md
│   ├── requirements.txt
│   ├── runtime.txt
│   └── app/
├── lwa-web/
│   ├── README.md
│   ├── package.json
│   └── app/
└── lwa-ios/
    ├── README.md
    ├── LWA.xcodeproj/
    └── LWA/
```

## Railway Deploy

### Backend Service

- Root Directory = `lwa-backend/`
- Start Command = `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `lwa-ios/` is not a Railway deployment target

### Frontend Service

- Root Directory = `lwa-web/`
- Build Command = `npm install && npm run build`
- Start Command = `npm run start`
- Environment Variable = `NEXT_PUBLIC_API_BASE_URL=https://lwa-backend-production-c9cc.up.railway.app`

`lwa-web/` is a standalone browser frontend and can be linked from Whop, your own domain, Gumroad, Lemon Squeezy, and any other URL-based flow.

Operational frontend routes now include:

- `/`
- `/login`
- `/signup`
- `/dashboard`
- `/upload`
- `/generate`
- `/history`
- `/batches`
- `/campaigns`
- `/wallet`
- `/settings`

## Backend Notes

The Railway service should deploy only the FastAPI backend from `lwa-backend/`.

Required backend endpoints:

- `GET /`
- `GET /health`
- `POST /generate`
- `POST /process`
- `POST /v1/jobs`

Local backend run:

```bash
cd lwa-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend checks commonly used in this repo:

```bash
cd lwa-backend
python3 -m unittest tests.test_attention_compiler tests.test_director_brain_integration tests.test_render_quality
```

## iOS Notes

`lwa-ios/` is for Xcode, Simulator, and device builds only.

Do not point Railway at `lwa-ios/`.
