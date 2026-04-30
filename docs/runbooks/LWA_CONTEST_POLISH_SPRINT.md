# LWA Contest Polish Sprint — PR Summary

## What this PR fixed

### Phase 1 — Homepage CTA fallback
- All action cards now have fallback chains ending at `getPrimaryMoneyLink()`
- "Request custom clip pack" → demoForm || contact || booking || primary
- "Book demo" → booking || demoForm || contact || primary
- "Join creator/referral program" → affiliateForm || contact || primary
- "Add path when configured" placeholder state is now unreachable when env vars are missing
- Verified `DEFAULT_WHOP_URL` is correct: `https://whop.com/lwa-app/lwa-ai-content-repurposer/`

### Phase 2 — Guest generate UX
- **Live stream preflight**: URLs matching twitch.tv/, youtube.com/live, or /live/ now show a non-blocking amber notice with "Continue anyway" and "Upload file instead" before submitting
- **Strategy-only card**: Updated to show structured "Strategy-only package" title, "No playable preview was created for this source." subtext, body copy, and "Upload source file for rendered clips" button — no fake thumbnail, no video player frame
- **Export bundle**: Now forces real file download via Blob when backend returns JSON; filename is `lwa-clip-package-{request_id}.json` (rendered) or `lwa-strategy-bundle-{request_id}.json` (strategy-only)
- **Button label**: Export button shows "Download Clip Package" or "Download Strategy Bundle" depending on rendered clip presence
- **Result ordering**: Clip cards now show Hook → Caption → Score → Timestamp → Recovery guidance (degraded only) → Platform recommendation (available only)
- **402 paywall card**: Shows "You have used your free launch credits." with "Join Waitlist" and "Save my work" buttons; no raw error strings

### Phase 3 — Agent and council registries
- Created `lwa-web/lib/lwa-agents.ts` with 7 agents (omega-prime, jackal-warden, veil-oracle, iron-seraph, horned-sentinel, shadow-scribe, grave-monk)
- Created `lwa-web/lib/production-council.ts` with 9 council roles
- Added homepage council line: "The Council builds the system. The characters guide the world." with "How LWA is built" eyebrow

### Phase 4 — Contrast
- Strategy-only card text bumped from `text-ink/62` to `text-ink/80` for body copy readability

### Phase 5 — Docs
- `docs/showcase/LWA_AI_SHOWCASE_SUBMISSION.md` — contest submission template
- `docs/runbooks/LWA_LIVE_SMOKE_TEST.md` — smoke test checklist with API spending decision tree
- `docs/runbooks/LWA_CONTEST_POLISH_SPRINT.md` — this file

## What was NOT changed
- iOS (lwa-ios/) — untouched
- Backend business logic — untouched
- Marketplace payout logic — untouched
- Blockchain or social posting claims — untouched
- Pricing copy — untouched
- Safety language — untouched
- Route shapes or status codes — untouched

## What remains
- Auth and ownership (Issue 72) — next sprint
- Director Brain deeper wiring — queued
- Live smoke test against production Railway deployment — required before claiming submission ready
- Screenshot capture for showcase submission
- Final readiness score (fill in after smoke test)

## Verification
- Backend compile: `python3 -m compileall lwa-backend/app lwa-backend/scripts`
- Frontend type-check: `cd lwa-web && npm run type-check`
- Frontend build: `cd lwa-web && npm run build`
