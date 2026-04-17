# LWA Master Execution Brief

**Repo:** `jcamacho611/lwa-app`  
**Primary branch:** `dev`  
**Do not work directly on `main`.**

## Mission

Turn LWA into the easiest, fastest, most premium-feeling clipping engine in the repo’s current direction by improving:

1. actual clip generation and preview reliability
2. Claude-powered intelligence quality
3. Seedance-safe premium visual infrastructure
4. homepage/background premium feel
5. UI simplicity for first-time users
6. overall operator-grade usability

This is **not** a rebuild.  
This is **not** a destructive refactor.  
This is an **additive, preservation-first upgrade**.

---

## Non-negotiable rules

- Preserve all existing working flows
- Do not rebuild the app
- Do not replace the current clipping engine
- Do not remove OpenAI/fallback behavior
- Do not rename stable routes unless absolutely necessary
- Do not break Railway deployment assumptions
- Do not break Whop/customer-facing flow
- Do not silently overwrite working code
- Do not let Seedance become a breaking dependency
- Do not make the UI more complicated
- Keep landing cinematic, but keep the interior product calmer and easier
- If a provider contract is uncertain, isolate it behind an adapter
- If something is not verified, fail gracefully rather than pretending it is live
- Work on `dev` or a feature branch off `dev` and open/update a PR when done

---

## Current repo seams to build on top of

### Backend

- `lwa-backend/app/api/routes/generate.py`
- `lwa-backend/app/services/clip_service.py`
- `lwa-backend/app/generation.py`
- `lwa-backend/app/services/ai_service.py`
- `lwa-backend/app/core/config.py`

### Product realities to preserve

- current generation flow
- current OpenAI support
- fallback support
- Railway assumptions
- Whop/customer-facing flow
- homepage/background fallback behavior when premium visual mode is unavailable

### Frontend realities to extend

- premium shell / hero layer
- `AIBackground` component
- generate/results workflow
- premium search/discovery surfaces
- no-rebuild path for adding premium visual mode

---

## Core product goal

LWA should feel like this:

### For first-time users

- instantly understandable
- cinematic but not confusing
- powerful immediately
- visibly useful in under 10 seconds

### For operators

- paste source
- choose very few necessary options
- generate
- see instant strategic intelligence while processing
- get actual preview
- get actual clips/files
- understand why the clips were chosen
- export/use them without friction

### Desired feeling

- premium
- Apple-level in restraint and clarity
- mythic in mood
- operator-grade in utility
- faster and easier than competitors
- more intelligent, not just more animated

---

## Phase 0 — Repo truth + safe branching

1. Inspect current repo truth on the target branch.
2. Report exact files already handling:
   - provider routing
   - generation
   - homepage background / hero
   - asset storage
   - video preview/render plumbing
3. Work on `dev` or create a feature branch off `dev`.
4. Open/update a PR at the end.
5. Do not silently overwrite working code.

Return a short **Reality Check** before major edits.

---

## Phase 1 — Actual video preview + real output reliability

This is one of the top priorities.

The app must not feel fake or locked up. First-time users must be able to see a real preview path and real generated assets.

### Tasks

1. inspect current preview/render/result plumbing end-to-end
2. ensure actual generated video assets are created when dependencies are present
3. ensure actual preview URLs resolve correctly
4. ensure frontend uses the right returned asset fields
5. ensure processing and completed states are obvious
6. if high-res final render takes time, expose a fast visible preview path first
7. do not break current routes

### Required behavior

- user can see that real clips are being generated
- user can preview a real asset when available
- result UI should prioritize preview clarity
- if assets are unavailable, UI should explain why cleanly instead of feeling broken

---

## Phase 2 — Radical simplicity UX pass

The app is too confusing right now. Make the job easier.

### Primary user flow

1. Paste source URL
2. Optional quick mode / pro mode
3. Generate
4. See instant intelligence
5. See preview/results
6. Export / copy / continue

### Do this by

- making **Paste link → Generate** the hero path
- hiding secondary controls behind progressive disclosure
- reducing visual competition
- reducing text clutter
- keeping advanced controls available but not dominant
- making first-time usage feel welcoming and obvious
- ensuring the first-time experience is not locked up or over-gated

For first-time users:

