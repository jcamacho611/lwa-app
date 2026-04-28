# Final Handoff

This is the shortest path to finish LWA/IWA from the current repo state.

## Current Repo State

- Branch: `main`
- Latest pushed commit: run `git log --oneline -1`
- Git remote: `origin`
- Worktree state when this file was written: clean
- iOS status:
  - Debug simulator build passed
  - Release device build passed
  - Archive passed
- Backend status:
  - local real clip pipeline fixed
  - macOS VideoToolbox-preferred encoding added
  - Railway deploy config present

## How To Save Your Work

If you change files later and want to save everything to GitHub:

```bash
cd /Users/bdm/LWA/lwa-app
git status
git add .
git commit -m "Describe what changed"
git push origin main
```

To verify nothing is pending:

```bash
cd /Users/bdm/LWA/lwa-app
git status --short --branch
git log --oneline -1
```

If `git status` prints only:

```text
## main...origin/main
```

then everything is already pushed.

## Railway: Exact Setup

Repository:

```text
https://github.com/jcamacho611/lwa-app
```

Service settings:

- Root Directory: `lwa-backend`
- Config file path: `/lwa-backend/railway.toml`
- Builder: `Dockerfile`
- Health check path: `/health`
- Recommended volume mount path: `/data`

Exact `railway.toml` already in repo:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 120
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Railway Variables To Set

Required:

```text
ENVIRONMENT=production
LWA_APP_NAME=LWA Backend
ALLOWED_ORIGINS=*
LOG_LEVEL=info
OPENAI_API_KEY=YOUR_REAL_OPENAI_KEY
FFMPEG_PATH=/usr/bin/ffmpeg
YT_DLP_TEMP_DIR=/tmp
LWA_VIDEO_ENCODER=auto
```

Recommended:

```text
LWA_DEFAULT_PLAN_NAME=Starter Trial
LWA_DEFAULT_CREDITS_REMAINING=2
LWA_DEFAULT_TURNAROUND=45 seconds
LWA_API_KEY_HEADER_NAME=x-api-key
LWA_API_KEY_SECRET=YOUR_OPTIONAL_SECRET
LWA_GENERATED_ASSETS_DIR=/data/lwa-generated
```

Optional:

```text
API_BASE_URL=https://lwa-backend-production-c9cc.up.railway.app
OPENAI_MODEL=gpt-4.1-mini
WHOP_API_KEY=YOUR_WHOP_KEY_IF_NEEDED
WHOP_COMPANY_ID=biz_5PkXdb9NPrZ6vk
```

Notes:

- If `API_BASE_URL` is unset on Railway, the backend can derive it from `RAILWAY_PUBLIC_DOMAIN`.
- If `LWA_GENERATED_ASSETS_DIR` is unset on Railway, the backend can derive storage from `RAILWAY_VOLUME_MOUNT_PATH`.
- If you want backend auth enabled, set `LWA_API_KEY_SECRET` and then set the same value in the iOS app `Settings` screen.

## Railway Checks After Deploy

Open these:

- `https://lwa-backend-production-c9cc.up.railway.app/`
- `https://lwa-backend-production-c9cc.up.railway.app/health`
- `https://lwa-backend-production-c9cc.up.railway.app/docs`

Expected health shape includes:

- `ffmpeg: true`
- `yt_dlp: true`
- `openai_key_present: true` once your key is set

## iOS Values Already In The App

From [`Info.plist`](/Users/bdm/LWA/lwa-ios/LWA/Info.plist):

- App name: `IWA`
- Production API URL: `https://lwa-backend-production-c9cc.up.railway.app`
- Checkout URL: `https://whop.com/lwa-app/lwa-ai-content-repurposer/`
- Privacy Policy URL: `https://github.com/jcamacho611/lwa-app/blob/main/docs/privacy-policy.md`
- Support URL: `https://github.com/jcamacho611/lwa-app/blob/main/docs/support.md`

## Final Manual Steps Outside The Repo

### Railway

1. Confirm the service uses the `lwa-backend` root directory.
2. Confirm a volume is attached at `/data`.
3. Add the required environment variables.
4. Redeploy.
5. Open `/health` and `/docs`.

### Whop

1. Confirm the main product page is correct:
   - `https://whop.com/lwa-app/lwa-ai-content-repurposer/`
2. Confirm the Free plan does not unintentionally give away premium value.
3. Keep paid plans attached to the real app/tool access.
4. If using backend-to-Whop auth later, set `WHOP_API_KEY`.

### Xcode / Apple

1. Open:
   - `/Users/bdm/LWA/lwa-ios/LWA.xcodeproj`
2. Select your Apple Developer team in `Signing & Capabilities`
3. Archive
4. Upload to App Store Connect
5. Fill App Store Connect metadata using:
   - [`docs/app-store-connect-pack.md`](/Users/bdm/LWA/docs/app-store-connect-pack.md)

## Exact Commands You Can Run

Local backend:

```bash
cd /Users/bdm/LWA/lwa-backend
source .venv/bin/activate
./scripts/dev_local.sh
```

Local smoke test:

```bash
cd /Users/bdm/LWA/lwa-backend
source .venv/bin/activate
python scripts/smoke_test.py http://127.0.0.1:8000
```

Open the iOS project:

```bash
open /Users/bdm/LWA/lwa-ios/LWA.xcodeproj
```

## Final GPT Prompt

Paste this into GPT when you want it to tell you exactly what remains:

```text
You are my release operator for the LWA / IWA project.

Use this exact current state:

- GitHub repo: jcamacho611/lwa-app
- Branch: main
- Latest commit: run `git log --oneline -1`
- Backend deploy target: Railway
- Railway backend URL: https://lwa-backend-production-c9cc.up.railway.app
- iOS app name: IWA
- Bundle ID: com.jcamacho611.lwa
- Production API URL in the app already points to Railway
- Checkout URL in the app already points to: https://whop.com/lwa-app/lwa-ai-content-repurposer/
- Privacy URL: https://github.com/jcamacho611/lwa-app/blob/main/docs/privacy-policy.md
- Support URL: https://github.com/jcamacho611/lwa-app/blob/main/docs/support.md
- Backend local real-clip pipeline is already working
- iOS Debug build passed
- iOS Release build passed
- iOS archive passed

I need:
1. the exact next manual steps left outside the repo
2. the order I should do them in
3. the Railway values I should verify
4. the App Store Connect values I should verify
5. the Whop values I should verify
6. a final go/no-go checklist

Do not redesign the product. Do not tell me to rebuild code that already exists. Work only from the current shipped repo state and produce a concise operator checklist.
```

## Go / No-Go Rule

You are good to proceed if all of these are true:

- `git status` is clean
- Railway `/health` is green
- Railway has `OPENAI_API_KEY`
- Whop checkout/product page is correct
- Xcode signing is set
- Archive uploads successfully

Do not block on extra polish once those are green.
