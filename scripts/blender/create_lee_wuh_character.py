"""
Create a procedural Lee-Wuh character blockout in Blender and export it as GLB.

Usage:
  blender --background --python scripts/blender/create_lee_wuh_character.py

Output:
  lwa-web/public/characters/lee-wuh/lee-wuh.glb
  lwa-web/public/characters/lee-wuh/lee-wuh.generated.blend (not committed)

This is not the final sculpt. It is the production bridge:
concept -> Blender scene -> GLB runtime -> web character stage.

Do not commit .blend source files. Commit only optimized runtime GLB if size is acceptable.
"""

from __future__ import annotations

import math
import os
import sys
from typing import Iterable, Tuple

try:
    import bpy
    from mathutils import Vector
except ImportError:
    print("This script must be run inside Blender. py_compile outside Blender is allowed.")
    sys.exit(0)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "lwa-web", "public", "characters", "lee-wuh")
OUT_GLB = os.path.join(OUT_DIR, "lee-wuh.glb")
OUT_BLEND = os.path.join(OUT_DIR, "lee-wuh.generated.blend")

# Color palette
BLACK = (0.015, 0.014, 0.013, 1)
CHARCOAL = (0.055, 0.049, 0.045, 1)
GOLD = (1.0, 0.64, 0.18, 1)
DARK_GOLD = (0.55, 0.32, 0.08, 1)
PURPLE = (0.52, 0.15, 1.0, 1)
DEEP_PURPLE = (0.18, 0.04, 0.34, 1)
WHITE = (0.92, 0.87, 0.76, 1)
RED = (0.75, 0.06, 0.045, 1)


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"


