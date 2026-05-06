# Lee-Wuh Character Blender Production Spec

## Overview
Create a lightweight 3D character model of Lee-Wuh for web use (GLB export).

## Character Design

### Style
- **Chibi proportions** (big head, small body ~1:2 ratio)
- **Afro-Futurist meets Japanese anime** final-boss energy
- **Cute but powerful** - approachable yet commanding presence

### Key Features
1. **Dreadlock hairstyle** with gold/thread accents
2. **Jewelry** - rings, necklace, earrings (gold/purple)
3. **Hoodie/Streetwear** - modern urban fashion
4. **Aura rings** - floating energy rings around character
5. **Furry chibi form** - anthropomorphic lion features

### Color Palette
- **Primary Gold**: #C9A24A (accents, jewelry, highlights)
- **Accent Purple**: #6D3BFF (energy, magic effects)
- **Base Black**: #0A0A0F (clothing, background)
- **Charcoal**: #1A1A24 (secondary surfaces)
- **Text White**: #F5F1E8 (eyes, bright details)

## Technical Requirements

### Polygon Budget
- **Target**: < 10,000 triangles for web performance
- **Style**: Low-poly with smooth shading
- **Focus**: Silhouette readability over detail

### Model Structure
```
lee-wuh-mascot.blend
├── Root
│   ├── Body (chibi proportions)
│   │   ├── Torso
│   │   ├── Head (larger scale 1.5x)
│   │   ├── Arms
│   │   └── Legs
│   ├── Dreadlocks (hair system)
│   ├── Clothing
│   │   ├── Hoodie
│   │   └── Accessories
│   ├── Jewelry
│   │   ├── Necklace
│   │   ├── Rings
│   │   └── Earrings
│   └── Aura_Rings (floating elements)
└── Lighting_Setup
```

### Required States (for Rive/Web)
1. **Idle** - Breathing loop, subtle aura pulse
2. **Analyzing** - Head tilt, processing "thinking" pose
3. **Rendering** - Active energy aura, working motion
4. **Complete** - Victory pose, celebration
5. **Victory** - Max energy, triumphant stance
6. **Error** - Confused/sad pose, drooping ears
7. **Helping** - Presenting gesture, welcoming

## Export Settings

### GLB Export (Web)
- **Format**: glTF 2.0 (GLB binary)
- **Draco compression**: Enabled
- **Max file size**: < 2MB
- **Textures**: 1024x1024 max, PNG/WebP
- **Materials**: PBR metallic-roughness

### Animation
- **Rig**: Simple FK/IK hybrid (no complex deformers)
- **Bones**: ~40 max for web performance
- **Animations**: 7 state loops, 2-4 seconds each
- **Export**: Separate .gltf + .bin or embedded GLB

## File Naming
```
/brand/lee-wuh/
├── blender/lee-wuh-character-blockout.blend # Master Blender file
├── 3d/lee-wuh-mascot.glb         # Web export
├── lee-wuh-mascot-idle.glb       # Idle animation only
├── lee-wuh-mascot-rigged.fbx     # For other engines
├── textures/
│   ├── lee-wuh-diffuse.png
│   ├── lee-wuh-normal.png
│   └── lee-wuh-metallic.png
└── animations/
    ├── idle.glb
    ├── analyzing.glb
    ├── rendering.glb
    ├── complete.glb
    ├── victory.glb
    ├── error.glb
    └── helping.glb
```

## Implementation Priority

### Phase 1: Blockout
- [ ] Base chibi mesh (head, body, limbs)
- [ ] Dreadlock hair style
- [ ] Basic hoodie/clothing

### Phase 2: Details
- [ ] Jewelry (necklace, rings)
- [ ] Aura rings (floating elements)
- [ ] Face details (eyes, expression capability)

### Phase 3: Rig & Animate
- [ ] Simple bone rig
- [ ] 7 state animations
- [ ] Weight painting

### Phase 4: Export
- [ ] Texture baking
- [ ] GLB export with Draco
- [ ] Web performance test
- [ ] Rive integration prep

## Notes
- Keep topology clean for subdivision if needed
- Use mirror modifier for symmetry, apply before export
- Test in browser with three.js or model-viewer
- Rive version will use simplified vector shapes
