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
