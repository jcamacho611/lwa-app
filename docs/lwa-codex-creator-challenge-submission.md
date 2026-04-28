# LWA Codex Creator Challenge Submission

## Product title

LWA — Director Brain for ranked short-form clips

## Short description

LWA turns one source into a ranked short-form clip pack with Director Brain shot plans, strategy-only fallback states, and rendered-first packaging so creators always know what to post first and what can be recovered later.

## Technical summary

LWA is a monorepo with:

- a FastAPI backend for source ingest, scoring, packaging, render orchestration, and fallback-safe generation
- a Next.js frontend that surfaces `Best clip first`, `Shot plan ready`, rendered-vs-strategy-only state, and recovery actions
- an offline-safe Director Brain layer that attaches:
  - `shot_plan`
  - `visual_engine_status`
  - `rendered_by`
  - `strategy_only_reason`
  - `recovery_recommendation`
- a heuristic fallback path that still returns ranked clips, multiple hook variants, packaging copy, and posting guidance when paid AI providers are unavailable

## What Codex helped build

Codex was used to ship the sprint in focused layers:

1. Day 1 — Director Brain backend foundation
   - `shot_planner.py`
   - `render_quality.py`
   - `visual_render_provider.py`
   - offline-safe provider states and backend tests
2. Day 2 — visible app integration
   - Director Brain fields attached to generation responses
   - `HeroClip`, `VideoCard`, and `clip-studio` updated to show:
     - `Best clip first`
     - `Rendered by LWA`
     - `Visual render ready`
     - `Strategy only`
     - `Shot plan ready`
     - `Recover render`
3. Day 3 — challenge polish
   - fallback score spread improvements
   - stronger hook variety without paid APIs
   - demo docs, smoke tests, and submission material

## Why it matters

Most clipping tools either hide their scoring logic or fail hard when rendering is blocked. LWA keeps the output useful:

- rendered clips stay first-class when they exist
- strategy-only clips are clearly labeled instead of being treated like broken output
- the user still gets a post order, hook options, and a shot plan they can act on

That makes LWA more honest, more demo-safe, and more useful in real creator workflows.

## 30-second investor / customer demo

### What to show on screen

1. Open `/generate`
2. Paste a source URL or upload a source file
3. Run generation
4. Land on the result with the lead clip visible
5. Expand the lead clip shot plan

### What to say

“LWA turns one source into a ranked clip stack. This lead clip is marked `Best clip first`, the shot plan is already attached, and the app tells you whether the clip is rendered now or still strategy-only. Even when premium rendering is unavailable, LWA still returns a useful posting plan instead of a dead end.”

## 60-second Codex Creator Challenge demo

### What to show on screen

1. Start on the `/generate` page
2. Paste a public source URL or direct MP4
3. Generate the clip pack
4. Point out:
   - `Best clip first`
   - `Shot plan ready`
   - `Rendered by LWA` or `Strategy only`
5. Expand the shot plan and show:
   - `hook`
   - `context`
   - `payoff`
   - `loop_end`
6. Show one alternate hook from the returned variants
7. Mention that the fallback path still ranks clips and returns packaging guidance without paid AI access

### What to say

“Codex helped turn LWA from a clip generator into a Director Brain system. The backend now plans shots, labels render states, and preserves strategy-only output. The frontend surfaces that intelligence clearly, so creators know what to post first, what is ready now, and what can be recovered later. Even offline-safe fallback mode still returns ranked clips, hooks, packaging copy, and a usable shot plan.”

## Exact smoke test checklist

### Normal generation

1. Open `/generate`
2. Paste a public source URL
3. Generate
4. Confirm:
   - `Best clip first`
   - `Shot plan ready`
   - ranked clips appear

### YouTube blocked / fallback path

1. Paste a public YouTube URL that Railway cannot ingest
2. Confirm the app still returns a useful explanation or strategy-only output
3. Confirm the UI does not collapse into a blank failure state

### Upload path

1. Upload a source file if available
2. Confirm generation still returns a clip pack

### Strategy-only output

1. Confirm at least one clip can render as strategy-only
2. Confirm it still shows:
   - `Strategy only`
   - `Shot plan ready`
   - `Recover render` when applicable

### Rendered output

1. Confirm rendered clips show `Rendered by LWA`
2. Confirm the lead clip remains `Best clip first`

### Director Brain labels

1. Expand a clip
2. Confirm the four shot plan beats are present
3. Confirm no customer-facing provider vendor names are exposed

### Scope protection

1. Confirm no `lwa-ios/` files changed in the sprint
