# LWA /GENERATE PAGE — ELITE DESIGN BLUEPRINT

## Core Philosophy

**Clarity over complexity. Hierarchy over features. Emotion without chaos.**

This page must feel like a **premium creator OS**, not "another AI tool."

---

## Visual Hierarchy (Z-Order)

### Layer 1: Background World (Z: -10)
**Purpose:** Set mood without distraction

```
Properties:
- Background image: /worlds/lee-wuh-realm-blur.jpg
- Filter: blur(20px) brightness(0.3)
- Opacity: 0.4
- Position: fixed, cover entire viewport
- No animation (static)
```

**Why:** Creates "this world exists" feel without blocking content.

---

### Layer 2: Character Presence (Z: -5)
**Purpose:** Lee-Wuh brand identity at edge

```
Position: bottom-right corner
Size: 200px width (desktop), 120px (mobile)
Opacity: 0.6 (subtle glow)
Animation: Slow breathing pulse (4s cycle)
State: "idle" mood
Visibility: 40% off-screen (peek effect)
```

**Why:** Bottom-right keeps center clean. Partial visibility = premium subtlety.

---

### Layer 3: Input Zone (Z: 10)
**Purpose:** Clear entry point

```
Position: Top center
Width: 600px max
Padding: 48px top, 24px sides

Components:
- Clean input field (no borders, subtle glow on focus)
- Single CTA button (gold accent)
- No secondary buttons visible initially
- Placeholder: "Paste your content here..."

Visual:
- Background: rgba(0,0,0,0.6) with backdrop-blur
- Border-radius: 16px
- Border: 1px solid rgba(255,255,255,0.1)
```

**Why:** Top = natural reading flow. Center = immediate attention. Clean = premium.

---

### Layer 4: BEST CLIP HERO (Z: 20)
**Purpose:** One clear decision

```
Position: Center (absolute center of viewport)
Width: 800px max

Structure:
┌─────────────────────────────────────────┐
│  🏆 POST THIS FIRST                     │
│                                         │
│  [Score Badge: 92/100]                  │
│                                         │
│  "Stop posting randomly if you          │
│   want to grow"                         │
│                                         │
│  Hook: [Copy Button]                    │
│  Caption: [Copy Button]                 │
│                                         │
│  [Why it works explanation]             │
│                                         │
│  CTA: "Follow for the full system"      │
└─────────────────────────────────────────┘

Visual:
- Background: gradient from #1A1A1A to #0A0A0A
- Border: 2px solid #C9A24A (gold accent)
- Border-radius: 24px
- Shadow: 0 25px 50px rgba(201,162,74,0.15)
- Padding: 40px
```

**Critical:** This must be the ONLY prominent element. Everything else fades back.

---

### Layer 5: Ranked Clip Stack (Z: 15)
**Purpose:** Secondary options (clearly secondary)

```
Position: Below hero, centered
Width: 800px max

Structure:
┌─────────────────────────────────────────┐
│  #2  [Score: 85]  "The truth about..."  │
│  #3  [Score: 78]  "This is the..."     │
│  #4  [Score: 65]  "Most people..."      │
└─────────────────────────────────────────┘

Visual:
- Smaller cards (compared to hero)
- Gray borders (not gold)
- Collapsed by default (expandable)
- Dimmed opacity (0.7)
- Hover: full opacity
```

**Why:** Shows "I have options" but guides to #1 clearly.

---

### Layer 6: Action Bar (Z: 25)
**Purpose:** Copy/export actions

```
Position: Fixed bottom center
Width: Auto (hug content)

Components:
- Copy Hook
- Copy Caption  
- Export All
- Schedule Post

Visual:
- Glassmorphism background
- Pill-shaped buttons
- Gold accent on primary action
```

---

## Color System

### Primary
- **Gold:** `#C9A24A` (accents, borders, CTAs)
- **Dark:** `#0A0A0A` (deep backgrounds)
- **Charcoal:** `#1A1A1A` (card backgrounds)

### Secondary
- **White:** `#FFFFFF` (primary text)
- **Gray 1:** `#A0A0A0` (secondary text)
- **Gray 2:** `#6B6B6B` (tertiary text)

