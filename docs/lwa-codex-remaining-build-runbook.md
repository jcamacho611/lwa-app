# LWA Codex Remaining Build Runbook

**Purpose:** preserve the exact backend/frontend checkpoint sequence for the next LWA build steps.

**Rule:** one narrow Codex task at a time. Do not build blockchain, NFTs, RPG, marketplace, direct social posting, full editor, or iOS rebuild in this sequence.

---

## Step 1 — Backend checkpoint

Paste this into Codex/backend after it finishes algorithm module work:

```text
PAUSE AND REPORT.

Do not continue editing.
Do not commit.

Report:
1. current branch
2. git status --short
3. exact files changed
4. whether any lwa-ios files were touched
5. whether any lwa-web files were touched
6. whether existing backend routes were changed
7. tests run
8. test results
9. any errors or skipped tests
10. recommended next backend step

Wait after reporting.
```

---

## Step 2 — Approve backend commit only if clean

Only approve if Codex confirms:

```text
lwa-ios untouched
lwa-web untouched
existing backend routes preserved
backend tests passed or failures are clearly unrelated
```

Then paste:

```text
Approved.

Commit the backend algorithm module scaffold only.

Use this commit message:

feat: scaffold LWA director brain support modules
```

---

## Step 3 — If Codex touched wrong files

If Codex touched `lwa-ios` or `lwa-web` during the backend task, paste:

```text
STOP.

Do not commit.

You touched files outside the backend task.

Revert all changes to:
- lwa-ios
- lwa-web

Preserve only backend algorithm module changes.

After reverting, report:
1. git status --short
2. files still changed
3. files reverted
4. whether backend routes are preserved
5. tests run
6. test results

Wait after reporting.
```

---

## Step 4 — Frontend display layer

After the backend commit is clean, move to Codex/frontend and paste:

```text
You are the LWA frontend implementation engineer.

Task:
Update the web frontend so it can display Director Brain output cleanly without breaking the existing generation flow.

Files likely involved:
- lwa-web/components/clip-studio.tsx
- lwa-web/components/HeroClip.tsx
- lwa-web/components/VideoCard.tsx
- lwa-web/lib/types.ts
- lwa-web/lib/api.ts only if necessary

Frontend requirements:
1. Preserve the current source input and generation flow.
2. Preserve existing backend API compatibility.
3. Add support for optional Director Brain fields:
   - algorithm_version
   - recommended_platform
   - recommended_content_type
   - recommended_output_style
   - platform_recommendation_reason
   - render_status
   - strategy_only
   - reason_not_rendered
   - post_rank
   - hook_variants
   - caption_style
   - thumbnail_text
   - cta_suggestion
   - why_this_matters
   - quality_gate_status
   - revenue_intent_score
   - offer_fit_score
4. Clearly separate:
   - rendered clips
   - raw-only clips
   - strategy-only clips
5. Never show strategy-only results as playable clips.
6. Never invent preview/download URLs.
7. Show the best clip first.
8. Show post order.
9. Show why the clip matters.
10. Show copy buttons for hooks, captions, CTA, and package.
11. Keep the app premium, dark, creator-native, and simple.
12. Do not touch backend.
13. Do not touch lwa-ios.
14. Do not build fake direct posting.
15. Do not build a full editor.

Before editing, report:
- git status --short
- exact files you plan to touch
- confirmation that backend/iOS will not be edited

Verification:
- npm run lint if available
- npm run typecheck if available
- npm run build if available

Expected output:
1. files changed
2. fields supported
3. UI behavior added
4. verification results
5. commit message
```

---

## Step 5 — If frontend asks where to start

Paste:

```text
Start with types.ts and VideoCard.tsx first.

Add safe optional types for Director Brain fields, then update VideoCard so rendered, raw-only, and strategy-only clips display differently.

Do not touch backend.
Do not touch iOS.
Do not alter the generation endpoint.
```

---

## Step 6 — Frontend checkpoint

After frontend finishes, paste:

```text
PAUSE AND REPORT.

Do not commit yet.

Report:
1. current branch
2. git status --short
3. exact files changed
4. whether any backend files were touched
5. whether any lwa-ios files were touched
6. whether existing generation flow was preserved
7. lint/typecheck/build commands run
8. results of each command
9. screenshots or description of UI behavior if available
10. recommended next frontend step

Wait after reporting.
```

---

## Step 7 — If frontend report is clean, approve commit

Only approve if:

```text
backend untouched
lwa-ios untouched
generation flow preserved
types added safely
strategy-only clips are not shown as playable
build/lint/typecheck passed or failures are clearly unrelated
```

Then paste:

```text
Approved.

Commit the frontend Director Brain display layer only.

Use this commit message:

feat: display director brain clip intelligence
```

---

## Step 8 — Caption style + quality gate backend

After backend and frontend are both committed, paste into Codex/backend:

```text
You are the LWA AI/media pipeline engineer.

Task:
Integrate caption style recommendations and quality gate results into the clip generation output without breaking existing generation.

Goals:
1. Add caption style recommendations to each clip.
2. Add quality gate status to each rendered or raw clip.
3. Keep strategy-only results honest.
4. Never mark failed renders as ready.
5. Preserve existing routes and response compatibility.

Fields to support:
- caption_style
- caption_style_reason
- emphasis_words
- suggested_caption_position
- quality_gate_status
- quality_gate_warnings
- render_readiness_score

Quality gate should check:
- playable asset exists
- audio likely exists
- timestamps are valid
- duration is reasonable
- clip is not marked rendered without URL
- strategy-only clips do not pretend to be downloadable

Constraints:
- Do not touch frontend.
- Do not touch lwa-ios.
- Do not change route names.
- Add optional fields only.
- Keep fallback deterministic.

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant backend tests

Expected output:
1. files changed
2. quality gate behavior
3. caption style behavior
4. tests added/updated
5. verification results
6. commit message
```

