# LWA Railway Smoke Test Runbook

Last updated: 2026-04-30

## Purpose

Use this after every merge to confirm Railway is running the correct LWA frontend/backend and that the public launch flow is safe.

## Live service targets

- Frontend: `https://lwa-the-god-app-production.up.railway.app`
- Backend: `https://lwa-backend-production-c9cc.up.railway.app`

## Smoke test order

### 1. Backend health

Open or curl the backend health route.

Confirm:

- backend responds
- no 500
- response is fast enough for demo use

### 2. Frontend loads

Open the live frontend.

Confirm:

- page loads
- no blank screen
- source input appears
- free launch state looks correct
- Whop CTA opens the configured Whop page

### 3. Generation happy path

Submit one known-safe source.

Confirm:

- request starts
- no frontend crash
- clip package returns
- best clip appears first
- hooks/captions/CTA copy buttons work
- Director Brain optional fields do not crash the UI

### 4. Failure path

Submit one bad or blocked URL.

Confirm:

- no raw stack trace
- no provider secret
- no extraction-tool internals
- clean degraded or strategy-only response
- failed render is not shown as playable

### 5. Upload path

Upload one supported file type if upload UI is enabled.

Confirm:

- backend accepts allowed file
- unsupported file gets a clean message
- source type stays stable

### 6. Whop webhook test after PR #37 merge

After the Whop webhook PR is merged and Railway has the correct backend settings, send a test event from Whop.

Confirm:

- valid signed event succeeds
- invalid signature fails
- replayed event is idempotent
- matching user plan updates only from signed event

## Required backend checks before public push

Run locally or through Codex:

```bash
python3 -m compileall lwa-backend/app
cd lwa-backend && python3 -m unittest discover -s tests
```

## Required frontend checks before public push

Run locally or through Codex:

```bash
cd lwa-web && npm run type-check
```

If stable in the environment, also run lint and build.

## Claim rules after smoke test

Allowed after smoke passes:

> LWA is live as an AI clipping MVP with ranked clip packages, hooks, captions, timestamps, scores, and export-ready packaging. Upload-first sources are supported. Public URLs are best-effort.

Allowed only after PR #37 is merged, deployed, configured, and tested:

> LWA supports Whop webhook-backed entitlement verification.

Not allowed yet:

- guaranteed viral
- guaranteed income
- marketplace payouts live
- direct social posting live
- blockchain product live
- every platform URL guaranteed

## Failure response

If smoke test fails:

1. capture route, timestamp, and error message
2. check Railway deploy logs
3. check environment settings
4. rollback to previous Railway deployment if public launch is affected
5. open a GitHub issue with exact repro
