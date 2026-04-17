# Claude & Seedance Integration — LWA

## Overview

This document covers the Anthropic (Claude) and Seedance integrations
added to LWA's backend and frontend. Both integrations are additive —
existing OpenAI, Ollama, and fallback flows are fully preserved.

---

## Environment Variables

### Anthropic (Claude)

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | `""` | Anthropic API key. When empty, Claude is unavailable. |
| `ANTHROPIC_MODEL_SONNET` | `claude-sonnet-4-20250514` | Default production model. |
| `ANTHROPIC_MODEL_OPUS` | `claude-opus-4-20250514` | Premium / high-depth reasoning model. |
| `ANTHROPIC_MODEL_HAIKU` | `claude-haiku-3-20240307` | Lightweight tagging model. |
| `LWA_ENABLE_ANTHROPIC` | `true` | Master toggle for Anthropic support. |
| `LWA_PREMIUM_REASONING_PROVIDER` | `anthropic` | Which provider to use for premium-tier reasoning. |

### Seedance (Premium Visual Generation)

| Variable | Default | Description |
|---|---|---|
| `SEEDANCE_ENABLED` | `false` | Master toggle. Must be `true` to activate. |
| `SEEDANCE_API_KEY` | `""` | Seedance API key. Required when enabled. |
| `SEEDANCE_BASE_URL` | `""` | Seedance API base URL. Required when enabled. |
| `SEEDANCE_MODEL` | `seedance-1-lite` | Model to use for generation. |
| `SEEDANCE_TIMEOUT_SECONDS` | `120` | HTTP timeout for Seedance API calls. |
| `SEEDANCE_POLL_INTERVAL_SECONDS` | `5` | Polling interval for job status. |

### Existing (Preserved)

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key — still fully supported. |
| `OPENAI_MODEL` | OpenAI model name. |
| `LWA_AI_PROVIDER` | Provider routing: `auto`, `openai`, `anthropic`, `ollama`, `heuristic`. |
| `OLLAMA_BASE_URL` | Ollama endpoint (if using local models). |
| `OLLAMA_MODEL` | Ollama model name. |

---

## Provider Routing

When `LWA_AI_PROVIDER=auto` (the default):

1. **Anthropic** — if `ANTHROPIC_API_KEY` is set and `LWA_ENABLE_ANTHROPIC=true`
2. **OpenAI** — if `OPENAI_API_KEY` is set
3. **Ollama** — if `OLLAMA_BASE_URL` is set
4. **Heuristic fallback** — always available

When `LWA_AI_PROVIDER=anthropic`:
- Uses Anthropic directly
- Falls through to OpenAI, then fallback, on error

When `LWA_AI_PROVIDER=openai`:
- Uses OpenAI directly
- Falls through to fallback on error

### Premium Reasoning

When a request qualifies for premium reasoning (based on existing plan/entitlement logic):
- If `LWA_PREMIUM_REASONING_PROVIDER=anthropic`, uses Claude Opus
- Otherwise, uses the normal provider with the standard model

---

## Fallback Behavior

Every provider path has strict fallback:

- If Anthropic returns malformed JSON → falls through to OpenAI
- If OpenAI fails → falls through to Ollama
- If Ollama fails → uses heuristic fallback
- Heuristic fallback produces structured clips from source context
  without any external API call

---

## What Is Live Now

### Claude Integration (Phase 1) ✅
- `anthropic_service.py` — full provider with Sonnet/Opus/Haiku support
- Provider routing updated in `generation.py` and `ai_service.py`
- Attention compiler updated in `attention_compiler.py`
- All existing flows preserved

### Seedance Adapter (Phase 2) — Adapter Only 🟡
- `seedance_service.py` — clean adapter boundary
- Routes at `/v1/seedance/background` and `/v1/seedance/jobs/{job_id}`
- Schemas for request/response
- Disabled by default (`SEEDANCE_ENABLED=false`)

**What is pending:** The exact Seedance HTTP API contract (auth format,
endpoint paths, request/response shapes) is unconfirmed. The adapter
contains best-guess placeholders clearly marked with `# ADAPTER NOTE`
comments. Once the contract is confirmed, only `seedance_service.py`
needs updating — no other files touch Seedance HTTP details.

### Frontend Premium Background (Phase 3) ✅
- `AIBackground.tsx` — `SeedancePremiumLayer` component
- Non-blocking: loads asynchronously, falls back to nothing
- Existing background layers remain fully visible underneath
- Only active on the home variant

---

## How to Enable / Disable

### Enable Claude
```bash
ANTHROPIC_API_KEY=sk-ant-...
LWA_ENABLE_ANTHROPIC=true
LWA_AI_PROVIDER=auto        # or explicitly "anthropic"
```

### Disable Claude
```bash
LWA_ENABLE_ANTHROPIC=false
# or simply remove ANTHROPIC_API_KEY
```

### Enable Seedance
```bash
SEEDANCE_ENABLED=true
SEEDANCE_API_KEY=...
SEEDANCE_BASE_URL=https://api.seedance.ai
```

### Disable Seedance (default)
```bash
SEEDANCE_ENABLED=false
# or simply leave SEEDANCE_API_KEY empty
```

---

## Files Changed

| File | Change |
|---|---|
| `lwa-backend/app/core/config.py` | Added Anthropic + Seedance env vars |
| `lwa-backend/requirements.txt` | Added `anthropic` SDK |
| `lwa-backend/app/services/anthropic_service.py` | **New** — Claude provider |
| `lwa-backend/app/services/seedance_service.py` | **New** — Seedance adapter |
| `lwa-backend/app/generation.py` | Added anthropic provider path |
| `lwa-backend/app/services/ai_service.py` | Updated resolve_attention_mode |
| `lwa-backend/app/services/attention_compiler.py` | Added anthropic compiler path |
| `lwa-backend/app/models/schemas.py` | Added Seedance schemas |
| `lwa-backend/app/api/routes/seedance.py` | **New** — Seedance routes |
| `lwa-backend/app/main.py` | Registered seedance router |
| `lwa-web/components/AIBackground.tsx` | Added SeedancePremiumLayer |
| `docs/claude-seedance-integration.md` | **New** — this document |

---

## Railway Deployment

No changes to deployment configuration. All new behavior is gated behind
environment variables. Set them in your Railway service's Variables panel.
The app starts and runs normally with zero new env vars configured.
