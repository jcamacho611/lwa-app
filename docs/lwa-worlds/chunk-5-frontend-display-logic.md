# LWA CHUNK 5 — FRONTEND TYPES AND DISPLAY LOGIC

This chunk defines how the frontend should display Director Brain, campaign, and render state fields safely.

## Truth rule

The frontend must support future fields without pretending unfinished systems are live.

```text
Rendered = playable media exists.
Raw-only = raw media exists.
Strategy-only = no playable media, but timestamps and packaging are useful.
Failed = do not present as a normal clip.
```

## Optional TypeScript fields

```ts
export type ClipRenderStatus = 'rendered' | 'raw_only' | 'strategy_only' | 'failed';

export type DirectorBrainClipFields = {
  algorithm_version?: string | null;
  render_status?: ClipRenderStatus | null;
  strategy_only?: boolean | null;
  reason_not_rendered?: string | null;
  post_rank?: number | null;
  hook_variants?: string[] | null;
  caption_style?: string | null;
  thumbnail_text?: string | null;
  cta_suggestion?: string | null;
  why_this_matters?: string | null;
  quality_gate_status?: 'pass' | 'warning' | 'fail' | 'strategy_only' | null;
  render_readiness_score?: number | null;
  revenue_intent_score?: number | null;
  offer_fit_score?: number | null;
  campaign_role?: string | null;
  campaign_reason?: string | null;
  funnel_stage?: string | null;
  suggested_post_order?: number | null;
  suggested_platform?: string | null;
  suggested_caption_style?: string | null;
  suggested_cta?: string | null;
};
```

## Media-state helpers

```ts
export function getPlayableUrl(clip: ClipResult): string | null {
  return clip.preview_url || clip.edited_clip_url || clip.clip_url || null;
}

export function getRawUrl(clip: ClipResult): string | null {
  return clip.raw_clip_url || null;
}

export function classifyClipMediaState(clip: ClipResult) {
  const playable = getPlayableUrl(clip);
  const raw = getRawUrl(clip);

  if (clip.render_status === 'rendered' && playable) return 'rendered';
  if (clip.render_status === 'raw_only' && raw) return 'raw_only';
  if (clip.strategy_only || clip.render_status === 'strategy_only') return 'strategy_only';
  if (playable) return 'rendered';
  if (raw) return 'raw_only';
  return 'strategy_only';
}
```

## Lead clip selection

```ts
export function chooseLeadClip(clips: ClipResult[]): ClipResult | null {
  if (!clips.length) return null;

  const rendered = clips.find((clip) => classifyClipMediaState(clip) === 'rendered');
  if (rendered) return rendered;

  const raw = clips.find((clip) => classifyClipMediaState(clip) === 'raw_only');
  if (raw) return raw;

  return [...clips].sort((a, b) => (b.score || 0) - (a.score || 0))[0];
}
```

## Display lanes

```text
Lead result:
- best rendered clip first
- if no rendered clip exists, best raw-only clip
- if no raw clip exists, best strategy-only clip

Rendered lane:
- only clips with playable preview/export URLs

Raw-only lane:
- clips with raw assets but no edited preview

Strategy-only lane:
- clips with packaging but no real media
```

## Component requirements

### DirectorBrainPackagePanel

Show:
- post rank
- recommended platform
- why this matters
- hook variants
- caption style
- thumbnail text
- CTA
- quality gate status
- revenue/offer score only if present

### VideoCard

Show:
- visual state badge
- video player only when playable URL exists
- raw-only action if raw URL exists
- strategy-only panel if no media exists

### HeroClip

Show:
- best clip first
- same DirectorBrainPackagePanel as VideoCard
- export/copy actions only when data exists

## Badge language

```text
rendered: Ready now
raw_only: Raw cut available
strategy_only: Strategy only
failed: Not ready
```

## Copy buttons

Each card should support:
- copy hook
- copy caption
- copy CTA
- copy full package

## Frontend Codex prompt

```text
Implement Chunk 5 only.

Task:
Update frontend types and display helpers so Director Brain, campaign, quality, and render state fields display safely.

Files likely involved:
- lwa-web/lib/types.ts
- lwa-web/lib/clip-utils.ts
- lwa-web/components/VideoCard.tsx
- lwa-web/components/HeroClip.tsx
- lwa-web/components/DirectorBrainPackagePanel.tsx

Rules:
- Touch lwa-web only.
- Do not touch backend.
- Do not touch lwa-ios.
- Preserve existing generation flow.
- Never show strategy-only clips as playable.
- Never invent preview/download URLs.

Verification:
- cd lwa-web
- npm run type-check if available
- npm run lint if available
- npm run build if available
```