- give a fuller preview of product power
- let the experience itself sell the value
- remove unnecessary friction from first-use understanding

Do not oversimplify by removing important capability. Simplify by improving hierarchy.

---

## Phase 3 — Claude as first-class intelligence provider

Implement Claude as a first-class provider without removing existing providers.

### Update config in `lwa-backend/app/core/config.py`

Add:

- `ANTHROPIC_API_KEY`
- `ANTHROPIC_MODEL_OPUS=claude-opus-4-7`
- `ANTHROPIC_MODEL_SONNET=claude-sonnet-4-6`
- `ANTHROPIC_MODEL_HAIKU=claude-haiku-4-5-20251001`
- `LWA_ENABLE_ANTHROPIC=true`
- `LWA_PREMIUM_REASONING_PROVIDER=anthropic`

Preserve:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `LWA_AI_PROVIDER`
- fallback behavior
- Ollama support if already present

### Update requirements

- add official Anthropic SDK
- remove nothing existing

### Create

- `lwa-backend/app/services/anthropic_service.py`

### Responsibilities

- Sonnet for default production intelligence
- Opus for premium/high-depth reasoning
- Haiku for light cleanup/tagging/classification if useful
- normalize outputs into existing clip schema expectations
- improve:
  - hooks
  - hook variants
  - titles
  - captions
  - caption variants
  - thumbnail text
  - CTA suggestions
  - packaging angle consistency
  - `why_this_matters`
  - ranking quality
  - campaign-aware reasoning
- preserve robust malformed-output fallback behavior

### Refactor safely

- `lwa-backend/app/generation.py`
- `lwa-backend/app/services/ai_service.py`

### Behavior

- current behavior must keep working
- add provider routing for:
  - `anthropic`
  - `openai`
  - `ollama`
  - `fallback`
- when `LWA_AI_PROVIDER=auto`:
  - prefer Anthropic if `ANTHROPIC_API_KEY` exists
  - otherwise OpenAI if `OPENAI_API_KEY` exists
  - otherwise Ollama if configured
  - otherwise fallback

### Premium behavior

- reuse existing entitlement/plan logic if present
- do not invent a new billing system
- regular/basic flows can use Sonnet
- premium flows can use Opus

### Zero-wait perception improvement

- return useful strategic intelligence quickly
- if possible, surface hooks/titles/packaging reasoning before final clip export completes
- make the app feel fast even while rendering continues

---

## Phase 4 — Seedance as safe premium visual adapter

**Important:** do not fake an unverified live Seedance contract.

Implement Seedance as a provider adapter and premium visual pipeline boundary.

### Update config

- `SEEDANCE_ENABLED=false`
- `SEEDANCE_API_KEY=`
- `SEEDANCE_BASE_URL=`
- `SEEDANCE_MODEL=seedance-2.0`
- `SEEDANCE_TIMEOUT_SECONDS=180`
- `SEEDANCE_POLL_INTERVAL_SECONDS=3`

### Create

- `lwa-backend/app/services/seedance_service.py`

### Responsibilities

- validate env presence
- expose:
  - `seedance_available(settings)`
  - `submit_seedance_job(...)`
  - `poll_seedance_job(...)`
  - `download_seedance_asset(...)`
  - `generate_seedance_background(...)`
  - `enhance_clip_with_seedance(...)`
- isolate all external HTTP/provider specifics here only
- raise clear controlled errors if disabled/misconfigured
- never expose secrets to frontend
- never break `/generate`, `/process`, or existing background fallback

### Add schemas only as needed

- `SeedanceBackgroundRequest`
- `SeedanceJobResponse`
- `SeedanceJobStatusResponse`
- `SeedanceAssetResponse`

Support fields such as:

- `prompt`
- `style_preset`
- `motion_profile`
- `duration_seconds`
- `aspect_ratio`
- `seed`
- `reference_image_url` (optional)
- `source_clip_url` (optional)
- `source_asset_id` (optional)

### Add routes

- `POST /v1/seedance/background`
- `GET /v1/seedance/jobs/{job_id}`

### Behavior

- validate request body
- return clean disabled/misconfigured responses
- keep separate from current generation routes
- use existing storage/job patterns where practical

Register route safely in app startup.

Reuse current generated asset/storage patterns. Do not invent a second storage system unless necessary.

---

