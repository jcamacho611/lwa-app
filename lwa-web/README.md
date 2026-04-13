# LWA Web

Standalone web frontend for LWA / IWA.

## What It Includes

- public generator flow from URL or upload-backed sources
- login and signup surfaces
- dashboard, history, batch, campaign, wallet, and settings pages
- clip-pack history editor with lightweight metadata editing
- posting connection and scheduling groundwork

## Railway

- Root Directory: `lwa-web/`
- Build Command: `npm install && npm run build`
- Start Command: `npm run start`

## Environment

- `NEXT_PUBLIC_API_BASE_URL=https://lwa-backend-production-c9cc.up.railway.app`
- `LWA_BACKEND_URL=https://lwa-backend-production-c9cc.up.railway.app` (optional server-side alias)

## Local Run

```bash
cd lwa-web
npm install
npm run build
npm start
```

## Routes

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
