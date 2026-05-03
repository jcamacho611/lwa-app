# LEE-WUH Mascot Brand System v0

## Overview

LEE-WUH is the official mascot of LWA, representing "The Last Creator" - a cute but dangerous anime final-boss chibi character that embodies the premium, mythic identity of the LWA video creation ecosystem.

## Brand Identity

### Character Profile
- **Name**: Lee-Wuh (pronounced "lee-wuh")
- **Role**: The Last Creator / Guardian of the Realm
- **Tagline**: "Create. Inspire. Takeover."
- **Style**: Cute but dangerous anime final-boss chibi
- **Cultural Fusion**: African + Japanese aesthetics with American streetwear twist
- **Color Palette**: Gold / Purple / Black luxury colors
- **Key Features**: Big jeweled dreadlocks, overlord/creator-god aura, furry creature energy

### Brand Naming Rules
- **LEE-WUH**: Used for mascot, merch, cultural brand moments
- **LWA**: Used for app, company, backend, frontend, technical references
- **Mixed Usage**: Strategic combination for brand moments (e.g., "LWA powered by LEE-WUH")

## Asset Organization

### Current Assets
```
lwa-web/public/brand/
├── lee-wuh-mascot.png          # Main mascot character (PNG)
└── README.md                   # Brand asset documentation
```

### Component Structure
```
lwa-web/lib/brand/
└── lee-wuh.ts                  # Brand constants and types

lwa-web/components/brand/
├── LeeWuhMascot.tsx           # Core mascot component
├── LeeWuhPresence.tsx         # App-wide presence component
├── LeeWuhTip.tsx              # Contextual tips component
├── LeeWuhLoadingState.tsx     # Loading state component
└── LeeWuhEmptyState.tsx       # Empty state component
```

## Component System

### 1. LeeWuhMascot
Core mascot rendering component with flexible configuration.

**Props:**
- `state`: LeeWuhState (idle, watching, thinking, etc.)
- `size`: LeeWuhSize (sm, md, lg, hero)
- `variant`: bust | full | sticker | watermark
- `showAura`: boolean (purple glow effect)
- `showLabel`: boolean (name and role display)
- `className`: string (custom styling)

**Features:**
- Next.js Image optimization
- Lazy loading support
- Reduced motion compatibility
- No layout shift
- Aura animation effects
- Overlord badge for success/overlord states

### 2. LeeWuhPresence
App-wide mascot presence for screen-specific interactions.

**Props:**
- `screen`: home | generate | video_os | loading | results | empty | error
- `state`: LeeWuhState
- `message`: string (custom message override)
- `compact`: boolean (mobile-friendly compact mode)
- `className`: string

**Usage:**
- Hero side guardian on homepage
- Loading companion in processing states
- Empty state guide
- Error state friendly warning
- Result celebration indicator

### 3. LeeWuhTip
Small contextual brand tips for user guidance.

**Props:**
- `tone`: default | success | warning | danger | premium
- `children`: ReactNode (tip content)

**Examples:**
- "Lee-Wuh says: Drop the source. I'll find the first move."
- "Lee-Wuh says: Rendered proof first. Strategy second."
- "Lee-Wuh says: This one builds trust. Post it with proof."

### 4. LeeWuhLoadingState
Premium loading state with mascot and progress indication.

**Props:**
- `phase`: ingesting | analyzing | composing | rendering | packaging | complete
- `title`: string (loading title)
- `body`: string (loading description)

**Features:**
- Phase-specific mascot states
- Premium progress visualization
- Contextual messaging
- Reduced motion support

### 5. LeeWuhEmptyState
Empty screen helper with mascot guidance.

**Props:**
- `title`: string (empty state title)
- `body`: string (empty state description)
- `action`: ReactNode (call-to-action button)

**Usage Examples:**
- No source assets yet
- No timelines yet  
- No render jobs yet
- No packages yet

## Brand Constants

### Colors
```typescript
colors: {
  black: "#050505",      // Primary background
  charcoal: "#111016",   // Secondary background
  gold: "#F4C45D",       // Primary accent
  deepGold: "#B88422",   // Secondary accent
  purple: "#8B3DFF",     // Primary brand color
  violet: "#B56CFF",     // Secondary brand color
  red: "#C92A2A",        // Error/danger accent
}
```

### States
```typescript
type LeeWuhState =
  | "idle"      // Default waiting state
  | "watching"  // Observing user actions
  | "thinking"  // Processing/analyzing
  | "ingesting" // Loading source material
  | "composing" // Building timeline
  | "rendering" // Generating output
  | "success"   // Completed successfully
  | "warning"   // Caution state
  | "error"     // Failure state
  | "overlord"  // Ultimate success state
```

### Messages
Each state has contextual messages that guide users:
- `idle`: "Drop the source. I'll find the first move."
- `success`: "Overlord status. This one is ready."
- `error`: "The realm rejected that move. Try again clean."
- `overlord`: "Create. Inspire. Takeover."

## Screen Integration Rules

### Homepage
- Hero side guardian or corner presence
- Welcome message for new users
- Brand establishment without blocking CTAs

