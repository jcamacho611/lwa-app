# Lee-Wuh Spline Web 3D Pipeline v0

## Overview

This document defines the Spline pipeline for web 3D scenes and lightweight Lee-Wuh 3D integration.

## Scene Types

### Hero Scene

- **Purpose**: Landing page hero animation
- **Content**: Floating Lee-Wuh with interactive elements
- **Duration**: Infinite loop with interactions
- **Performance**: Lightweight, under 2MB

### Throne Room

- **Purpose**: Lee-Wuh command center visualization
- **Content**: Lee-Wuh on throne with council elements
- **Duration**: Interactive scene
- **Performance**: Medium complexity, under 5MB

### Brand Portal

- **Purpose**: Brand showcase and navigation
- **Content**: 3D brand elements with Lee-Wuh
- **Duration**: Interactive navigation
- **Performance**: Lightweight, under 3MB

### 3D Preview

- **Purpose**: Quick 3D asset preview
- **Content**: Single 3D object preview
- **Duration**: Short interaction
- **Performance**: Very lightweight, under 1MB

## Integration Patterns

### React Integration

```typescript
import { SplineScene } from '@splinetool/react-spline';

function LeeWuh3D() {
  return (
    <SplineScene
      scene="https://prod.spline.design/your-scene-url"
      style={{ width: '100%', height: '100%' }}
    />
  );
}
```

### Loading Strategies

- **Lazy loading**: Load Spline scenes only when in viewport
- **Progressive loading**: Show placeholder while loading
- **Priority loading**: Load hero scene first
- **Background loading**: Load secondary scenes in background

## Performance Budgets

### File Size

- **Hero scene**: Under 2MB
- **Throne room**: Under 5MB
- **Brand portal**: Under 3MB
- **3D preview**: Under 1MB
- **Total assets**: Under 10MB for all Spline scenes

### Load Time Targets

- **Hero scene**: Under 3 seconds initial load
- **Interactive scenes**: Under 2 seconds
- **Preview scenes**: Under 1 second
- **Memory usage**: Under 100MB for Spline runtime

## Optimization Strategies

### Scene Optimization

- **Reduce polygon count**: Use simplified geometry
- **Optimize materials**: Use standard materials
- **Reduce textures**: Use procedural textures where possible
- **Limit lights**: Use minimal lighting setup
- **Optimize animations**: Use simple animations

### Loading Optimization

- **Use CDN**: Serve Spline scenes from CDN
- **Enable compression**: Use gzip/brotli
- **Cache aggressively**: Use long cache headers
- **Preload critical scenes**: Preload hero scene
- **Lazy load secondary**: Load other scenes on demand

## Fallback Strategies

### When Spline Fails

1. **Static image**: Show static 3D render
2. **2D animation**: Use Rive animation fallback
3. **CSS 3D**: Use CSS 3D transforms
4. **No 3D**: Show 2D alternative

### Progressive Enhancement

- Load 2D assets first
- Load Spline runtime asynchronously
- Swap to 3D when ready
- Graceful degradation if Spline fails

## Web 3D Integration Specs

### Three.js Alternative

For scenes requiring more control than Spline:

```typescript
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

function LeeWuh3D() {
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <LeeWuhModel />
      <OrbitControls />
    </Canvas>
  );
}
```

### GLB Loading

```typescript
import { useGLTF } from '@react-three/drei';

function LeeWuhModel() {
  const { scene } = useGLTF('/models/lee-wuh.glb');
  return <primitive object={scene} />;
}
```

## Scene Specifications

### Hero Scene

- **Camera**: Perspective camera, 75° FOV
- **Lighting**: Ambient + directional light
- **Objects**: Lee-Wuh model + floating elements
- **Animation**: Idle animation + hover effects
- **Interactions**: Mouse follow, click effects

### Throne Room

- **Camera**: Orbit controls, 60° FOV
- **Lighting**: 3-point lighting setup
- **Objects**: Lee-Wuh + throne + council elements
- **Animation**: Idle + state changes
- **Interactions**: Camera orbit, object selection

### Brand Portal

- **Camera**: Fixed camera, 90° FOV
- **Lighting**: Studio lighting
- **Objects**: Brand elements + Lee-Wuh
- **Animation**: Subtle movement
- **Interactions**: Hover effects, navigation

## Performance Monitoring

### Metrics to Track

- **Load time**: Scene load duration
- **Frame rate**: FPS during animation
- **Memory usage**: Runtime memory consumption
- **GPU usage**: GPU utilization
- **Interaction latency**: Response time to interactions

### Optimization Targets

- **Load time**: Under 3 seconds
- **Frame rate**: 60 FPS minimum
- **Memory usage**: Under 100MB
- **GPU usage**: Under 50%
- **Interaction latency**: Under 100ms

## File Organization

### Naming Convention

- `lee-wuh-hero.spline`
- `lee-wuh-throne-room.spline`
- `lee-wuh-brand-portal.spline`
- `lee-wuh-preview.spline`

### Directory Structure

```
/public/3d/
  ├── lee-wuh-hero.spline
  ├── lee-wuh-throne-room.spline
  ├── lee-wuh-brand-portal.spline
  └── lee-wuh-preview.spline
```

## Quality Control

### Checklist

- [ ] Scene under size limit
- [ ] Loads within time target
- [ ] Runs at 60 FPS
- [ ] Interactions responsive
- [ ] Fallback provided
- [ ] Mobile tested
- [ ] Memory usage acceptable
- [ ] No visual glitches

### Testing

- Test in target browsers (Chrome, Safari, Firefox)
- Test on mobile devices (iOS, Android)
- Test with different screen sizes
- Test with low-end devices
- Test loading performance

## Interactive Behaviors

### Mouse Interactions

- **Hover**: Highlight or scale effect
- **Click**: Trigger animation or navigation
- **Drag**: Camera orbit or object manipulation
- **Scroll**: Zoom or pan

### Touch Interactions

- **Tap**: Same as click
- **Swipe**: Camera orbit
- **Pinch**: Zoom
- **Two-finger drag**: Pan

## Brand Guidelines

### Colors

- **Primary**: Purple (#8B5CF6)
- **Secondary**: Gold (#F59E0B)
- **Accent**: White (#FFFFFF)
- **Background**: Black (#000000)

### Lighting

- **Key light**: White, warm tone
- **Fill light**: White, cool tone
- **Rim light**: Purple accent
- **Ambient**: Low intensity

## Troubleshooting

### Common Issues

- **Scene not loading**: Check URL, verify CDN
- **Performance issues**: Reduce complexity, optimize
- **Visual glitches**: Check materials, verify lighting
- **Not responsive**: Check canvas sizing
- **Memory leaks**: Clean up on unmount

### Debug Tools

- **Spline Viewer**: For testing scenes
- **Browser DevTools**: For performance profiling
- **Three.js Inspector**: For debugging
- **Network tab**: For loading issues

## Production Pipeline

### Workflow

1. **Design** scene in Spline
2. **Set up** interactions
3. **Test** in Spline Viewer
4. **Optimize** scene complexity
5. **Export** Spline scene
6. **Test** in web environment
7. **Add** fallback assets
8. **Integrate** with frontend
9. **Deploy** to production

### Automation

- Use Spline CLI for exports
- Automate optimization
- Set up CI/CD for assets
- Automate fallback generation

## Next Steps

- [ ] Create hero scene in Spline
- [ ] Set up throne room scene
- [ ] Create brand portal scene
- [ ] Optimize all scenes
- [ ] Create fallback assets
- [ ] Test in web environment
- [ ] Integrate with frontend
- [ ] Performance optimization
