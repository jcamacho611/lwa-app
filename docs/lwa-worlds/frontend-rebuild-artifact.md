# LWA Frontend Rebuild Artifact

## Purpose

This artifact defines the premium web experience for LWA / IWA.

The frontend must feel like a creator command center, not a generic SaaS dashboard.

## Current principle

Preserve the working backend, route spine, generation flow, and source contract.

Do not touch `lwa-ios`.

## Experience goal

One source should become a clean ranked workspace:

1. source input
2. generation state
3. best clip first
4. rendered clips lane
5. raw-only clips lane
6. strategy-only clips lane
7. Director Brain explanation
8. campaign role / post order
9. copy/export actions
10. upgrade/demo/Whop CTA

## Required UI behavior

### Source input

- allow public URL where supported
- allow upload where supported
- explain public URLs as best-effort
- do not claim every platform URL works

### Results

- show best clip first
- show score and post order
- show rendered clips only when a playable/export URL exists
- show strategy-only packages separately
- never invent preview URLs
- never show failed render as ready

### Director Brain display

Optional fields the UI should tolerate:

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
- campaign_role
- campaign_reason
- funnel_stage
- suggested_post_order

## Component responsibilities

### `clip-studio.tsx`

Owns:

- source input
- generation request
- loading state
- result grouping
- CTA panels

### `HeroClip.tsx`

Owns:

- lead/best clip presentation
- strongest hook
- rendered proof if available
- top Director Brain rationale

### `VideoCard.tsx`

Owns:

- individual clip display
- rendered/raw/strategy-only distinction
- copy buttons
- score/rank/quality/campaign badges

### `DirectorBrainPackagePanel.tsx`

Owns:

- optional intelligence fields
- quality warnings
- offer/revenue scores
- campaign role
- platform reason

## Design direction

- dark premium shell
- neon/cyan/purple accents
- controlled crimson/gold highlights
- glass panels
- strong spacing
- minimal copy
- creator-native language

Avoid:

- corporate gray SaaS feel
- childish game UI
- cluttered explanation blocks
- fake editor controls

## Copy rules

Use:

- clips worth posting
- hooks that hit
- ranked outputs
- source to post faster
- strategy-only package
- rendered ready

Avoid:

- guaranteed viral
- guaranteed income
- passive income
- every link works
- verified payment unless webhook-backed

## Frontend Codex prompt

```text
You are the LWA frontend implementation engineer.

Task:
Polish the LWA web frontend into a premium clipping command center.

Rules:
- Preserve existing generation flow.
- Do not touch backend unless a type contract requires it.
- Do not touch lwa-ios.
- Do not invent playable URLs.
- Do not show strategy-only results as playable.
- Add optional Director Brain fields safely.
- Keep rendered clips, raw-only clips, and strategy-only clips visually distinct.

Likely files:
- lwa-web/components/clip-studio.tsx
- lwa-web/components/HeroClip.tsx
- lwa-web/components/VideoCard.tsx
- lwa-web/lib/types.ts

Verification:
- cd lwa-web && npm run type-check
- cd lwa-web && npm run build if stable

Expected output:
- files changed
- UI behavior added
- fields supported
- verification results
```

## Definition of done

- generated results still render
- older backend responses still work
- Director Brain fields show only when present
- strategy-only lane is honest
- Whop CTA remains available
- no iOS changes
