# LWA Visual Generation Migration Notes

## Purpose

This document explains how LWA's visual generation stack is being migrated into fully LWA-owned architecture.

The goals are:

- preserve first-upload no-signup
- preserve export flow
- preserve multimodal routing
- keep clipping stable while visual generation becomes LWA-owned
- remove old provider-centered language from the product over time

## Current Product Rule

LWA owns the product.

That means the final system should be described as:

- LWA routes
- LWA generation runtime
- LWA visual generation
- LWA generated asset persistence
- LWA-owned UX and export flow

Older provider-shaped naming may still appear temporarily in compatibility history, tests, or transitional references, but it is not the product center.

## What Is Already True

The current active backend flow has already been moved toward LWA-native visual generation.

Verified areas include:

- compile passing on targeted backend files
- startup passing
- visual generation health route working
- visual generation idea flow working
- multimodal routing preserving video-to-clipping separation

## Migration Order

The correct order is:

1. preserve working behavior
2. absorb useful patterns into LWA-owned modules
3. move logic behind LWA-owned interfaces
4. verify parity or better behavior
5. remove old provider-shaped remnants where safe

This avoids regressions in:

- first-upload no-signup
- export
- clipping
- multimodal routing

## LWA-Owned Visual Generation Direction

### LWA Clipping Remains Separate

Video clipping continues to use the clipping pipeline and should not be blocked by visual generation work.

### LWA Visual Generation Owns Image And Idea Flows

Visual generation now belongs under LWA-owned routes/services/runtime structure.

That includes:

- visual generation route handling
- visual generation service logic
- LWA provider abstraction
- generated asset persistence
- LWA-native language in docs/tests/logs over time

## Compatibility Rule

Do not delete compatibility paths too early.

Only remove remaining old branded remnants when:

1. compile/startup verification passes
2. visual generation routes still work
3. multimodal routing still works
4. first-upload no-signup still works
5. export remains intact where relevant

## Remaining Cleanup Categories

Typical remaining cleanup after backend migration may include:

- old docs headings
- old test file names
- old provider-health assertions
- old comments/log strings
- historical references that no longer reflect active ownership

These should be cleaned carefully, not blindly.

## Final Target

The final target is a repo where active product architecture is described as LWA-owned end to end:

- routes
- services
- provider/runtime naming
- generated assets
- docs
- tests
- logs
- UI labels

At that point, the generation system is simply LWA.