def mat(name: str, color: Tuple[float, float, float, float], metallic: float = 0.0, roughness: float = 0.45, emission: Tuple[float, float, float, float] | None = None, strength: float = 0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission:
            bsdf.inputs["Emission Color"].default_value = emission
            bsdf.inputs["Emission Strength"].default_value = strength
    return material


def add_uv_sphere(name: str, location, scale, material, segments: int = 48, rings: int = 24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj


def add_cube(name: str, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("soft bevel", "BEVEL")
    bevel.width = 0.08
    bevel.segments = 6
    obj.modifiers.new("weighted normals", "WEIGHTED_NORMAL")
    return obj


def add_cylinder(name: str, location, radius, depth, material, vertices: int = 32, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    obj.modifiers.new("weighted normals", "WEIGHTED_NORMAL")
    return obj


def add_torus(name: str, location, major_radius, minor_radius, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major_radius, minor_radius=minor_radius, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def add_cone(name: str, location, radius1, radius2, depth, material, rotation=(0, 0, 0), vertices=4):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def add_curve_tube(name: str, points: Iterable[Tuple[float, float, float]], material, bevel_depth=0.035):
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 8
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 5
    poly = curve.splines.new("POLY")
    pts = list(points)
    poly.points.add(len(pts) - 1)
    for point, co in zip(poly.points, pts):
        point.co = (co[0], co[1], co[2], 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def add_text(name: str, text: str, location, size: float, material, rotation=(math.radians(80), 0, 0)):
    bpy.ops.object.text_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.01
    obj.data.materials.append(material)
    return obj


def build_character() -> None:
    # Materials
    black = mat("LeeWuh velvet black", BLACK, 0.0, 0.38)
    charcoal = mat("LeeWuh charcoal cloth", CHARCOAL, 0.0, 0.5)
    gold = mat("LeeWuh royal gold", GOLD, 1.0, 0.25)
    dark_gold = mat("LeeWuh old gold", DARK_GOLD, 0.7, 0.32)
    purple = mat("LeeWuh purple energy", PURPLE, 0.0, 0.18, PURPLE, 2.8)
    deep_purple = mat("LeeWuh deep purple cloth", DEEP_PURPLE, 0.0, 0.42)
    white = mat("LeeWuh sneaker white", WHITE, 0.0, 0.34)
    red = mat("LeeWuh sneaker red", RED, 0.0, 0.32)

    # Body and head
    add_uv_sphere("LeeWuh head", (0, 0, 2.68), (0.78, 0.66, 0.62), black)
    add_uv_sphere("LeeWuh body", (0, 0, 1.48), (0.52, 0.38, 0.66), charcoal)

    # Ears
    add_cone("left cat ear", (-0.48, 0.01, 3.28), 0.28, 0.02, 0.52, black, rotation=(0, math.radians(-18), math.radians(22)), vertices=32)
    add_cone("right cat ear", (0.48, 0.01, 3.28), 0.28, 0.02, 0.52, black, rotation=(0, math.radians(18), math.radians(-22)), vertices=32)
    add_cone("left gold ear armor", (-0.5, -0.025, 3.29), 0.14, 0.0, 0.28, gold, rotation=(0, math.radians(-18), math.radians(22)), vertices=32)
    add_cone("right gold ear armor", (0.5, -0.025, 3.29), 0.14, 0.0, 0.28, gold, rotation=(0, math.radians(18), math.radians(-22)), vertices=32)

    # Eyes
    add_uv_sphere("left purple eye", (-0.28, -0.55, 2.78), (0.16, 0.055, 0.105), purple, 32, 16)
    add_uv_sphere("right purple eye", (0.28, -0.55, 2.78), (0.16, 0.055, 0.105), purple, 32, 16)
    add_uv_sphere("nose", (0, -0.66, 2.58), (0.065, 0.035, 0.045), black, 24, 12)

    # Forehead crest and jewelry
    add_cone("forehead gold sigil", (0, -0.66, 3.03), 0.14, 0.01, 0.34, gold, rotation=(math.radians(90), 0, math.radians(45)), vertices=4)
    add_torus("left earring", (-0.72, -0.28, 2.45), 0.105, 0.018, gold, rotation=(math.radians(90), 0, 0))
    add_torus("right earring", (0.72, -0.28, 2.45), 0.105, 0.018, gold, rotation=(math.radians(90), 0, 0))
    add_torus("neck chain", (0, -0.15, 2.05), 0.42, 0.024, gold, rotation=(math.radians(90), 0, 0))

    # Dreadlock-like hair tubes with gold cuffs
    for i in range(24):
        angle = (i / 24) * math.tau
        side = math.sin(angle)
        back = math.cos(angle)
        x0 = side * 0.38
        y0 = -0.04 + back * 0.22
        z0 = 3.17
        x1 = side * (0.65 + 0.15 * abs(back))
        y1 = 0.08 + back * 0.62
        z1 = 2.75 - 0.28 * max(back, 0)
        x2 = side * (0.86 + 0.14 * abs(back))
        y2 = 0.16 + back * 0.86
        z2 = 2.2 - 0.25 * max(back, 0)
        tube = add_curve_tube(f"dread tube {i:02d}", [(x0, y0, z0), (x1, y1, z1), (x2, y2, z2)], black, 0.045)
        cuff_count = 2 if i % 3 else 3
        for c in range(cuff_count):
            t = (c + 1) / (cuff_count + 1)
            x = x0 + (x2 - x0) * t
            y = y0 + (y2 - y0) * t
            z = z0 + (z2 - z0) * t
            add_torus(f"gold dread cuff {i:02d}-{c}", (x, y, z), 0.055, 0.012, gold, rotation=(math.radians(90), angle, 0))

    # Coat / robe panels
    add_cube("left long coat panel", (-0.32, -0.03, 1.17), (0.18, 0.055, 0.78), charcoal)
    add_cube("right long coat panel", (0.32, -0.03, 1.17), (0.18, 0.055, 0.78), charcoal)
    add_cube("center purple sash", (0, -0.39, 1.7), (0.5, 0.05, 0.09), deep_purple)
    add_cube("gold belt", (0, -0.42, 1.55), (0.56, 0.055, 0.055), gold)
    add_cube("left gold coat trim", (-0.55, -0.1, 1.18), (0.035, 0.04, 0.75), gold)
    add_cube("right gold coat trim", (0.55, -0.1, 1.18), (0.035, 0.04, 0.75), gold)
    add_text("robe glyph left", "夢", (-0.52, -0.18, 1.16), 0.18, gold, rotation=(math.radians(84), 0, math.radians(2)))
    add_text("robe glyph right", "創", (0.52, -0.18, 1.16), 0.18, gold, rotation=(math.radians(84), 0, math.radians(-2)))

    # Arms / hands
    add_cylinder("left arm", (-0.65, -0.05, 1.55), 0.105, 0.72, black, rotation=(0, math.radians(42), math.radians(14)))
    add_cylinder("right arm", (0.65, -0.05, 1.55), 0.105, 0.72, black, rotation=(0, math.radians(-42), math.radians(-14)))
    add_uv_sphere("left paw", (-0.96, -0.22, 1.34), (0.13, 0.11, 0.11), black)
    add_uv_sphere("right paw", (0.96, -0.22, 1.34), (0.13, 0.11, 0.11), black)

    # Legs and original sneakers
    add_cylinder("left leg", (-0.23, 0, 0.75), 0.12, 0.62, black)
    add_cylinder("right leg", (0.23, 0, 0.75), 0.12, 0.62, black)
    add_cube("left sneaker base", (-0.28, -0.18, 0.32), (0.24, 0.42, 0.12), white)
    add_cube("right sneaker base", (0.28, -0.18, 0.32), (0.24, 0.42, 0.12), white)
    add_cube("left sneaker red panel", (-0.28, -0.42, 0.38), (0.22, 0.045, 0.06), red)
    add_cube("right sneaker red panel", (0.28, -0.42, 0.38), (0.22, 0.045, 0.06), red)
    add_cube("left sneaker black tongue", (-0.28, -0.24, 0.48), (0.14, 0.04, 0.1), black)
    add_cube("right sneaker black tongue", (0.28, -0.24, 0.48), (0.14, 0.04, 0.1), black)

    # Tail
    add_curve_tube("purple black tail", [(0.55, 0.28, 1.05), (1.08, 0.38, 1.22), (1.22, -0.04, 1.44), (0.95, -0.18, 1.58)], black, 0.06)
    add_curve_tube("tail purple aura", [(0.58, 0.30, 1.08), (1.12, 0.40, 1.28), (1.28, -0.08, 1.48)], purple, 0.018)

    # Sword: ornate oversized creator blade
    add_cube("sword handle", (-0.86, -0.42, 0.92), (0.07, 0.07, 0.42), dark_gold)
    add_cube("sword guard", (-0.86, -0.42, 1.22), (0.34, 0.055, 0.06), gold)
    blade = add_cube("oversized creator blade", (-1.34, -0.48, 0.86), (0.13, 0.04, 0.9), gold)
    blade.rotation_euler[1] = math.radians(-35)
    add_curve_tube("sword purple edge energy", [(-1.65, -0.52, 0.15), (-1.5, -0.5, 0.58), (-1.24, -0.48, 1.25), (-1.07, -0.47, 1.68)], purple, 0.02)

    # Purple aura rings / realm energy
    add_torus("base purple aura ring", (0, 0, 0.18), 1.28, 0.018, purple, rotation=(0, 0, 0))
    for i in range(7):
        a = i / 7 * math.tau
        r = 1.15 + 0.12 * math.sin(i)
        add_curve_tube(
            f"realm energy lick {i}",
            [
                (math.cos(a) * r, math.sin(a) * r, 0.25),
                (math.cos(a + 0.24) * (r + 0.12), math.sin(a + 0.24) * (r + 0.12), 0.62),
                (math.cos(a + 0.42) * (r + 0.05), math.sin(a + 0.42) * (r + 0.05), 1.02),
            ],
            purple,
            0.018,
        )

    # Pedestal
    add_cylinder("black gold pedestal", (0, 0, 0.05), 1.25, 0.16, charcoal, vertices=96)
    add_torus("pedestal gold trim", (0, 0, 0.14), 1.25, 0.025, gold)
    add_text("pedestal inscription", "MAKE DREAMS REAL", (0, -1.08, 0.2), 0.14, gold, rotation=(math.radians(78), 0, 0))


def setup_camera_lighting() -> None:
    bpy.ops.object.light_add(type="AREA", location=(0, -4.4, 5.5))
    light = bpy.context.object
    light.name = "large softbox front"
    light.data.energy = 520
    light.data.size = 4.5

    bpy.ops.object.light_add(type="POINT", location=(-2.8, -1.2, 3.2))
    left = bpy.context.object
    left.name = "purple rim left"
    left.data.color = (0.52, 0.15, 1.0)
    left.data.energy = 180

    bpy.ops.object.light_add(type="POINT", location=(3, -1.1, 3.1))
    right = bpy.context.object
    right.name = "gold rim right"
    right.data.color = (1.0, 0.64, 0.18)
    right.data.energy = 150

    bpy.ops.object.camera_add(location=(0, -6.2, 2.35), rotation=(math.radians(72), 0, 0))
    camera = bpy.context.object
    bpy.context.scene.camera = camera
    camera.data.lens = 48


def export() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    bpy.ops.export_scene.gltf(
        filepath=OUT_GLB,
        export_format="GLB",
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
        export_animations=True,
        export_skins=True,
        export_morph=True,
        export_lights=False,
        export_cameras=False,
        export_yup=True,
    )
    print(f"Saved generated scene to: {OUT_BLEND}")
    print(f"Exported runtime GLB to: {OUT_GLB}")


if __name__ == "__main__":
    reset_scene()
    build_character()
    setup_camera_lighting()
    export()
