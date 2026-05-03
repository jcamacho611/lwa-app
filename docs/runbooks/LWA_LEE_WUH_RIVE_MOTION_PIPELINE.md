# Lee-Wuh Rive Motion Pipeline v0

## Overview

This document defines the Rive motion pipeline for Lee-Wuh 2D animations and interactive states.

## Animation States

### Core States

- **Idle blink**: Subtle eye blinking (2-3 second cycle)
- **Aura pulse**: Energy aura pulsing effect
- **Thinking**: Head movement and concentration
- **Success**: Victory animation with celebration
- **Warning**: Alert state animation
- **Error**: Failure/retry animation
- **Rendering**: Active processing animation
- **Overlord mode**: Powerful transformation animation

### Secondary States

- **Loading**: Loading spinner or progress
- **Hover**: Mouse hover interaction
- **Click**: Click response animation
- **Transition**: State transition animations

## Motion Quality Standards

### Frame Rate

- **Target**: 60 FPS for smooth motion
- **Minimum**: 30 FPS acceptable
- **Web optimization**: Use frame skipping for performance

### Duration

- **Idle animations**: 2-4 second loops
- **Interaction animations**: 0.5-1 second
- **Transition animations**: 0.3-0.5 second
- **Complex animations**: Under 3 seconds

### Easing

- **Smooth**: Use ease-in-out for natural motion
- **Bounce**: Use for playful interactions
- **Elastic**: Use for energetic states
- **Linear**: Use for mechanical movements

## Performance Budgets

### File Size

- **Target**: Under 500KB per .riv file
- **Maximum**: 1MB absolute limit
- **Total assets**: Under 2MB for all Rive assets

### Runtime Performance

- **CPU usage**: Under 10% during animation
- **Memory usage**: Under 20MB for Rive runtime
- **Frame time**: Under 16ms (60 FPS target)

## Fallback Strategies

### When Rive Fails

1. **Static PNG**: Show static image of Lee-Wuh
2. **CSS animation**: Use CSS for simple animations
3. **SVG animation**: Use SVG as lightweight alternative
4. **No animation**: Show static state with loading indicator

### Progressive Enhancement

- Load static image first
- Load Rive runtime asynchronously
- Swap to Rive when ready
- Graceful degradation if Rive fails

## Integration Patterns

### React Integration

```typescript
import { useRive } from '@rive-app/react-canvas';

function LeeWuhMascot() {
  const { rive } = useRive({
    src: '/animations/lee-wuh.riv',
    stateMachines: 'Idle',
  });
  
  return <canvas ref={rive.canvas} />;
}
```

### State Machine Setup

- Use state machines for complex interactions
- Name states clearly: `Idle`, `Thinking`, `Success`
- Use triggers for state transitions
- Add inputs for dynamic control

## Animation Specifications

### Idle Blink

- **Duration**: 2.5 second loop
- **Action**: Subtle eye close/open
- **Frequency**: Every 2-3 seconds
- **Ease**: Smooth ease-in-out

### Aura Pulse

- **Duration**: 3 second loop
- **Action**: Scale aura up/down
- **Intensity**: 10-20% scale change
- **Ease**: Smooth sine wave

### Thinking

- **Duration**: 2 second loop
- **Action**: Head tilt, hand on chin
- **Variation**: 2-3 variations for variety
- **Ease**: Natural ease-in-out

### Success

- **Duration**: 1.5 second one-shot
- **Action**: Arms raised, celebration
- **Follow-through**: Return to idle
- **Ease**: Bounce for energy

### Warning

- **Duration**: 1 second loop
- **Action**: Lean forward, concerned
- **Color**: Yellow/orange accent
- **Ease**: Quick in, slow out

### Error

- **Duration**: 1.5 second one-shot
- **Action**: Slump shoulders, disappointed
- **Recovery**: Return to idle
- **Ease**: Slow in, quick out

### Rendering