---

## Step 9 — Campaign Mode backend scaffold

After Step 8 is clean, paste into Codex/backend:

```text
You are the LWA product/backend architect.

Task:
Scaffold Campaign Mode for LWA.

Campaign Mode turns one source into a structured posting campaign, not just a list of clips.

Add optional campaign fields to the clip generation response.

Campaign output types:
1. lead_clip
2. trust_clip
3. sales_clip
4. educational_clip
5. controversy_clip
6. retargeting_clip
7. community_clip

Each clip may include:
- campaign_role
- campaign_reason
- funnel_stage
- suggested_post_order
- suggested_platform
- suggested_caption_style
- suggested_cta

Rules:
- Preserve existing generation route compatibility.
- Do not require account system yet.
- Do not require social posting yet.
- Do not claim campaign manager is fully built.
- Do not touch frontend.
- Do not touch lwa-ios.
- Add optional fields only.
- Keep outputs JSON-safe.

Verification:
- git status --short
- python -m py_compile on changed backend files
- pytest relevant backend tests

Expected output:
1. files changed
2. campaign fields added
3. tests added
4. verification results
5. commit message
```

Clean commit message:

```text
feat: scaffold campaign mode clip roles
```

---

## Step 10 — Campaign Mode frontend display

After Campaign Mode backend is clean, paste into Codex/frontend:

```text
You are the LWA frontend implementation engineer.

Task:
Display Campaign Mode fields in the web frontend without breaking the existing generation flow.

Files likely involved:
- lwa-web/components/clip-studio.tsx
- lwa-web/components/HeroClip.tsx
- lwa-web/components/VideoCard.tsx
- lwa-web/lib/types.ts

Display optional fields:
- campaign_role
- campaign_reason
- funnel_stage
- suggested_post_order
- suggested_platform
- suggested_caption_style
- suggested_cta

UI requirements:
1. Show campaign role badges.
2. Show suggested post order.
3. Show sales/trust/education/lead labels clearly.
4. Keep rendered clips first.
5. Keep strategy-only clips separate.
6. Do not fake direct posting.
7. Do not build a full campaign manager yet.
8. Do not touch backend.
9. Do not touch lwa-ios.

Verification:
- npm run lint if available
- npm run typecheck if available
- npm run build if available

Expected output:
1. files changed
2. campaign fields displayed
3. verification results
4. commit message
```

Clean commit message:

```text
feat: display campaign mode clip roles
```

---

## Step 11 — Whop / paid access audit

Do this after the clipping experience is better, not before.

Paste into Codex:

```text
You are the LWA monetization integration engineer.

Task:
Audit the existing Whop / entitlement / plan / credits flow.

Goal:
Determine what is already implemented, what is missing, and what exact minimal changes are needed before selling access through Whop.

Check:
1. frontend billing/plan display
2. backend entitlement checks
3. environment variables
4. checkout URL usage
5. webhook readiness
6. credit/plan enforcement
7. free launch mode behavior
8. guest user fallback behavior

Rules:
- Audit first.
- Do not edit files yet.
- Do not redesign monetization.
- Do not remove FREE_LAUNCH_MODE.
- Do not touch iOS.
- Do not fake completed Whop integration.

Return:
1. what exists now
2. what is missing
3. risks
4. exact files likely involved
5. smallest safe implementation plan
6. verification checklist
```

---

## Step 12 — Final launch hardening

Paste into Codex after Whop audit:

```text
You are the LWA launch hardening engineer.

Task:
Prepare the app for public free launch without breaking current generation.

Must include:
1. FREE_LAUNCH_MODE safety
2. guest user fallback
3. abuse-prevention IP rate limit
4. deterministic fallback clip result
5. no frontend 500 crashes
6. clean error messages
7. README launch instructions
8. Railway env var checklist

Rules:
- Preserve existing routes.
- Preserve working generation flow.
- Do not touch iOS unless explicitly required.
- Do not add heavy new systems.
- Do not block public demo usage with incomplete paywall logic.
- Fallback must be honest and never invent rendered clips.

Verification:
- backend py_compile
- backend pytest
- frontend lint/typecheck/build if frontend touched
- one manual generation test
- one failure/fallback test

Expected output:
1. files changed
2. launch hardening added
3. fallback behavior
4. env vars needed
5. verification results
6. commit message
```

Clean commit message:

```text
chore: harden public launch flow
```

---

## Final order

```text
1. Backend Director Brain modules
2. Backend checkpoint
3. Backend commit
4. Frontend Director Brain display
5. Frontend checkpoint
6. Frontend commit
7. Caption style + quality gate backend
8. Campaign Mode backend
9. Campaign Mode frontend display
10. Whop/entitlement audit
11. Public launch hardening
12. Railway verification
13. Sales/demo push
```

## Do not build yet

```text
- blockchain
- NFTs
- RPG layer
- marketplace
- direct social posting
- full editor
- upload-from-every-source
- mobile/iOS rebuild
```

Fastest money path:

```text
Better clips → better proof → better frontend → Whop/pay access → sales/demo push
```
