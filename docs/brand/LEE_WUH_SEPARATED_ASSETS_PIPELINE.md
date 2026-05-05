# Lee-Wuh Separated Assets Pipeline

## Purpose

Lee-Wuh must function as a living interface layer for LWA, not a flat poster.

This requires three separated production layers:

1. Character cutout
2. World/background
3. Realm Blade sword prop

## Final Public Paths

```text
lwa-web/public/brand/lee-wuh/lee-wuh-character-transparent.png
lwa-web/public/brand/lee-wuh/backgrounds/lee-wuh-world-background.png
lwa-web/public/brand/lee-wuh/props/lee-wuh-realm-sword.png
```

## Source/Archive Paths

```text
brand-source/lee-wuh/separated-assets/lee-wuh-character-transparent.png
brand-source/lee-wuh/separated-assets/lee-wuh-world-background.png
brand-source/lee-wuh/separated-assets/lee-wuh-realm-sword.png
```

## Reference Paths

```text
brand-source/lee-wuh/references/lee-wuh-main-reference.png
brand-source/lee-wuh/references/lee-wuh-turnaround-reference.png
brand-source/lee-wuh/references/lee-wuh-3d-ready-reference.png
```

## Layer Uses

### Character Cutout

Used for:

- floating living agent
- loading states
- processing states
- homepage hero foreground
- game avatar reference
- Blender model reference

### World Background

Used for:

- homepage atmosphere
- realm/game environment
- marketplace atmosphere
- Company OS atmosphere
- animated video-like CSS backgrounds

### Sword Prop

Used for:

- game item
- CTA hover effects
- badges
- loading effects
- Blender weapon reference

## Rule

The app must build even when final PNG assets are missing.

Use fallback:

```text
/brand/lee-wuh-hero-16x9.svg
```

## Next Production Step

Replace fallback assets with generated PNGs at the exact public paths, then upgrade Lee-Wuh motion states:

```text
idle
breathe
blink
hover
click
speak
thinking
marketplace guide
realm portal
victory
error
```