### Semantic
- **Success:** `#10B981` (high scores)
- **Warning:** `#F59E0B` (medium scores)
- **Error:** `#EF4444` (alerts only)

---

## Typography Scale

```
Hero Title: 48px / font-bold / leading-tight
Hero Hook: 32px / font-semibold / leading-snug
Section Title: 24px / font-semibold
Body Large: 18px / font-normal
Body: 16px / font-normal
Caption: 14px / font-normal
Label: 12px / font-medium / uppercase / tracking-wide
```

Font: Inter (or system-ui fallback)

---

## Animation Principles

### Entry Animations
- **Hero card:** Fade up (0.6s, ease-out)
- **Input:** Fade in (0.4s)
- **Background:** Already visible (no animation)

### Micro-interactions
- **Copy button:** Scale 1.02 on hover
- **Cards:** Lift 4px on hover
- **Character:** Breathing pulse (4s infinite)
- **Score badge:** Subtle glow pulse

### Performance
- Use `transform` and `opacity` only
- Add `will-change` on animated elements
- Respect `prefers-reduced-motion`

---

## Responsive Breakpoints

### Desktop (1200px+)
- Full layout as specified
- Character: 200px
- Hero: 800px

### Tablet (768px - 1199px)
- Character: 150px
- Hero: 90% viewport width
- Input: 90% viewport width

### Mobile (< 768px)
- Character: Hidden (or 80px micro)
- Hero: 100% viewport width
- Input: 100% viewport width
- Stack all vertically

---

## Interaction Flow

### State 1: Empty
```
[Background]
[Character - subtle]
[Input Zone - prominent]
[Hero - hidden]
[Clip Stack - hidden]
[Action Bar - hidden]
```

### State 2: Generating
```
[Background]
[Character - reacts]
[Input Zone - disabled state]
[Loading State - center]
[Clip Stack - hidden]
[Action Bar - hidden]
```

### State 3: Results
```
[Background]
[Character - celebrates subtly]
[Input Zone - collapses to top]
[Hero - animates in]
[Clip Stack - visible below]
[Action Bar - visible]
```

---

## Critical Rules (Never Break)

### 1. Center Must Stay Clean
**Forbidden in center:**
- Characters
- Heavy animations
- Multiple competing CTAs
- Cluttered information

### 2. One Clear Winner
**Required:**
- Hero card shows "POST THIS FIRST"
- Score visible
- Hook prominent
- Copy actions immediate

### 3. Background = Mood, Not Content
**Background must:**
- Be blurred
- Be darkened
- Not compete with foreground
- Feel "atmospheric"

### 4. Character = Brand, Not UI
**Character must:**
- Stay at edges
- Never block interactions
- Be subtle (opacity < 0.7)
- Animate slowly (not distracting)

---

## Implementation Priority

### Phase 1: Structure
1. Background layer
2. Character positioning
3. Input zone layout
4. Hero card structure

### Phase 2: Styling
1. Color system
2. Typography
3. Spacing/sizing
4. Borders/shadows

### Phase 3: Animation
1. Entry animations
2. Micro-interactions
3. Character breathing
4. State transitions

### Phase 4: Polish
1. Responsive
2. Dark mode (if needed)
3. Reduced motion support
4. Final spacing adjustments

---

## Success Criteria

**Visual:**
- Hero card is unmistakably #1
- No confusion what to post
- Feels premium (not cluttered)
- Character adds brand without distraction

**Functional:**
- Copy buttons work instantly
- Ranking is clear
- Actions are accessible
- Responsive on all devices

**Emotional:**
- User feels guided (not overwhelmed)
- Confidence in the #1 clip
- "This is professional" feeling
- World feels alive (character presence)

---

## Emergency Revert Criteria

If any of these happen, **revert immediately**:

- Character blocks input or hero
- Multiple elements compete for attention
- Layout breaks on mobile
- Animations are distracting
- User can't find copy button in 2 seconds

---

*Blueprint Version: 1.0*
*Target: /generate page (clip-studio.tsx)*
*Status: Ready for implementation*
