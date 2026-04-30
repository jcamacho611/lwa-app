# Phase 1 — Launch Hardening Proof Runbook

Updated: 2026-04-30

## Purpose

This runbook completes the Phase 1 council lane by tying the current repo implementation to a launch-proof checklist. It does not restart the build and does not introduce new runtime behavior.

## Council lane

Lead council: Principal Engineering Council

Supporting councils:
- AI / Media Pipeline Council
- DevOps / Infrastructure Council
- Product / UX Council

GitHub phase issue: #51

## Current implementation evidence

The current repo already includes these Phase 1 launch-hardening pieces:

- backend `Settings.free_launch_mode` reads `FREE_LAUNCH_MODE` / `LWA_FREE_LAUNCH_MODE`
- backend `Settings.rate_limit_guest_rpm` reads `RATE_LIMIT_GUEST_RPM` / `LWA_RATE_LIMIT_GUEST_RPM`
- generate route normalizes source type and handles upload/source routing
- source ingestion errors are classified before returning client errors
- usage quota is released on generation failures and throttle failures
- frontend `FreeLaunchBanner` renders only when `NEXT_PUBLIC_FREE_LAUNCH_MODE === "true"`
- backend quality gate distinguishes strategy-only packages from rendered asset claims

## Proof checklist

### 1. Free launch env proof

Required env vars:

```text
FREE_LAUNCH_MODE=true
NEXT_PUBLIC_FREE_LAUNCH_MODE=true
RATE_LIMIT_GUEST_RPM=30
```

Expected proof:

```text
- Backend settings expose free launch mode as true.
- Web banner renders in public launch mode.
- Guest/public generation remains allowed according to current entitlement behavior.
```

### 2. Source handling proof

Test cases:

```text
- valid YouTube/public URL
- raw domain normalized by frontend before submit
- missing media URL without strategy prompt
- upload_file_id that does not exist
- unsupported file/source type
```

Expected proof:

```text
- valid source continues through generation
- missing/invalid sources return controlled 4xx response
- quota is released on source failure
- frontend does not crash
```

### 3. Degraded output proof

Test provider-failure scenarios:

```text
- invalid OpenAI key
- invalid Anthropic key
- unavailable transcript/provider step
- unavailable render step
```

Expected proof:

```text
- response is controlled
- result status and reason are explicit
- no strategy-only package claims a playable URL
- quality gate warnings are visible when render readiness is low
```

### 4. Render-state proof

Required states:

```text
rendered
raw_only
strategy_only
failed
```

Expected proof:

```text
- rendered requires actual playable/downloadable asset
- raw_only requires raw asset
- strategy_only has packaging but no fake media player
- failed is not promoted as a ready clip
```

### 5. README/live URL proof

Live URLs to keep current:

```text
Frontend: https://lwa-the-god-app-production.up.railway.app
Backend: https://lwa-backend-production-c9cc.up.railway.app
```

Expected proof:

```text
- README or launch docs reference current URLs
- health endpoint path is documented
- generation endpoint path is documented
- env mapping is clear
```

## Verification commands

Run what exists in the current repo layout and record skipped commands with reason.

Backend:

```text
cd lwa-backend
python -m py_compile $(git ls-files '*.py')
pytest -x
```

Frontend:

```text
cd lwa-web
npm run type-check
npm run lint
npm run build
```

If a command does not exist, record:

```text
SKIPPED: command unavailable in package scripts
```

## Definition of done

Phase 1 is done when:

```text
- public launch env names are confirmed
- banner behavior is confirmed
- bad sources return controlled responses
- provider/render failures do not create fake playable clips
- quality gate output is visible or stored
- launch docs reference the current Railway URLs
- verification commands are run or explicitly skipped with reason
```

## Non-goals

Do not include these in Phase 1 finishing work:

```text
- marketplace runtime checkout
- direct social posting
- full editor
- blockchain minting
- iOS rebuild
- fake uploads
- fake analytics
```

## Next action

Use this runbook to run the Phase 1 verification pass and post results back to issue #51.
