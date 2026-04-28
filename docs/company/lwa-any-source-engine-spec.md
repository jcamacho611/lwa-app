# LWA Any-Source Engine Spec

## Purpose
This document defines the product and architecture expectations for the any-source engine.

## Engine Law

The source engine must not assume the user is always bringing a public video URL.

The engine must support, when technically possible:

- `video`
- `audio`
- `music`
- `prompt`
- `twitch`
- `stream`
- `campaign`
- `upload`
- `url`
- `unknown`

## Source Branch Expectations

### Video

Expected output:

- ranked clip packages
- timestamps when available
- hooks
- captions
- score and post order
- rendered assets when possible

### Audio

Expected output:

- quote moments
- hooks
- captions
- scripts
- visual prompts
- packaging strategy

### Music

Expected output:

- promo concepts
- visual ideas
- hook options
- short-form packaging
- safe non-lyrical promotional copy

### Prompt

Expected output:

- scripts
- hooks
- captions
- thumbnail text
- CTA suggestions
- visual generation prompts
- strategy package

### Twitch / Stream

Expected output:

- highlight angles
- streamer clip hooks
- community-aware packaging
- post order for short-form repurposing

### Campaign / Objective

Expected output:

- campaign-fit packages
- manual review notes
- platform fit
- compliance reminders when available

### Upload / File

Expected output:

- same creator-ready package path as public sources when processing succeeds

## Fallback Rules

If real media cannot be processed:

- do not fail silently
- do not dump raw extractor logs to the user
- do return a strategy-only package when possible
- do explain safe next steps in plain English

## Current Repo Alignment

Current repo foundation already points in this direction, but the engine is not fully aligned yet.

Needs more work in:

- request schema normalization
- source_type routing
- audio and prompt-only output consistency
- Twitch / stream metadata handling
- blocked-platform fallback quality

## Safety Rules

- do not imply private bypass
- do not imply universal source support before verified
- do not imply rendered media exists when it does not

## Testing Expectations

Test cases must include:

- video source
- audio source
- music source
- prompt-only source
- Twitch / stream source
- campaign objective source
- blocked platform fallback
- unsupported source fallback