- **Duration**: 2 second loop
- **Action**: Active working pose
- **Variation**: Subtle movement
- **Ease**: Continuous motion

### Overlord Mode

- **Duration**: 3 second one-shot
- **Action**: Transformation, power up
- **Follow-through**: Maintain powerful state
- **Ease**: Dramatic ease-in-out

## File Organization

### Naming Convention

- `lee-wuh-idle.riv`
- `lee-wuh-thinking.riv`
- `lee-wuh-success.riv`
- `lee-wuh-warning.riv`
- `lee-wuh-error.riv`
- `lee-wuh-rendering.riv`
- `lee-wuh-overlord.riv`

### Directory Structure

```
/public/animations/
  ├── lee-wuh-idle.riv
  ├── lee-wuh-thinking.riv
  ├── lee-wuh-success.riv
  ├── lee-wuh-warning.riv
  ├── lee-wuh-error.riv
  ├── lee-wuh-rendering.riv
  └── lee-wuh-overlord.riv
```

## Quality Control

### Checklist

- [ ] File under 500KB
- [ ] Animation plays smoothly at 60 FPS
- [ ] State transitions work correctly
- [ ] No visual artifacts or glitches
- [ ] Colors match brand guidelines
- [ ] Fallback image provided
- [ ] Performance tested on mobile
- [ ] Memory usage acceptable

### Testing

- Test in target browsers (Chrome, Safari, Firefox)
- Test on mobile devices (iOS, Android)
- Test with different screen sizes
- Test with low-end devices
- Test loading performance

## Optimization Techniques

### File Size Reduction

- Remove unused artboards
- Optimize vector paths
- Reduce number of nodes
- Use shared assets
- Enable compression

### Runtime Optimization

- Use state machines efficiently
- Avoid unnecessary recalculations
- Use GPU acceleration when available
- Cache rendered frames
- Use requestAnimationFrame

## Interactive Behaviors

### Mouse Interactions

- **Hover**: Subtle scale or color change
- **Click**: Trigger animation or state change
- **Drag**: If applicable for interactive elements
- **Scroll**: Parallax or follow effect

### Touch Interactions

- **Tap**: Same as click
- **Swipe**: Directional triggers
- **Pinch**: Scale effects
- **Long press**: Context menus

## Brand Guidelines

### Colors

- **Primary**: Purple (#8B5CF6)
- **Secondary**: Gold (#F59E0B)
- **Accent**: White (#FFFFFF)
- **Background**: Black (#000000)
- **Warning**: Yellow (#EAB308)
- **Error**: Red (#EF4444)

### Typography

- **Font**: Inter or system font
- **Weight**: 500-700 for readability
- **Size**: 16-24px for web
- **Color**: White on dark backgrounds

## Troubleshooting

### Common Issues

- **Animation not playing**: Check state machine setup, verify file path
- **Performance issues**: Reduce complexity, optimize file size
- **Visual glitches**: Check vector paths, verify easing
- **Not responsive**: Check canvas sizing, verify resize handler
- **Memory leaks**: Clean up Rive instances on unmount

### Debug Tools

- **Rive Debugger**: For inspecting .riv files
- **Browser DevTools**: For performance profiling
- **Rive Viewer**: For testing animations
- **Network tab**: For loading issues

## Production Pipeline

### Workflow

1. **Design** animation in Rive
2. **Set up** state machines
3. **Test** in Rive Viewer
4. **Optimize** file size
5. **Export** .riv file
6. **Test** in web environment
7. **Add** fallback images
8. **Integrate** with frontend
9. **Deploy** to production

### Automation

- Use Rive CLI for batch exports
- Automate file optimization
- Set up CI/CD for asset pipeline
- Automate fallback generation

## Next Steps

- [ ] Create core animation states
- [ ] Set up state machines
- [ ] Optimize file sizes
- [ ] Create fallback images
- [ ] Test in web environment
- [ ] Integrate with frontend
- [ ] Add interactive behaviors
- [ ] Performance optimization
