# Claude And Seedance Integration

This document describes the additive provider and premium-visual architecture added to LWA without replacing the current generation spine.

## What Is Live Now

- Existing `/generate`, `/process`, and `/v1/jobs` flows remain the backbone.
- OpenAI support remains intact.
- Fallback/heuristic generation remains intact.
- Ollama support remains intact when configured.
- Anthropic routing is now available as a first-class provider.
- Premium reasoning can use Claude Opus when the current entitlement path unlocks `priority_processing`.
- Seedance is wired as a disabled-safe adapter boundary and background/enhancement integration surface.

## What Is Adapter-Only Right Now

Seedance job submission and polling remain adapter-only until the exact live vendor contract is confirmed for this repo.

That means:

- the config/env is present now
- the service boundary is present now
- the routes are present now
- disabled or incomplete config fails cleanly
- enabled config still returns a controlled provider error instead of pretending the vendor contract is confirmed

## Environment Variables

### Core Provider Routing

- `LWA_AI_PROVIDER`
  - Supported values: `auto`, `anthropic`, `openai`, `ollama`, `fallback`
  - Default: `auto`

### Anthropic

- `LWA_ENABLE_ANTHROPIC=true`
- `ANTHROPIC_API_KEY=`
- `ANTHROPIC_MODEL_OPUS=claude-opus-4-7`
- `ANTHROPIC_MODEL_SONNET=claude-sonnet-4-6`
- `ANTHROPIC_MODEL_HAIKU=claude-haiku-4-5-20251001`
- `LWA_PREMIUM_REASONING_PROVIDER=anthropic`

### OpenAI

- `OPENAI_API_KEY=`
- `OPENAI_MODEL=gpt-4.1-mini`

### Ollama

- `OLLAMA_BASE_URL=`
- `OLLAMA_MODEL=llama3.2`

### Seedance

- `SEEDANCE_ENABLED=false`
- `SEEDANCE_API_KEY=`
- `SEEDANCE_BASE_URL=`
- `SEEDANCE_MODEL=seedance-2.0`
- `SEEDANCE_TIMEOUT_SECONDS=180`
- `SEEDANCE_POLL_INTERVAL_SECONDS=3`

## Provider Routing Behavior

When `LWA_AI_PROVIDER=auto`, routing works like this:

1. Anthropic if enabled and `ANTHROPIC_API_KEY` is present
2. OpenAI if `OPENAI_API_KEY` is present
3. Ollama if `OLLAMA_BASE_URL` is present
4. fallback/heuristic generation otherwise

When `LWA_AI_PROVIDER` is explicitly set to `anthropic`, `openai`, `ollama`, or `fallback`, the app honors that choice and degrades safely if the required config is missing.

## Premium Reasoning Behavior

The current entitlement path already exposes `priority_processing`.

That flag is now reused for premium reasoning:

- standard flows: Anthropic Sonnet when Anthropic is active, otherwise the currently selected provider
- premium flows: Anthropic Opus when Anthropic is available and premium reasoning is enabled through the current plan path

This preserves the existing plan model. No new billing system was introduced.

## Homepage And Background Stability

Seedance is optional at runtime.

If Seedance is disabled or misconfigured:

- homepage render continues normally
- existing background fallback continues normally
- clip generation continues normally
- no vendor secret is exposed to the client

## How To Enable Anthropic Safely

1. Set `LWA_ENABLE_ANTHROPIC=true`
2. Set `ANTHROPIC_API_KEY`
3. Leave `LWA_AI_PROVIDER=auto` to prefer Anthropic automatically

Optional:

- set `LWA_PREMIUM_REASONING_PROVIDER=anthropic`
- override model env vars if needed

## How To Enable Seedance Safely

1. Set `SEEDANCE_ENABLED=true`
2. Set `SEEDANCE_API_KEY`
3. Set `SEEDANCE_BASE_URL`
4. Confirm the exact vendor job submission/polling contract before changing the adapter internals

Until the exact contract is confirmed, the adapter intentionally returns controlled errors instead of pretending the premium visual pipeline is fully live.
