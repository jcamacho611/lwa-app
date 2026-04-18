# LWA Web

Next.js 14 web frontend for the LWA AI Clip Generator.

## Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS (dark theme)
- **Runtime**: Node.js 18+

## Local Development

```bash
cd lwa-web
npm install
cp .env.local.example .env.local   # or edit .env.local directly
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Backend base URL | `http://127.0.0.1:8000` |

For local dev the backend should be running at `http://127.0.0.1:8000`.  
For production set `NEXT_PUBLIC_API_BASE_URL=https://lwa-backend-production-c9cc.up.railway.app`.

## Production Build

```bash
npm run build
npm run start
```

## Railway Deployment

| Setting | Value |
|---|---|
| Root Directory | `lwa-web` |
| Build Command | `npm install && npm run build` |
| Start Command | `npm run start` |
| Environment Variable | `NEXT_PUBLIC_API_BASE_URL=https://lwa-backend-production-c9cc.up.railway.app` |

Railway will auto-detect Node.js via Nixpacks. The `railway.toml` in this directory configures the build and deploy settings automatically.

## Project Structure

```
lwa-web/
├── railway.toml              # Railway config-as-code
├── next.config.js            # Next.js config (standalone output)
├── tailwind.config.ts        # Tailwind theme (dark, brand colours)
├── tsconfig.json
├── package.json
└── src/
    ├── app/
    │   ├── layout.tsx        # Root layout, metadata, fonts
    │   ├── page.tsx          # Main page (hero + input + results)
    │   └── globals.css       # Tailwind base + custom dark theme
    ├── components/
    │   ├── VideoInput.tsx    # URL input + platform selector + submit
    │   ├── ClipCard.tsx      # Individual clip with copy buttons
    │   └── ResultsDisplay.tsx # Results container + summary bar
    ├── hooks/
    │   └── useClipGeneration.ts  # Async generation state machine
    └── lib/
        ├── api.ts            # fetch wrapper for /generate
        └── types.ts          # TypeScript interfaces matching backend schemas
```

## API Integration

The frontend calls `POST /generate` on the backend:

```json
{
  "video_url": "https://...",
  "target_platform": "TikTok"
}
```

Response shape is typed in `src/lib/types.ts` and mirrors `ClipBatchResponse` from the backend's `lwa-backend/app/models/schemas.py`.

## Features

- Dark gradient UI with brand purple/indigo palette
- Video URL input with validation
- Platform selector (TikTok, Instagram Reels, YouTube Shorts, X, LinkedIn)
- Loading state with spinner
- Per-clip copy buttons for hook, caption, CTA, thumbnail text
- Hook variant expansion
- Transcript excerpt accordion
- Clip download links (edited / raw)
- Processing summary bar (plan, credits, AI provider)
- Error handling with user-friendly messages
- Fully responsive (mobile, tablet, desktop)
- Accessible (keyboard navigation, focus rings, ARIA labels)
