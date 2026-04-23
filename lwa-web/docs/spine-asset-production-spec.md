# LWA Spine Asset Production Spec

## Production Goal

Create premium edge characters that support the current LWA web shell without competing with the center product UI.

The first production pair is:

- Athena on the left edge.
- Hades on the right edge.

Both characters must be delivered as Spine-ready layered source files and runtime exports.

## Screen Placement Contract

- Characters live only on the left and right edges.
- Center 60% of the viewport must stay visually quiet for product UI.
- Character silhouettes should fade toward center.
- Faces and eye glow should remain readable at 1440px desktop width.
- Mobile and low-end fallback uses static PNG or CSS sprite only.

## Required Deliverables

- Layered PSD or layered source file per character.
- Transparent PNG reference render per character.
- Spine `.skel` export per character.
- Spine `.atlas` export per character.
- Atlas PNG sheet per character.
- Static fallback PNG per character at 1536 x 2304.
- Cropped web fallback PNG per character at 768 x 1536.
- Neutral expression preview.
- Speak expression preview.
- Alert expression preview.
- React expression preview.

## Canvas And Safe Area

- Source art ratio: 9:16.
- Recommended source size: 2048 x 3640.
- Runtime fallback size: 768 x 1536.
- Character body should occupy 84% to 92% of canvas height.
- Face should sit between 18% and 30% from top.
- Keep outer 8% transparent padding for glow and mask.
- Do not place important detail in the center-facing fade edge.

## Shared Layer Plan

Use these layer names where possible:

- root
- body
- hip
- spine
- chest
- neck
- head
- hair_front
- hair_back
- hair_side_L
- hair_side_R
- brow_L
- brow_R
- eye_white_L
- eye_white_R
- pupil_L
- pupil_R
- eyelid_upper_L
- eyelid_upper_R
- eyelid_lower_L
- eyelid_lower_R
- mouth_neutral
- mouth_open
- mouth_wide
- mouth_small
- shoulder_L
- shoulder_R
- arm_upper_L
- arm_lower_L
- hand_L
- arm_upper_R
- arm_lower_R
- hand_R
- leg_upper_L
- leg_lower_L
- foot_L
- leg_upper_R
- leg_lower_R
- foot_R
- cloth_front
- cloth_back
- cape
- armor_overlay
- glow_eye
- glow_aura
- fx_gold
- fx_blue
- fx_crimson

## Required Animation States

### idle_breathe

- 5 to 7 second loop.
- Chest, shoulder, robe, and hair motion only.
- Eye glow pulse remains subtle.
- No large hand or weapon motion.

### alert

- 1 to 2 second transition.
- Athena: slight head tilt and eye sharpen.
- Hades: chin lowers and eye burn increases.
- Must return cleanly to idle_breathe.

### speak

- 2 to 4 second loop.
- Mouth shapes use neutral, small, open, wide.
- Eye glow becomes steadier.
- Body movement stays restrained.

### react

- 1.5 to 3 second motion.
- Athena: robe lift, gaze lock, small shoulder shift.
- Hades: robe weight settles, crimson glow rises, hand or collar shift.
- No screen-center gestures.

## Athena Direction

- Silhouette: tall, balanced strategist with clean shoulders and a narrow crown line.
- Color: matte black, muted gold, silver-blue emissive details.
- Face: calm, intelligent, readable from the edge.
- Armor: black ceremonial breastplate, gold filigree, layered robe panels.
- Eye glow: silver-blue, low pulse, precise.
- Aura: blue intelligence haze behind head and shoulders with restrained gold rim.
- Product role: source input, strategy, recommendations.

## Hades Direction

- Silhouette: broad underworld judge with heavy robe fall and dense shoulder mass.
- Color: black, deep shadow, restrained crimson, sparse muted gold.
- Face: severe, calm, final.
- Armor: black plate under shadow robe, crimson lining, gold collar or wrist trim.
- Eye glow: tight crimson burn, not neon.
- Aura: low underworld haze anchored below chest.
- Product role: review, export truth, low-credit tension.

## Runtime Performance Rules

- Max two active characters at once.
- Use one atlas per character.
- Keep atlas count low: target one 2048 texture, max two.
- Avoid large transparent glow sheets.
- Glow should be a small additive slot, not a full-canvas layer.
- Cloth and hair physics must be baked or lightweight.
- No particle systems in Spine export.
- Characters must look acceptable when suspended to static pose.

## Naming Contract

- Athena fallback: `/brand-source/chars/athena.png`
- Hades fallback: `/brand-source/chars/hades.png`
- Athena Spine: `/brand-source/chars/athena.skel`
- Hades Spine: `/brand-source/chars/hades.skel`
- Athena atlas: `/brand-source/chars/athena.atlas`
- Hades atlas: `/brand-source/chars/hades.atlas`

## Acceptance Checklist

- Center UI remains readable with both characters visible.
- Athena reads as strategy and precision.
- Hades reads as judgment and discipline.
- Idle motion feels slow and premium.
- Alert and react states do not distract from source input or results.
- Speak state supports short oracle-style bubbles.
- PNG fallback works before Spine runtime ships.
- Spine export can be suspended without visual glitches.