### Clip Studio / Generate
- Source input helper
- Loading state companion
- Success celebration
- Error state friendly warning

### Video OS / Command Center
- Command guardian presence
- Loading/processing states
- Empty state guides
- Result celebrations

### Empty States
- Contextual guidance for missing data
- Clear action prompts
- Brand consistency across screens

### Error States
- Friendly error presentation
- Recovery guidance
- Premium error experience

## Design Guidelines

### Visual Hierarchy
- Lee-Wuh should be present but not loud
- Never center mascot in workflow cards
- Use as hero art, loading companion, empty guide, or result celebration
- Maintain black/gold/purple consistency

### Motion Guidelines
- Support reduced motion preferences
- Use CSS animations with `motion-safe:` prefix
- No jarring or distracting animations
- Smooth, premium transitions only

### Performance Rules
- Optimize images for web (Next.js Image component)
- Lazy load mascots when possible
- No layout shift during loading
- Respect user's motion preferences

## Future Development Roadmap

### v1: Animated PNG/WebP States
- Micro-animations for each state
- Smooth transitions between states
- Enhanced visual feedback

### v2: Rive Interactive State Machine
- Interactive mascot animations
- State-based animation system
- User interaction responses

### v3: Spline Web 3D Hero Scene
- 3D mascot implementation
- Interactive 3D scenes
- Hero page 3D presence

### v4: Blender Rigged GLB Model
- Full 3D rigged model
- Advanced posing and animation
- Web-optimized 3D delivery

### v5: Live Reactive App State Engine
- Real-time app state reactions
- Dynamic mascot behavior
- Context-aware responses

### v6: Merch/Sticker Export Kit
- Print-ready assets
- Sticker designs
- Merchandise templates

## 3D Model Pipeline Plan

### Source File Management
- Create Blender source file outside repo
- Maintain asset in external storage
- Version control model separately

### Export Specifications
- GLB format under 5MB
- Web-optimized textures
- Rigged for animation
- Multiple pose variants

### Interactive States
- Idle: Breathing/looking around
- Blink: Natural eye movement
- Aura Pulse: Energy glow effect
- Blade Glow: Power activation
- Success Pose: Victory stance
- Warning Look: Caution expression
- Overlord Throne: Ultimate power state

### Web Integration
- Dynamic import for 3D viewer
- Lazy load on hero/mascot lab pages
- Never block app startup
- Fallback to 2D for performance

## File Size and Performance Rules

### Image Assets
- Main mascot PNG: Optimized under 200KB
- WebP variants: 50% smaller than PNG
- Multiple sizes: Responsive loading
- Progressive loading: Blur to sharp

### Animation Assets
- Rive files: Under 100KB per state
- 3D models: Under 5MB total
- Audio: Optional, under 50KB
- Total brand assets: Under 10MB

### Loading Strategy
- Critical path: Load mascot after main content
- Lazy loading: Non-critical mascot appearances
- Progressive enhancement: Start with 2D, upgrade to 3D
- Performance monitoring: Track brand asset impact

## Merchandise and Social Usage

### Print Assets
- High-resolution mascot files
- Multiple color variants
- Transparent backgrounds
- Print-ready formats (PNG, SVG)

### Social Media
- Platform-specific sizes
- Animated versions where supported
- Consistent brand presentation
- Engagement-focused content

### Sticker Designs
- Die-cut templates
- Material specifications
- Color variants
- Packaging designs

## Implementation Examples

### Homepage Integration
```tsx
import { LeeWuhPresence } from "@/components/brand/LeeWuhPresence";

<LeeWuhPresence
  screen="home"
  state="idle"
  message="Drop one source. I'll find the strongest first move."
/>
```

### Loading State
```tsx
import { LeeWuhLoadingState } from "@/components/brand/LeeWuhLoadingState";

<LeeWuhLoadingState
  phase="analyzing"
  title="Lee-Wuh is finding the signal"
  body="Scanning the source for the strongest hook, proof, and post order."
/>
```

### Empty State
```tsx
import { LeeWuhEmptyState } from "@/components/brand/LeeWuhEmptyState";

<LeeWuhEmptyState
  title="No source assets yet"
  body="Add a video, song, script, voice note, or URL and I'll start building the realm."
  action={<AddSourceButton />}
/>
```

### Contextual Tips
```tsx
import { LeeWuhTip } from "@/components/brand/LeeWuhTip";

<LeeWuhTip tone="premium">
  This clip builds trust. Post it with proof for maximum impact.
</LeeWuhTip>
```

## Validation and Testing

### Component Testing
- Unit tests for all components
- Visual regression testing
- Accessibility testing
- Performance impact measurement

### Integration Testing
- Screen-specific integration testing
- Cross-browser compatibility
- Mobile responsiveness
- Reduced motion support

### Brand Consistency
- Visual style guide adherence
- Color palette validation
- Typography consistency
- Motion guideline compliance

This mascot brand system establishes Lee-Wuh as a premium, interactive brand presence that enhances the LWA experience without interfering with the core functionality, creating a memorable creator-native identity that scales from simple 2D graphics to advanced 3D interactions.
