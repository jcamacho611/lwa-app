# Lee-Wuh Character Pipeline

## Goal

Lee-Wuh must be a real character system, not an emoji-only mascot.

## Visual Target

Lee-Wuh is a **chibi black cat/lion creator deity** with:

- Purple glowing eyes
- Black and gold armor/robe/creator coat
- Dreadlock-like hair tubes with gold cuffs
- Purple realm energy aura
- Ornate oversized creator sword
- Original luxury streetwear sneakers (no trademark logos)
- Japanese/African/American cultural fusion motifs
- Creator overlord / final boss / last creator energy

The runtime priority is:

```text
1. GLB/GLTF 3D character (Three.js)
2. Poster image fallback
3. Brand SVG fallback
4. Emoji only as last-resort fallback
```

## Runtime component

```text
lwa-web/components/lee-wuh/LeeWuhCharacterStage.tsx
```

## Runtime asset paths

```text
lwa-web/public/characters/lee-wuh/lee-wuh.glb
lwa-web/public/characters/lee-wuh/lee-wuh.poster.png
```

## Current Implementation

### Three.js Renderer

Uses `three` with `GLTFLoader` for GLB models:
- Gold rim lighting (`#f5d88a`)
- Purple accent lighting (`#6d3bff`)
- Ambient fill
- Auto-rotation animation
- Drift bobbing animation

### Fallback Chain

1. Try to load GLB → if success, render 3D
2. If GLB fails → show poster PNG
3. If poster fails → show SVG (`/brand/lee-wuh-hero-16x9.svg`)
4. If all fail → emoji fallback

## Mood States

| Mood | Animation | Message |
|------|-----------|---------|
| idle | Slow rotation | Ready to run the signal |
| focused | Medium rotation | Locked onto best clip path |
| analyzing | Fast rotation | Scanning hooks, beats, captions |
| confident | Medium rotation + pulse | Found creator signal |
| victory | Slow rotation + glow | Packaged the win |
| warning | Static + pulse | Needs real asset or safer source |

## Placement Variants

| Variant | Size | Use Case |
|---------|------|----------|
| hero | 460px height | Homepage hero section |
| card | 320px height | Feature cards, results panels |
| compact | 220px height | Sidebars, inline placements |
| floating | 80px circle | Assistant button, avatars |

## Blender Export

### Prerequisites

- Blender 3.6+ or 4.0+
- Lee-Wuh source `.blend` file

### Export Script

Run:

```bash
blender --background /path/to/lee-wuh.blend --python scripts/blender/export_lee_wuh.py
```

Or use the newer optimized script:

```bash
blender --background /path/to/lee-wuh.blend --python scripts/blender/export_lee_wuh_glb.py
```

### Output

```text
lwa-web/public/characters/lee-wuh/lee-wuh.glb
```

### Optimization Settings

- Format: GLB (binary GLTF)
- Draco compression: enabled, level 6
- Position quantization: 14 bits
- Normal quantization: 10 bits
- UV quantization: 12 bits
- No cameras, no lights
- Y-up orientation

## Repo Rules

Do not commit:

```text
.blend
.fbx
.obj
.zip
.psd
.mp4
.mov
.wav
.aiff
```

Commit only optimized runtime assets if size is acceptable (< 5MB preferred, < 10MB max).

## Integration Points

Lee-Wuh appears in:

```text
✅ Homepage (hero variant)
✅ Generate / clip-studio (card variant, dynamic mood)
✅ Command Center overview (card variant)
✅ Floating assistant (floating variant)
```

## Usage Examples

### Hero Section

```tsx
<LeeWuhCharacterStage
  mood="confident"
  variant="hero"
  title="Lee-Wuh"
  message="Meet the guardian of the creator engine."
/>
```

### Generate Page

```tsx
<LeeWuhCharacterStage
  mood={isLoading ? "analyzing" : result ? "victory" : "focused"}
  variant="card"
  title="Lee-Wuh is on the clip hunt"
/>
```

### Floating Assistant

```tsx
<LeeWuhCharacterStage
  mood={mood}
  variant="floating"
  showLabel={false}
/>
```

## Validation

```bash
cd lwa-web
npm run type-check
npm run build
cd ..
python3 -m py_compile scripts/blender/export_lee_wuh_glb.py
```

## Procedural Character Generation

For testing and development, generate a procedural Lee-Wuh:

```bash
blender --background --python scripts/blender/create_lee_wuh_character.py
```

This creates:
- `lee-wuh.glb` - Runtime GLB for web
- `lee-wuh.generated.blend` - Source scene (do not commit)

The procedural character includes:
- Chibi cat/lion head with ears
- Purple glowing eyes
- Dreadlock hair tubes with gold cuffs
- Black/gold coat with Japanese glyphs (夢, 創)
- Ornate creator sword with purple edge energy
- Original luxury sneakers (white/red/black, no logos)
- Purple realm energy aura rings
- Gold pedestal with inscription

## VR / AR Readiness

The GLB is designed for future XR compatibility:

- Real-world scale friendly (1 unit ≈ 1 meter)
- Y-up export for standard compliance
- No trademarked content
- Optimized materials (PBR-ready)
- Animation-ready armature structure
- Under 5MB runtime size target

Future targets:

```text
WebXR viewer integration
Quest/Oculus build path
ARKit/ARCore anchor support
Rive/Spine 2D expression overlays
Full animation state machine
```

## Next Steps

1. Generate procedural character: `blender --background --python scripts/blender/create_lee_wuh_character.py`
2. Or create artist-made model in Blender
3. Run export script to generate `lee-wuh.glb`
4. Place GLB in `lwa-web/public/characters/lee-wuh/`
5. Test fallback chain by temporarily renaming GLB
6. Commit optimized runtime assets only

## Dependencies

Already installed:

```text
three: ^0.184.0
@types/three: ^0.184.0
```

No new dependencies required.
