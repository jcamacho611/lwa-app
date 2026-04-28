# LWA AI Prompt Systems Architecture

## Purpose
This document defines the AI prompt spine for Issue #24: the any-source God App realignment.

It exists to stop product drift.

LWA must not behave like:

- a YouTube-only clipper
- a Whop-only checkout shell
- a video-only workflow
- a generic clipping dashboard

LWA must behave like:

> Any source in. Creator-ready content out.

That means the AI layer must accept video, audio, music, prompts, Twitch or stream sources, campaign context, creator objectives, and uploaded files when technically possible, then generate ranked clips, hooks, captions, visuals, post order, strategy, and creator-ready packages.

## Master Prompt Law

> LWA is an any-source AI content engine for creators, clippers, agencies, streamers, and media operators.

The AI system must never drift into:

- YouTube-first reasoning
- Whop-first reasoning
- video-only assumptions
- fake rendered output
- fake campaign automation
- guaranteed viral or revenue claims

The AI system must always preserve:

- rendered vs strategy-only truth
- source limitations
- claim safety
- useful fallback behavior
- optional-field-safe output

## Architecture Layers

### 1. Source Understanding Layer
Normalizes the source before any clip or package generation.

Supported source directions:

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

Primary job:

- identify source type
- preserve source constraints
- choose the right prompt branch
- avoid pretending video exists when it does not

### 2. Packaging Intelligence Layer
Turns source context into useful creator-ready outputs.

Required outputs can include:

- ranked clips
- hooks
- hook variants
- captions
- caption variants
- caption style
- thumbnail text
- CTA suggestions
- visual generation prompts
- post order
- score and confidence
- score breakdown
- why-this-matters reasoning
- campaign notes

### 3. Render Truth Layer
Separates actual media output from strategy-only output.

Allowed labels:

- `rendered`
- `strategy_only`
- `render_limited`
- `failed`
- `unknown`

Rules:

- never invent playable media
- never show rendered truth without real asset URLs
- always return a useful strategy package if media fails

### 4. Fallback Safety Layer
Keeps the product useful when platforms, providers, or rendering fail.

Fallback behavior must:

- explain what happened in plain English
- avoid raw technical logs in primary user copy
- return safe next steps
- return hooks/captions/thumbnail text when enough context exists
- never imply private-content bypass

### 5. Provider Routing Layer
Chooses the best model path without letting any provider override product law.

Preferred routing:

- Anthropic for deep reasoning, campaign logic, and long-form strategy
- OpenAI for structured JSON and fast package generation
- deterministic local fallback when providers are unavailable
- visual engine for visual prompt and scene generation

Provider limits:

- no provider may override claim safety
- no provider may override rendered-vs-strategy truth
- no provider may override source limitations

### 6. Protocol Layer Alignment
All prompt work must map into the protocol layer before feature claims are made.

Prompt systems must align with:

- source protocol
- output package protocol
- event protocol
- connector protocol
- consent protocol
- reward protocol

This is how the AI layer stays connected to future Twitch, guild, consent, reward, and optional proof-of-contribution systems without becoming a pile of disconnected prompts.

## Current Repo Alignment

Current repo alignment is partial but real.

Implemented or in foundation form:

- backend Attention Compiler and retention scoring foundations
- fallback hook/caption/package logic
- rendered vs strategy-only contract direction
- packaging fields in backend/frontend types
- any-source direction now visible on the web homepage

Not fully aligned yet:

- backend source normalization is still not complete for every source type
- prompt-only and audio/music flows need stronger backend-first contracts
- Twitch and stream handling need a distinct typed source path
- frontend and iOS still need broader source-mode alignment

## Safety Rules

Forbidden:

- guaranteed viral results
- guaranteed views
- guaranteed revenue
- guaranteed payouts
- automatic posting claims
- campaign submission claims
- hidden compute
- hidden AI training
- hidden mining
- private-content bypass

Allowed:

- ranked content packages
- creator-ready outputs
- rendered when available
- strategy-only fallback
- manual campaign preparation
- helps prepare clips
- helps speed up repurposing

## Testing Expectations

Prompt systems are not complete because a prompt exists in a doc.

They are complete only when:

- the prompt path is implemented
- the output schema is typed
- fallback behavior is tested
- rendered-vs-strategy truth is preserved
- unsafe claims are filtered
- frontend/iOS can safely display the output

## Future Implementation Path

1. Finish backend any-source source typing.
2. Align generation requests to typed source branches.
3. Keep output schema backward-compatible.
4. Route provider-specific prompt templates through one shared prompt registry.
5. Add explicit prompt tests for video, audio, music, prompt-only, Twitch/stream, and campaign/objective input.
6. Connect prompt behavior into the protocol layer docs and implementation.

