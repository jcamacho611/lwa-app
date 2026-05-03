# Lee-Wuh Mascot Brand System v0

## Overview

Lee-Wuh is the official mascot and brand guide for LWA (The Creator Engine). Lee-Wuh serves as the memorable face and cultural identity layer, while LWA remains the technical product and company name.

**Core Rule**: LWA = Product/App/Company, Lee-Wuh = Mascot/Brand/Culture

## Brand Identity

### Character Profile
- **Name**: Lee-Wuh (pronounced "lee-wuh")
- **Role**: The Last Creator
- **Tagline**: Create. Inspire. Take over.
- **Core Line**: The final boss of lazy content.
- **Personality**: Afro-futurist anime final boss with creator energy
- **Style**: Japanese x African x American fusion, premium luxury with streetwear edge

### Visual Design
- **Aesthetic**: Cute but powerful anime final boss chibi
- **Features**: Big jeweled dreads, furry creature energy, overlord aura
- **Colors**: Black, gold, purple luxury palette with red accents
- **Fusion**: African + Japanese + American cultural elements

## Asset System

### Asset Paths
```
lwa-web/public/brand/
├── lee-wuh-hero-16x9.png     # Homepage hero (16:9)
├── lee-wuh-mascot.png         # General mascot (square)
├── lee-wuh/avatar.png          # Small avatars
├── lee-wuh/loading.png         # Loading states
└── lee-wuh/whop-cover.png     # Marketplace listings
```

### Asset Usage Guide
| Asset | Use Case | Dimensions |
|-------|----------|------------|
| hero-16x9 | Homepage hero, marketing | 1600x720 |
| mascot | General brand use | 720x720 |
| avatar | Loading states, small UI | 128x128 |
| loading | Processing screens | 256x256 |
| whop-cover | Marketplace, product pages | 1200x630 |

## Component System

### LeeWuhMascot
**Purpose**: Core mascot rendering component
```tsx
<LeeWuhMascot
  state="thinking"
  size="md"
  variant="full"
  showAura={true}
  showLabel={false}
  className="custom-class"
/>
```

**Props**:
- `state`: idle, watching, thinking, ingesting, composing, rendering, success, warning, error, overlord
- `size`: sm, md, lg, hero
- `variant`: bust, full, sticker, watermark
- `showAura`: Purple glow effect
- `showLabel`: Name and role display
- `className`: Custom CSS classes

### LeeWuhTip
**Purpose**: Contextual guidance bubbles
```tsx
<LeeWuhTip
  message="Drop one source. I'll find the strongest first move."
  tone="premium"
  size="md"
  showMascot={true}
/>
```

**Props**:
- `message`: Custom tip text (auto-generated if not provided)
- `tone`: default, success, warning, danger, premium
- `size`: sm, md, lg
- `showMascot`: Show mascot avatar

### LeeWuhLoadingState
**Purpose**: Premium loading screens with mascot
```tsx
<LeeWuhLoadingState
  title="Lee-Wuh is finding your strongest moments..."
  progress={75}
  showProgress={true}
  size="lg"
/>
```

**Props**:
- `title`: Loading title
- `message`: Custom loading message
- `progress`: Progress percentage (0-100)
- `showProgress`: Show progress bar
- `size`: sm, md, lg

### LeeWuhEmptyState
**Purpose**: Empty state helpers with mascot guidance
```tsx
<LeeWuhEmptyState
  title="No sources yet"
  message="Feed Lee-Wuh a source."
  action={<AddSourceButton />}
  size="md"
/>
```

**Props**:
- `title`: Empty state title
- `message`: Custom empty message
- `action`: Call-to-action component
- `size`: sm, md, lg

## Messaging System

### Homepage Hero
- **Eyebrow**: "Meet Lee-Wuh"
- **Headline**: "The final boss of lazy content."
- **Subtext**: "Drop one video. Get the best clips, hooks, captions, and posting angles."
- **Description**: "Lee-Wuh is the guardian of the creator engine..."

### Loading States
- **Primary**: "Lee-Wuh is finding your strongest moments..."
- **Secondary**: "Scanning hooks, silence, energy, and viral structure."
- **Processing**: "Lee-Wuh is analyzing the source material..."
- **Rendering**: "Lee-Wuh is composing the perfect clip..."

### Empty States
- **Primary**: "Feed Lee-Wuh a source."
- **Secondary**: "Paste a video URL and let the clipping engine find the best short-form moments."
- **No Sources**: "No sources yet. Add a video and Lee-Wuh will get to work."

### Success States
- **Primary**: "Boss-level clip detected."
- **Secondary**: "Post this first for maximum impact."
- **Completed**: "Lee-Wuh has finished analyzing your content."

### Tips Library
- "Drop one source. I'll find the strongest first move."
- "Rendered proof first. Strategy second."
- "Boss-level clip detected. Post this first."
- "The silence before the drop matters most."
- "Your first 3 seconds determine everything."

## Design Rules

