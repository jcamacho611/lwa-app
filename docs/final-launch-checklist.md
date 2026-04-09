# Final Launch Checklist

This is the final manual checklist to get LWA from codebase to a live paid product.

## What Is Already Done In Code

- FastAPI backend with:
  - `/`
  - `/health`
  - `/v1/trends`
  - `/v1/jobs`
  - `/v1/jobs/{job_id}`
  - `/process`
  - `/v1/generate`
- Real `yt-dlp` video download path
- Real `ffmpeg` MP4 clip generation
- Transcript-aware clip selection when subtitles exist
- Async job queue with polling
- SwiftUI iOS client that polls jobs and displays asset links
- Railway config in [railway.toml](/Users/bdm/LWA/lwa-backend/railway.toml)
- Render config in [render.yaml](/Users/bdm/LWA/render.yaml)

## Railway Final Steps

1. Create a Railway service from `jcamacho611/lwa-app`
2. Set `Root Directory` to `lwa-backend`
3. Set config path to `/lwa-backend/railway.toml`
4. Attach a volume at `/data`
5. Set these variables:
   - `ENVIRONMENT=production`
   - `LWA_APP_NAME=LWA Backend`
   - `OPENAI_API_KEY=...`
   - `ALLOWED_ORIGINS=*`
6. Optional:
   - `API_BASE_URL=https://your-custom-domain.com`
   - `LWA_GENERATED_ASSETS_DIR=/data/lwa-generated`
7. Deploy
8. Verify:
   - `/`
   - `/health`
   - `/docs`
   - `/v1/trends`

## Backend Smoke Test

Run this locally:

```bash
cd /Users/bdm/LWA/lwa-backend
python3 scripts/smoke_test.py
```

Run this against Railway:

```bash
cd /Users/bdm/LWA/lwa-backend
python3 scripts/smoke_test.py https://YOUR-RAILWAY-URL
```

## Whop Final Steps

1. Confirm the product is not unintentionally free
2. Keep these plans:
   - Free
   - Pro $19/month
   - Scale $49/month
3. Confirm the paid plans are the only plans granting full app value
4. Set the app or experience base URL to your deployed backend or hosted app flow
5. Keep the product copy aligned to:
   - more clips
   - more views
   - more Whop income
6. Confirm onboarding includes:
   - Start Here
   - App Access
   - Community
   - Tutorials
   - Updates

## iOS Final Steps

1. Deploy the backend first
2. Update the production API URL in:
   - [Info.plist](/Users/bdm/LWA/lwa-ios/LWA/Info.plist)
   - or the in-app Settings screen
3. Replace the placeholder checkout URL with your real payment URL
4. Run the app in the simulator and generate clips from:
   - a direct MP4 URL
   - a YouTube URL
5. Confirm:
   - trend radar loads
   - job status updates
   - clip asset links open
   - share output includes asset URLs

## What Still Requires External Accounts

- Railway deployment
- Whop pricing and access controls
- OpenAI billing and API key
- TikTok, YouTube, Instagram, and Facebook publishing credentials
- App Store or TestFlight release workflow

## Launch Decision Rule

Do not block launch on:

- social auto-posting
- auth complexity
- analytics polish
- team features

Do launch once:

- backend is live
- iOS app points to production backend
- Whop pricing is correct
- clip generation works
- checkout link is real
