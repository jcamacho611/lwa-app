# LWA Public Launch Hardening Checklist

Last updated: 2026-04-30

## Goal

Prepare LWA for public demo/free-launch traffic without breaking the existing clipping MVP or overclaiming unfinished systems.

## Required health checks

Run these before each launch push:

```bash
python3 -m compileall lwa-backend/app
cd lwa-backend && python3 -m unittest discover -s tests
cd ../lwa-web && npm run type-check
cd .. && git diff --check
```

If `npm run lint` or `npm run build` is stable in the current environment, also run:

```bash
cd lwa-web && npm run lint
cd lwa-web && npm run build
```

## Live smoke tests

### Backend

- [ ] `/health` or `/healthz` returns healthy.
- [ ] `/v1/generate` accepts a valid source request.
- [ ] `/v1/jobs` still returns/polls job state if configured.
- [ ] Upload route accepts allowed file types.
- [ ] Unsupported file type returns a clean user-facing error.
- [ ] Bad/blocked public URL returns degraded/strategy-only output or clean error, not raw yt-dlp/provider internals.

### Frontend

- [ ] Home/generate page loads.
- [ ] Source input works.
- [ ] Upload UI matches allowed backend source contract.
- [ ] Rendered clips display as playable/exportable only when a URL exists.
- [ ] Strategy-only clips display as strategy-only and do not fake previews/downloads.
- [ ] Director Brain fields are optional and do not crash older responses.
- [ ] Whop/money CTA opens configured external link.
- [ ] Free launch banner appears only when configured.

## FREE_LAUNCH_MODE

Backend env:

```bash
FREE_LAUNCH_MODE=true
RATE_LIMIT_GUEST_RPM=30
```

Frontend env:

```bash
NEXT_PUBLIC_FREE_LAUNCH_MODE=true
NEXT_PUBLIC_LWA_WHOP_URL=https://whop.com/lwa-app/lwa-ai-content-repurposer/
```

Rules:

- Free launch should not require completed paid webhook gating.
- Free launch should still have abuse prevention.
- Free launch should not hide the Whop path.
- Whop CTA is checkout/access intent, not verified entitlement until signed webhooks exist.

## Fallback safety

If source extraction, transcription, AI scoring, rendering, captions, or provider calls fail:

- return clean status/reason
- preserve request context
- provide strategy-only package if possible
- never leak raw stack traces
- never leak API keys, cookies, provider internals, yt-dlp internals, or bot-check details
- never mark failed render as ready

## Claim safety

Allowed launch claim:

> LWA turns creator sources into ranked short-form clip packages with hooks, captions, timestamps, scores, and workflow-ready packaging. Upload-first sources are supported; public URLs are best-effort because platforms can block extraction.

Avoid:

- guaranteed viral
- guaranteed income
- works with every platform link
- verified paid access unless webhooks exist
- marketplace payouts live
- social posting live
- NFT/blockchain live

## Manual launch test script

1. Open the Railway frontend.
2. Confirm page renders without console-breaking errors.
3. Submit one normal generation request.
4. Submit one blocked/bad URL request.
5. Upload one supported file if upload UI is enabled.
6. Confirm best clip appears first.
7. Confirm strategy-only outputs are visually distinct.
8. Copy hook, caption, CTA, and package.
9. Open Whop CTA.
10. Capture screenshots for sales/demo.

## Next code slice after checklist

Only after health checks pass:

1. Whop verified webhook MVP.
2. Caption style renderer deeper integration.
3. Quality gate deeper integration.
4. Operator dashboard metrics.
5. Marketplace scaffold without payouts.

## Do not start yet

- live Stripe Connect payouts
- Whop submerchant payouts
- NFT purchases
- blockchain contracts
- direct posting APIs
- iOS rebuild
