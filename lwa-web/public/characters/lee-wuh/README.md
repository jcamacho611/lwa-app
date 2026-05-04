# Lee-Wuh Character Assets

This folder is the runtime character asset home for Lee-Wuh.

## Preferred runtime files

```text
lee-wuh.glb
lee-wuh.poster.png
```

## Rules

* Commit only optimized runtime assets.
* Do not commit heavy `.blend`, `.fbx`, `.obj`, `.zip`, or raw source files.
* Keep `.blend` source files outside the repo or in external asset storage.
* Use `scripts/blender/create_lee_wuh_character.py` for procedural blockout/testing.
* Use `scripts/blender/export_lee_wuh_glb.py` for exporting from final Blender files.

## Frontend runtime path

```text
/characters/lee-wuh/lee-wuh.glb
/characters/lee-wuh/lee-wuh.poster.png
```

If the GLB is missing, the app falls back to poster/SVG instead of emoji-first UI.

## Current status

- [ ] `lee-wuh.glb` - 3D character model (not yet added)
- [x] `lee-wuh.poster.png` - Fallback poster image (using `/brand/lee-wuh/lee-wuh-hero-16x9.png`)
