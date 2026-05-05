# Lee-Wuh Blender 3D Mascot Artist / Modeler Handoff

## Brief

This replaces the Spine / 2D-layer handoff. I do **not** have separated 2D body-part assets ready. The goal is to build Lee-Wuh directly in **Blender** as a full 3D mascot character that can later be exported as a web/game-ready GLB.

Lee-Wuh is the living mascot / visual agent for LWA. He is not just a logo, sticker, or flat illustration. He needs to become a 3D character that can eventually appear in the website, game/world layer, marketplace, loading states, AI assistant interface, and future animations.

## Character Direction

Lee-Wuh should match the approved visual direction:

- Cute chibi / furry / anime final-boss energy
- Black panther / cat-like mascot feel
- Large expressive purple eyes
- Big dreadlocks with gold and purple beads
- Black, gold, and purple color palette
- Jeweled/luxury outfit
- Robe + streetwear + sneaker influence
- African + Japanese + American fusion
- Premium, powerful, playful, mystical
- Purple aura / realm energy
- Sword as a separate prop

He should feel strong enough for a game world, cute enough to be a mascot, and premium enough to represent the LWA brand.

## Main Goal

Please create Lee-Wuh as a **full 3D Blender character**, not a 2D Spine puppet.

The model should be built in Blender with a clean file structure and export-ready parts so it can eventually become:

1. A `.blend` source file
2. A web/game-ready `.glb` file
3. A rigged animated mascot
4. A homepage / app / game character
5. A clickable visual agent for the LWA frontend

## Required Blender Deliverables

Please deliver:

```text
lee-wuh-character.blend
lee-wuh-character.glb
lee-wuh-character.fbx optional
lee-wuh-realm-sword.glb optional separate prop
preview-render-front.png
preview-render-side.png
preview-render-back.png
preview-render-3quarter.png
```

If the full rig/animation is not included in the first version, please still structure the model so it can be rigged later.

## Required 3D Character Parts

The Blender model should include separate, named objects or collections for:

```text
Head
Body
Left Eye
Right Eye
Mouth / muzzle
Left Arm
Right Arm
Left Hand / paw
Right Hand / paw
Left Leg
Right Leg
Tail
Robe / coat
Robe trim
Dreadlocks
Gold dread beads
Purple beads / gems
Chest gem
Jewelry / chains
Sneakers
Realm Blade sword
Aura / energy rings optional
```

Please keep the sword separate enough that it can be animated, hidden, exported, or used as an independent game prop.

## Suggested Blender Collection Structure

Please organize the Blender file like this:

```text
LEE_WUH_CHARACTER
  body
  head
  face
  eyes
  mouth
  arms
  hands
  legs
  tail
  dreadlocks
  jewelry
  robe
  sneakers
  sword
  aura
  rig_optional
  lights_camera
```

## Modeling Style Requirements

The model should be:

- chibi proportions
- oversized head
- small powerful body
- clean readable silhouette
- expressive large purple eyes
- soft black panther/cat face
- stylized dreadlocks with bead detail
- ornate gold/purple luxury details
- clear robe/streetwear/sneaker mix
- readable from a distance in a web UI
- not overly realistic
- not horror/gore
- not generic fantasy
- not a copy of another known character

## Material Direction

Suggested materials:

```text
Black fur / matte dark material
Deep black robe / cloth
Metallic gold trim and jewelry
Glowing purple eyes
Purple gem / crystal material
White/cream eye highlights
Sneaker material
Purple aura / emissive energy material
```

## Rigging Goals

If rigging is included, please support these future animation states:

```text
idle_breathe
blink
hover_react
click_open
talk_loop
thinking
analyzing
rendering
point_right
point_left
marketplace_guide
realm_open
victory
error_confused
sword_powerup
```

If rigging is not included yet, please make sure the model topology and object separation make those animations possible later.

## Suggested Rig / Bone Areas

The model should eventually support control over:

```text
root
pelvis
spine
chest
neck
head
jaw / mouth
left_eye
right_eye
left_arm
right_arm
left_hand
right_hand
left_leg
right_leg
tail controls
dreadlock controls
robe controls
sword bone
```

## Web / Game Export Rules

The final GLB should be optimized enough for future web use.

Target performance goals:

```text
Agent GLB target: under 3 MB if possible
Hero GLB target: under 8 MB if possible
Clean object names
Textures packed or clearly linked
No unnecessary hidden objects
Origin and scale cleaned
Forward-facing character
```

If high-detail sculpting makes the file large, please also provide a lower-poly web version.

## Scale / Pose

Preferred default pose:

- Standing pose
- 3/4 front-facing
- sword held or sword separate beside him
- confident final-boss mascot stance
- arms slightly away from body for future rigging
- dreads visible and readable
- aura optional as separate effect

## Important Notes

Please make sure:

- Lee-Wuh still looks like the approved concept.
- The sword is its own prop/object.
- Dreads are modeled in a way that can be animated later.
- Jewelry and beads are separate or clearly grouped.
- The eyes can be animated or swapped later.
- The model is not one merged uneditable mesh unless there is also a clean source version.
- The Blender file is organized and named clearly.
- The export is usable for web/game pipelines.

## Acceptance Checklist

The delivery is complete when:

- I receive the `.blend` source file.
- I receive a `.glb` export.
- Lee-Wuh is recognizable as the chibi/furry anime-final-boss mascot.
- Dreadlocks, purple eyes, black/gold/purple palette, robe, jewelry, sneakers, and sword are present.
- The sword is separate or exportable as a separate prop.
- The file is organized with clear object/collection names.
- The model can be rigged/animated later.
- Preview renders are included from front, side, back, and 3/4 view.

## Final Delivery Request

Please send either:

1. A complete Blender source file plus GLB export, or
2. A first blockout Blender file that establishes the character shape, with a clear note on what still needs sculpting, rigging, materials, and animation.

The goal is to turn Lee-Wuh into a real 3D mascot that can move, breathe, blink, talk, guide users, and eventually act as the living visual agent inside the LWA app.
