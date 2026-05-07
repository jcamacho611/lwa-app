# Lee-Wuh Asset Map

This package places the Lee-Wuh visual source files into the LWA repo without touching backend, iOS, API contracts, or build config.

## Runtime assets for the Next.js app

Use these paths in frontend code with plain public URLs:

| Purpose | Public URL |
|---|---|
| World/background layer | `/brand/lee-wuh/backgrounds/lee-wuh-empty-world-background.png` |
| Lee-Wuh transparent character with sword + aura | `/brand/lee-wuh/characters/lee-wuh-transparent-with-sword-aura.png` |
| Lee-Wuh transparent character with aura/no sword | `/brand/lee-wuh/characters/lee-wuh-transparent-aura.png` |
| Lee-Wuh transparent clean character/no aura | `/brand/lee-wuh/characters/lee-wuh-transparent-clean.png` |
| Transparent sword asset | `/brand/lee-wuh/weapons/lee-wuh-sword-transparent-aura.png` |
| Mobile UI composition reference | `/brand/lee-wuh/ui/lee-wuh-mobile-ui-reference.png` |
| Master character/world reference | `/brand/lee-wuh/references/lee-wuh-master-character-world.png` |

## Source/reference assets

These are the original creative source placements Codex should treat as references, not as final UI code:

| Purpose | Repo path |
|---|---|
| World/background layer | `brand-source/lee-wuh/references/lee-wuh-empty-world-background.png` |
| Master Lee-Wuh character/world reference | `brand-source/lee-wuh/references/lee-wuh-master-character-world.png` |
| Mobile UI composition reference | `brand-source/lee-wuh/references/lee-wuh-mobile-ui-reference.png` |
| Transparent Lee-Wuh with sword + aura | `brand-source/lee-wuh/cutouts/lee-wuh-transparent-with-sword-aura.png` |
| Transparent Lee-Wuh with aura/no sword | `brand-source/lee-wuh/cutouts/lee-wuh-transparent-aura.png` |
| Transparent clean Lee-Wuh/no aura | `brand-source/lee-wuh/cutouts/lee-wuh-transparent-clean.png` |
| Transparent sword asset | `brand-source/lee-wuh/cutouts/lee-wuh-sword-transparent-aura.png` |

## Codex usage rules

1. **Use the background/world layer as the scene**, not the UI itself.
2. **Use transparent Lee-Wuh PNGs as overlay/hero layers**, so Lee-Wuh can float, scale, pulse, and react independently.
3. **Use the sword PNG as a separate effect/weapon layer** when possible.
4. **Use the mobile UI composition as layout inspiration only**; do not bake the UI into the background.
5. **Keep all work additive.** Do not delete the existing clipping engine, backend, iOS folder, or API contracts.
6. **Preserve performance.** Use Next/Image where appropriate, lazy load non-critical references, and keep the landing scene responsive.
7. **Do not commit secrets or generated build folders.**

## First frontend integration target

Add a safe Lee-Wuh hero/world component that layers:

```text
background image
→ atmospheric overlays/glow
→ Lee-Wuh transparent PNG
→ UI cards/buttons/input
→ bottom navigation/command surfaces
```

Suggested component path:

```text
lwa-web/components/lee-wuh/LeeWuhWorldHero.tsx
```
