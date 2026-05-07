# LWA Lee-Wuh 3D Asset Index

## Separated layers

| Layer | Source path | Frontend path | Rule |
|---|---|---|---|
| World background | `brand-source/lee-wuh/separated-assets/lee-wuh-world-background.glb` | `/brand/lee-wuh/backgrounds/lee-wuh-world-background.glb` | Environment only; no character; no sword |
| Sword | `brand-source/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb` | `/brand/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb` | Sword only; no aura; separate from character/background |

## Build direction

The app should treat Lee-Wuh as layered:

```text
Background/world layer
→ Lee-Wuh character layer
→ Sword/weapon layer
→ UI layer
→ AI/game interaction layer
```

This keeps the experience flexible for animation, depth, future GLB rigging, and game-style interactions.
