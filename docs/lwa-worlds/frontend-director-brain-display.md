# Frontend Director Brain Display Notes

## Purpose

This note tracks the next frontend implementation slice after the Director Brain backend foundation.

## Implementation target

The web UI should display optional Director Brain fields without breaking older generation responses.

## Required behavior

- Preserve the current source input and generation flow.
- Do not touch backend code.
- Do not touch `lwa-ios`.
- Treat Director Brain fields as optional.
- Keep rendered clips, raw-only clips, and strategy-only clips visually honest.
- Never invent preview or download URLs.
- Never show strategy-only results as playable clips.

## Existing repo state

The current frontend already includes:

- `lwa-web/lib/types.ts` with many optional intelligence fields.
- `lwa-web/components/DirectorBrainPackagePanel.tsx` for optional intelligence display.
- `lwa-web/components/VideoCard.tsx` using `DirectorBrainPackagePanel`.
- `lwa-web/components/HeroClip.tsx` as the lead clip surface.
- `lwa-web/lib/clip-utils.ts` for media URL truth helpers.

## Next code changes

Recommended code-only slice:

1. Add a media-state helper in `lwa-web/lib/clip-utils.ts`:
   - `rendered`
   - `raw_only`
   - `strategy_only`

2. Update `VideoCard.tsx`:
   - show raw-only clips as playable proof, not polished renders
   - keep strategy-only cards non-playable
   - keep Director Brain package display visible when fields exist

3. Update `HeroClip.tsx`:
   - show Director Brain package display on the lead clip
   - show raw-only vs rendered status honestly
   - keep copy/package actions intact

## Verification

Run from `lwa-web`:

```bash
npm run type-check
npm run lint
npm run build
```

If any command is unavailable, report that clearly.

## Commit message

```text
feat: display director brain clip intelligence
```
