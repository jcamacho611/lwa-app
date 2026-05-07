# LWA Asset Registry Engine

The asset registry engine keeps Lee-Wuh's character, sword, background, aura, GLB, Blender, Spine, and UI references separated so the frontend can compose them safely.

It exists because a single visual system can quickly become brittle if every asset is treated as interchangeable. LWA needs to know which assets are runtime-safe, which are source-only, and which intentionally mix layers as references.

## Key Rules

- Character assets should be transparent and not bake in sword or aura unless explicitly labeled as a combined reference or aura variant.
- Sword assets should stay sword-only and not bake in the character body.
- Background assets should not include foreground character or sword layers.
- Runtime assets should be clearly separated from Blender source and future Spine source.

## Engine Surface

- canonical asset registry data
- approved/placeholder/deprecated status
- runtime safety classification
- layer truth validation
- asset lookup by id and kind

## Current Registry Types

- `character`
- `sword`
- `background`
- `aura`
- `combined_reference`
- `blender_source`
- `glb_runtime`
- `spine_source`
- `ui_reference`

## Future Backend Use

Later backend work can validate uploaded/generated asset metadata, preserve version history, and expose asset health to the frontend and iOS. That should stay additive and not break the current public asset surface.