## Phase 5 — Homepage / background / visual premium layer

This must feel one-of-a-kind, alive, premium, mythic, and cinematic — but still controlled.

Search for:

- homepage shell
- `AIBackground` component
- hero/background rendering layer
- logo/brand heading system
- typography system
- `clip-studio` shell

### Implement a premium living mythic background system with

- layered silhouettes / mythic figures
- subtle character drift
- aura / eye glow flickers
- fog drift
- pulse lighting
- shimmer / scan energy
- cursor-reactive depth / parallax
- reduced-motion fallback
- mobile-safe lighter version
- no layout shift chaos
- no blocking render behavior

### Visual direction

- premium crimson / neon / void palette
- anime-influenced
- not toy cyberpunk
- not noisy
- not generic SaaS
- powerful but restrained

### Typography

Add a Japanese-inspired English display style:

- English only
- visually sharp / premium / title-card energy
- readable Latin letters
- use only for:
  - hero heading
  - section titles
  - premium labels
  - logo / wordmark-adjacent uses
- do not use for:
  - body copy
  - forms
  - dashboards
  - result details

### Interior product surfaces

- calmer
- cleaner
- more readable
- more operator-grade

### Landing surfaces

- more cinematic
- more animated
- more emotionally capturing

Do not let visuals overpower product clarity.

---

## Phase 6 — Premium enhancement + reactive experience

Add optional premium enhancement ideas where practical without destabilizing the app:

### 1. Viral reasoning transparency

- show why a clip was chosen
- expose high-end reasoning in an elegant way
- make LWA feel like a creative strategist, not just a generator

### 2. Immediate visible intelligence

- user should see useful output fast
- hooks/titles/strategy can appear before final video export finishes if possible

### 3. Optional low-res / early preview path

- if feasible, provide a quick preview or lightweight early artifact before full final render finishes
- do not block on this if it risks destabilizing current flows

### 4. Premium visual upgrade path

- optional only
- not the default path
- Seedance-backed only when truly available
- otherwise fall back cleanly

---

## Phase 7 — Docs, tests, and safety

Add/update:

- `docs/claude-seedance-integration.md`

Include:

- all new env vars
- provider routing behavior
- fallback behavior
- what is enabled by default
- what is live now
- what remains adapter-only pending exact Seedance contract confirmation
- how homepage/background enhancement works
- how to keep UI stable if Seedance is disabled

### Add tests/checks where reasonable

- provider selection logic
- Anthropic fallback behavior
- Seedance disabled behavior
- schema normalization
- malformed model response fallback
- startup/import safety
- homepage/background fallback behavior when premium mode is unavailable

---

## Product rules

- the app must show visible value in under 10 seconds
- the main workflow should fit in one screen
- advanced options must be secondary
- preview must be more important than decorative motion
- the UI should sell confidence, not complexity

---

## GUI rules

- big primary action
- fewer competing cards
- stronger hierarchy
- clear `working` / `preview ready` / `final ready` states
- first-time user experience should feel unlocked, not withheld

---

## Technical rules

- real preview path must be verified end-to-end
- asset URLs must resolve cleanly
- frontend must gracefully handle `preview pending` vs `preview ready`
- Seedance remains adapter-safe until contract is confirmed
- Claude improves intelligence without breaking current providers

---

## Work style requirements

- Make the smallest safe changes first
- Reuse current patterns before inventing new abstractions
- Keep changes localized
- Prefer new files over risky rewrites
- If a file must be edited, change only the minimum necessary sections
- Comment clearly where something is intentionally adapter-only pending vendor contract details
- Do not make unrelated cleanup edits

---

## Absolutely do not do these things

- do not rewrite the app architecture
- do not switch everything to Seedance
- do not remove OpenAI support
- do not delete fallback behavior
- do not rename stable API routes casually
- do not break homepage rendering
- do not break Railway deployment
- do not silently ship guessed Seedance endpoint logic as if it were confirmed
- do not make the UI more confusing
- do not hide the value behind too much gating for first-time understanding

---

## Required deliverable format

Return exactly:

1. Reality Check
2. Implementation Plan
3. File-by-File Changes
4. Exact Code Changes
5. Verification
6. Blockers
7. Env Vars I Must Set
8. PR Link
9. Confirmation Existing Flows Were Preserved
