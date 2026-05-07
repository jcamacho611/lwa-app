# LWA Fantasy Sword Asset — No Aura

## Purpose

This asset is the separated fantasy sword layer for Lee-Wuh. It is intended to be loaded independently so the frontend/game layer can attach, animate, hide, or swap the sword without baking it into the background.

## What it contains

- Isolated sword
- Gold/black/purple fantasy material direction
- No aura
- Transparent render setup in the Blender generator script

## Repo placement

```text
brand-source/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb
lwa-web/public/brand/lee-wuh/models/weapons/lwa_fantasy_sword_no_aura.glb
scripts/blender/create_lwa_fantasy_sword_no_aura_blend.py
```

## Usage rule

Do not merge this asset into the background. Keep it separate so Lee-Wuh can hold, drop, summon, resize, or animate the sword in the frontend/game layer.
