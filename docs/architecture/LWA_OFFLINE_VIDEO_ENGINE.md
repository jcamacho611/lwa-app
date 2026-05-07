# LWA Offline Video Engine

## Purpose

The offline video engine is the local-first processing foundation for the original LWA clipping product.
It inspects uploaded video files without calling paid providers and can produce deterministic clip candidates,
render plans, thumbnails, and proof data from local FFmpeg/ffprobe tooling.

## What it does

- Probes uploaded video files locally with `ffprobe`
- Detects candidate scene boundaries with FFmpeg when available
- Builds audio windows with local silence analysis
- Generates deterministic moment candidates for 15s, 30s, 45s, and 60s cuts
- Builds caption segments without paid transcription
- Scores candidates transparently with local signals
- Builds local render and thumbnail plans
- Renders clips only through local FFmpeg subprocess calls when enabled
- Produces proof records that explicitly show provider calls were not made

## What it does not do

- Does not call OpenAI, Runway, Replicate, or any paid provider
- Does not require API keys
- Does not post to social platforms
- Does not execute payouts or touch payments/crypto
- Does not mutate the existing `/generate` contract
- Does not delete the source file

## FFmpeg requirement

FFmpeg and ffprobe are required only when you want actual probing, scene detection, rendering, or thumbnails.
If FFmpeg is missing, the engine fails safely and returns structured unavailable status instead of crashing.

## Connection to `/generate`

This package is intentionally isolated from `/generate` in this slice.
That route remains untouched so the current generation contract keeps working.

The safe next integration step is to add a flag-gated path in the backend generation pipeline:

```text
LWA_OFFLINE_VIDEO_ENGINE_ENABLED=true
```

That flag should be checked only after the new package is validated in isolation.
If the integration path is risky, keep it out of `/generate` and call this engine from a separate offline endpoint or job runner first.

## Future local transcript option

Caption generation currently accepts an optional transcript string and otherwise emits placeholder captions.
The next safe step is a local transcription adapter, such as a bundled Whisper-based worker, still running without paid providers.

## Future render queue option

Rendering is synchronous in this foundation slice.
The next safe step is a local render queue or background job worker so long renders do not block request handling.

## Safety contract

The engine should always remain:

- deterministic
- local-first
- nonfatal on FFmpeg absence
- explicit about fallback behavior
- isolated from paid-provider workflows
