# Lee-Wuh Blender 3D Pipeline v0

## Overview

This document defines the Blender pipeline for Lee-Wuh 3D model, rigging, animations, and web-ready exports.

## Model Parts

Lee-Wuh 3D model consists of the following parts:

- **Head/face**: Main facial structure with expressive features
- **Jeweled dreads**: Signature dreadlocks with jewel accents
- **Eyes**: Expressive eyes with pupil and iris
- **Coat**: Long coat with flowing fabric simulation
- **Sword**: Energy sword with glow effects
- **Sigils**: Mystical symbols on coat and accessories
- **Shoes**: Footwear with detailed design
- **Tail**: Animated tail for expression
- **Body**: Full body rig for posing and animation

## Rig States

Lee-Wuh requires the following rig states:

- **Idle**: Neutral standing pose
- **Thinking**: Head tilt, hand on chin
- **Success**: Arms raised, celebratory pose
- **Warning**: Leaning forward, concerned expression
- **Error**: Slumped shoulders, disappointed pose
- **Rendering**: Active working pose
- **Analyzing**: Focused concentration pose
- **Excited**: Energetic, bouncing pose
- **Overlord**: Commanding, authoritative pose

## Animation States

Required animations:

- **Idle blink**: Subtle eye blinking (2-3 second cycle)
- **Aura pulse**: Energy aura pulsing effect
- **Thinking**: Head movement and hand gestures
- **Success**: Victory animation with celebration
- **Warning**: Alert state animation
- **Error**: Failure/retry animation
- **Rendering**: Active processing animation
- **Overlord mode**: Powerful transformation animation

## GLB Export Standards

### File Size Limits

- **Target**: Under 5MB for web-ready GLB
- **Maximum**: 10MB absolute limit
- **Hero scenes**: Lazy-load only, under 8MB

### Export Settings

- **Format**: GLB (binary glTF)
- **Scale**: Meters (0.01 = 1cm)
- **Up axis**: Y-up
- **Forward axis**: -Z forward
- **Compression**: Draco compression enabled
- **Texture compression**: KTX2 or WebP

### Material Requirements

- **PBR workflow**: Metallic/Roughness workflow
- **Texture resolution**: 1024x1024 max for web
- **Normal maps**: Optional but recommended for detail
- **Emissive materials**: For glow effects (sword, sigils)

## Texture Optimization

### Guidelines

- **Max texture size**: 2048x2048 for hero assets
- **Standard texture size**: 1024x1024 for web
- **Texture format**: PNG or JPEG for web
- **Compression**: Use texture atlases where possible
- **Mipmaps**: Generate for web performance

### Storage Rules

- **Do not commit** heavy .blend files to repo
- **Do not commit** large texture folders
- **Do not commit** raw GLB files over 5MB
- **Store heavy source files** externally or in asset storage
- **Commit docs and tiny placeholders only**
- **Use .placeholder text files** for missing assets

## Web Performance Budgets

### Load Time Targets

- **Initial load**: Under 2 seconds for mascot
- **Animation load**: Under 1 second per state
- **Memory usage**: Under 50MB for 3D assets

### Optimization Strategies

- **Lazy loading**: Load 3D assets only when needed
- **LOD levels**: Use Level of Detail for distance
- **Instancing**: Reuse geometry where possible
- **Static batching**: Batch static meshes
- **GPU skinning**: Enable for performance

## Future Integration Components

### Frontend Integration

- **React Three Fiber**: For React-based 3D rendering
- **@react-three/drei**: Helper components
- **@react-three/fiber**: Canvas and scene setup
- **useGLTF**: For loading GLB models
- **useAnimations**: For playing Blender animations

### Fallback Strategies

- **Static PNG**: Fallback image for when 3D fails
- **2D Rive**: Fallback to 2D animation
- **CSS animation**: Simple CSS fallback
- **Loading states**: Show loading during 3D asset load

## Animation Export

### Naming Convention

- Use descriptive names: `idle_01`, `thinking_01`, `success_01`
- Number variations for variety
- Include state in filename

### Export Settings

- **Frame rate**: 30 FPS for web
- **Bake animation**: Bake all modifiers and constraints
- **Action export**: Export each action separately
- **NLA strips**: Use Non-Linear Animation for organization

## Quality Control

### Checklist

- [ ] Model under 5MB GLB
- [ ] All animations play correctly
- [ ] Materials render correctly in web
- [ ] No texture seams visible
- [ ] Rig deformation smooth
- [ ] Normal maps facing correct direction
- [ ] Emissive materials glow appropriately
- [ ] Scale matches reference (0.01 = 1cm)

### Testing

- Test in Three.js viewer
- Test in target browser (Chrome, Safari, Firefox)
- Test on mobile devices
- Test with different GPU capabilities
- Test loading performance

## External Asset Storage

### Recommended Storage

- **AWS S3**: For production asset storage
- **Cloudflare R2**: For CDN delivery
- **GitHub Releases**: For versioned assets
- **Asset CDN**: For global distribution

### Versioning

- Use semantic versioning for assets
- Tag releases with model version
- Maintain changelog for updates
- Keep backup of previous versions

## Production Pipeline

### Workflow

1. **Model creation** in Blender
2. **Rigging** and weight painting
3. **Animation** creation
4. **Material** setup and texturing
5. **Export** to GLB with compression
6. **Optimize** for web (Draco, texture compression)
7. **Test** in web environment
8. **Upload** to external storage
9. **Update** frontend references
10. **Deploy** to production

### Automation

- Use Blender Python API for batch exports
- Automate texture compression
- Automate GLB optimization
- Set up CI/CD for asset pipeline

## Troubleshooting

### Common Issues

- **GLB too large**: Reduce texture resolution, enable Draco compression
- **Materials not loading**: Check texture paths, use embedded textures
- **Animation not playing**: Check action names, bake animations
- **Model not visible**: Check scale, position, camera
- **Performance issues**: Reduce polygon count, enable LOD

### Debug Tools

- **Three.js Inspector**: For debugging 3D scenes
- **glTF Validator**: For validating GLB files
- **Blender Console**: For export errors
- **Browser DevTools**: For loading issues

## Next Steps

- [ ] Create Lee-Wuh base model
- [ ] Set up rig and weight painting
- [ ] Create required animation states
- [ ] Export and optimize GLB
- [ ] Test in web environment
- [ ] Set up external storage
- [ ] Integrate with frontend
- [ ] Add fallback strategies
