# LWA Omega Visual Engine

## Status

This document tracks the foundation layer for the LWA Omega Visual Engine.

This is **not** a proprietary video model.
This is the director-brain architecture that lets LWA:

- understand what kind of clip it has
- plan the shots in a structured way
- decide whether a clip is render-ready, strategy-only, recoverable, or failed
- keep provider execution behind an internal adapter

## Day 1 foundation

The first backend-only pass adds:

- optional `ClipResult` fields for director-brain metadata
- `shot_planner.py`
- `render_quality.py`
- `visual_render_provider.py`
- offline-safe provider states:
  - `disabled`
  - `missing-key`
  - `failed`
- backend tests for the new services

## What this foundation does

### Shot planner

The shot planner produces a structured four-beat plan per clip:

1. `hook`
2. `context`
3. `payoff`
4. `loop_end`

Each beat carries:

- duration
- camera direction
- visual direction
- motion direction
- text overlay guidance
- subtitle behavior
- transition guidance
- retention goal

### Render quality

The render quality evaluator labels output with LWA-owned states:

- `ready_now`
- `needs_review`
- `strategy_only`
- `render_failed`
- `recoverable`

This keeps the app honest even when no playable asset exists yet.

### Provider abstraction

The visual render provider adapter keeps the app contract stable:

- public provider id: `lwa_visual_engine`
- public rendered-by label: `LWA Omega Visual Engine`

Vendor-specific logic is intentionally left behind a TODO boundary and is **not**
wired in this phase.

## What is intentionally preserved

This phase does **not** change:

- routes
- auth
- plans / credits
- wallet
- campaigns
- uploads
- history
- queue
- recovery flow
- ffmpeg path handling
- current strategy-only fallback behavior
- `lwa-ios/`

## Next phases

### Day 2

- attach shot plans to generated clips
- add processing summary counts for visual-engine attempts and outcomes
- surface `Rendered by LWA`, `Visual render ready`, `Shot plan ready`, `Recover render`

### Day 3

- improve fallback hook/scoring quality
- polish demo docs
- finalize challenge/demo submission materials

## Day 3 fallback lane

The Day 3 pass hardens the offline-safe packaging path so LWA still feels intelligent when paid providers are blocked or intentionally disabled.

### What improves in fallback mode

- score spread is no longer flat across the pack
- hooks come back with stronger variety instead of near-duplicates
- packaging copy is more specific:
  - clearer `why_this_matters`
  - stronger thumbnail text
  - clearer CTA suggestions
- strategy-only clips keep:
  - Director Brain shot plans
  - render recovery guidance
  - visible explanation of why no playable asset exists yet

### Product contract

Day 3 keeps this promise:

- if a clip is rendered, show the ready lane clearly
- if a clip is strategy-only, still show the best hook, shot plan, and recovery path
- never hide a useful clip just because premium rendering is unavailable

## Smoke test checklist

### Normal generation

1. Open `/generate`
2. Paste a public source URL
3. Generate
4. Confirm:
   - `Best clip first`
   - `Shot plan ready`
   - ranked results are visible

### YouTube blocked / fallback path

1. Paste a YouTube source that cannot be ingested from Railway
2. Confirm LWA still returns a strategy-only or fallback-safe result when possible
3. Confirm the user-facing explanation stays plain English

### Upload path

1. Upload a direct video file if available
2. Confirm the app returns a clip pack even without live provider help

### Strategy-only output

1. Confirm at least one strategy-only result shows:
   - `Strategy only`
   - `Shot plan ready`
   - `Recover render` when applicable

### Rendered output

1. Confirm rendered clips show `Rendered by LWA`
2. Confirm the lead clip still holds the `Best clip first` position

### Director Brain visibility

1. Expand a clip
2. Confirm the four-beat plan is present:
   - `hook`
   - `context`
   - `payoff`
   - `loop_end`

### Scope protection

1. Confirm no `lwa-ios/` files were changed in this sprint pass
