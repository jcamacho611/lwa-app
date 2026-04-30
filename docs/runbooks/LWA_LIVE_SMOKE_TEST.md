# LWA Live Smoke Test Runbook

## Pages to test
| Page | URL | Pass |
|------|-----|------|
| Homepage | https://lwa-the-god-app-production.up.railway.app/ | |
| Generate | https://lwa-the-god-app-production.up.railway.app/generate | |
| Marketplace | https://lwa-the-god-app-production.up.railway.app/marketplace | |
| Operator | https://lwa-the-god-app-production.up.railway.app/operator | |
| Proof | https://lwa-the-god-app-production.up.railway.app/proof | |
| Realm | https://lwa-the-god-app-production.up.railway.app/realm | |
| Social | https://lwa-the-god-app-production.up.railway.app/social | |
| Whop | https://whop.com/lwa-app/lwa-ai-content-repurposer/ | |

## Backend health check
```
GET https://lwa-backend-production-c9cc.up.railway.app/health
```
Expected: 200 OK with status message.

## Generate smoke test — URL path
1. Go to /generate
2. Paste a public YouTube URL (non-live, non-private)
3. Click Generate Clips
4. Verify result cards show hook first, then caption, score, timestamp
5. Verify strategy-only cards show "Strategy-only package" title and upload CTA
6. Click "Download Clip Package" or "Download Strategy Bundle"
7. Verify file downloads (not opened in browser tab)

## Generate smoke test — upload path
1. Go to /generate
2. Click "Upload file" and upload a short .mp4
3. Click Generate Clips
4. Verify same result structure as URL path test

## Live stream preflight test
1. Go to /generate
2. Paste a twitch.tv or youtube.com/live URL
3. Click Generate Clips
4. Verify preflight notice appears with "Continue anyway" and "Upload file instead"
5. Verify clicking "Continue anyway" proceeds to generation

## Whop access path test
1. Go to https://whop.com/lwa-app/lwa-ai-content-repurposer/
2. Verify page loads and product is listed
3. Verify homepage "Support the build" CTA points to Whop

## Railway env vars to verify
| Variable | Required | Note |
|----------|----------|------|
| FREE_LAUNCH_MODE | Backend | Enables free guest generation |
| NEXT_PUBLIC_FREE_LAUNCH_MODE | Frontend | Enables free launch UI mode |
| OPENAI_API_KEY | Backend | Primary intelligence provider |
| ANTHROPIC_API_KEY | Backend | Secondary intelligence provider |
| NEXT_PUBLIC_API_BASE_URL | Frontend | Must point to live backend URL |
| NEXT_PUBLIC_LWA_WHOP_URL | Frontend | Whop product page URL |

## Error decoding
| Symptom | Likely cause |
|---------|-------------|
| Backend 500 on /generate | Missing OPENAI_API_KEY or ANTHROPIC_API_KEY |
| Frontend cannot reach backend | NEXT_PUBLIC_API_BASE_URL missing or wrong |
| CORS error in browser console | API base URL mismatch or CORS not configured |
| All results are strategy-only | Video provider cannot access source URL |
| Backend 422 on generate | Request payload shape mismatch |

## Screenshots to capture
- [ ] Homepage hero (full width, dark background)
- [ ] /generate with a result loaded (hook-first card visible)
- [ ] Strategy-only card with "Upload source file for rendered clips" button
- [ ] Whop product page

## API spending decision tree

1. **Spend zero dollars** until live smoke testing identifies the missing provider.
2. If the intelligence provider key is missing, **spend $5–$10 on Anthropic first** (not OpenAI, not Seedance).
3. **Do not spend on Seedance video first** — strategy-only is acceptable for the launch run.
4. Keep **$10–$15 in reserve** for the post-smoke-test generation sprint.
5. Only add a video rendering provider after the text intelligence layer is confirmed working.