### Placement Guidelines
- **Never Center**: Keep Lee-Wuh at edges, corners, or side panels
- **Mobile Safe**: Collapsible avatar on small screens
- **State-Aware**: Different expressions for loading, success, error
- **Premium Feel**: Gold/purple aura effects, not cartoonish

### Do Not Block
- **Source Input**: Lee-Wuh guides, doesn't interfere
- **Results Display**: Lee-Wuh celebrates, doesn't cover
- **Timeline Editing**: Lee-Wuh watches from side, doesn't block
- **Export Functions**: Lee-Wuh confirms success, doesn't interrupt

### Animation Rules
- **Reduced Motion Safe**: Respect user preferences
- **Micro-interactions**: Subtle breathing, thinking animations
- **Loading States**: Premium progress indicators, not spinners
- **Success Celebrations**: Quick, non-intrusive effects

## Integration Guidelines

### Homepage Integration
```tsx
// In CinematicHero.tsx
<LeeWuhMascot
  state="overlord"
  size="hero"
  variant="full"
  showAura={true}
  useHeroAsset={true}
/>
```

### Generate Flow Integration
```tsx
// Empty state
<LeeWuhEmptyState
  title="No sources yet"
  message="Feed Lee-Wuh a source."
  action={<AddSourceButton />}
/>

// Loading state
<LeeWuhLoadingState
  title="Lee-Wuh is finding your strongest moments..."
  showProgress={true}
/>
```

### Video OS Integration
```tsx
// Panel tip
<LeeWuhTip
  message="Timeline composed. Ready for rendering."
  tone="success"
  size="sm"
/>
```

## Performance Guidelines

### Image Optimization
- **Format**: WebP for web, PNG fallback
- **Sizes**: Responsive loading with srcset
- **Loading**: Lazy loading for non-hero images
- **Compression**: Balance quality vs file size

### Animation Performance
- **CSS Transforms**: Use transform/opacity for smooth animations
- **Reduced Motion**: Respect `prefers-reduced-motion`
- **60fps**: Keep animations performant
- **GPU Acceleration**: Use `will-change` sparingly

## Future Roadmap

### Phase 1: Static v0 (Current)
- ✅ Static PNG mascot system
- ✅ Brand components and messaging
- ✅ Homepage and generate flow integration

### Phase 2: Rive Animation v1
- 🔄 Interactive state machine
- 🔄 Smooth transitions between states
- 🔄 Micro-interactions and reactions

### Phase 3: Spline 3D v2
- 📋 Web 3D hero scenes
- 📋 Interactive 3D mascot
- 📋 Spatial audio integration

### Phase 4: Blender GLB v3
- 📋 Rigged 3D model
- 📋 Advanced animations
- 📋 Custom expressions

### Phase 5: Reactive Engine v4
- 📋 App state integration
- 📋 Real-time reactions
- 📋 Contextual behavior

## File Size Rules

### What to Commit
- ✅ Optimized web assets (under 500KB)
- ✅ Component code and documentation
- ✅ Design system constants

### What to Keep External
- ❌ Large source files (PSD, AI, Blender)
- ❌ Raw 3D models (MB-sized files)
- ❌ High-resolution source art
- ❌ Video assets

### Asset Storage Strategy
- **Repository**: Optimized web assets only
- **Cloud Storage**: Large source files and raw assets
- **CDN**: Production asset delivery

## Usage Examples

### Basic Mascot Display
```tsx
import { LeeWuhMascot } from "@/components/brand/LeeWuhMascot";

<LeeWuhMascot state="idle" size="md" showAura={true} />
```

### Loading State with Progress
```tsx
import { LeeWuhLoadingState } from "@/components/brand/LeeWuhLoadingState";

<LeeWuhLoadingState
  title="Processing your video..."
  progress={45}
  showProgress={true}
/>
```

### Contextual Tip
```tsx
import { LeeWuhTip } from "@/components/brand/LeeWuhTip";

<LeeWuhTip
  message="Boss-level clip detected. Post this first."
  tone="success"
  showMascot={true}
/>
```

### Empty State with Action
```tsx
import { LeeWuhEmptyState } from "@/components/brand/LeeWuhEmptyState";

<LeeWuhEmptyState
  title="No clips yet"
  message="Add a video source to get started."
  action={<Button>Add First Source</Button>}
/>
```

## Development Guidelines

### Component Development
- Use TypeScript strictly
- Follow existing naming conventions
- Maintain accessibility (ARIA labels, alt text)
- Test reduced motion scenarios
- Validate responsive behavior

### Brand Consistency
- Use design system colors from `DESIGN_SYSTEM`
- Follow spacing and typography guidelines
- Maintain mascot personality in all messaging
- Test contrast ratios for accessibility

### Performance Monitoring
- Monitor bundle size impact
- Test loading performance
- Validate animation smoothness
- Check memory usage

---

**Version**: v0.1.0  
**Last Updated**: 2026-05-02  
**Next Review**: v1.0.0 (Rive integration)
