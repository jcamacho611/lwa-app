"""
Export Lee-Wuh from Blender to an optimized GLB runtime asset.

Usage inside Blender:
  blender --background /path/to/lee-wuh.blend --python scripts/blender/export_lee_wuh_glb.py

Output:
  lwa-web/public/characters/lee-wuh/lee-wuh.glb

Rules:
- Do not commit heavy .blend files.
- Commit only optimized runtime GLB when size is acceptable.
"""

from __future__ import annotations

import os
import sys

try:
    import bpy
except ImportError as exc:  # Allows py_compile outside Blender.
    print("This script must run inside Blender for export. py_compile check only.")
    sys.exit(0)


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(ROOT, "lwa-web", "public", "characters", "lee-wuh")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "lee-wuh.glb")


def prepare_scene() -> None:
    """Prepare scene for export - apply transforms and ensure materials."""
    bpy.ops.object.select_all(action="DESELECT")

    # Select all objects
    for obj in bpy.context.scene.objects:
        obj.select_set(True)

    # Apply transforms
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Ensure materials on mesh objects
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            if not obj.data.materials:
                # Create gold-themed material for LWA
                material = bpy.data.materials.new(name=f"{obj.name}_LWA_Material")
                material.use_nodes = True
                nodes = material.node_tree.nodes
                principled = nodes.get("Principled BSDF")
                if principled:
                    principled.inputs["Base Color"].default_value = (0.78, 0.58, 0.22, 1.0)  # Gold
                    principled.inputs["Roughness"].default_value = 0.48
                    principled.inputs["Metallic"].default_value = 0.8
                obj.data.materials.append(material)

            obj.select_set(False)


def export_glb() -> None:
    """Export optimized GLB for web use."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=OUTPUT_FILE,
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
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12,
    )

    file_size = os.path.getsize(OUTPUT_FILE) / 1024  # KB
    print(f"✓ Exported Lee-Wuh GLB to: {OUTPUT_FILE}")
    print(f"✓ File size: {file_size:.1f} KB")

    if file_size > 5120:  # 5MB
        print("⚠ Warning: File exceeds 5MB. Consider further optimization.")
    elif file_size > 10240:  # 10MB
        print("❌ Error: File exceeds 10MB. Do not commit without optimization.")


if __name__ == "__main__":
    prepare_scene()
    export_glb()
