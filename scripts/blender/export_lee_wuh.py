"""
Blender Python script for exporting Lee-Wuh character to GLB
Run inside Blender: Scripting tab > Open > Run Script
"""

import bpy
import os

# Export settings
EXPORT_DIR = "/Users/bdm/LWA/lwa-app/public/brand/lee-wuh"
FILENAME = "lee-wuh-mascot.glb"

# Ensure export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)

# Full export path
filepath = os.path.join(EXPORT_DIR, FILENAME)

# Export settings for web optimization
bpy.ops.export_scene.gltf(
    filepath=filepath,
    export_format='GLB',
    export_copyright="LWA - Lee-Wuh",
    export_image_format='WEBP',
    export_texture_dir="textures",
    export_keep_originals=False,
    export_texcoords=True,
    export_normals=True,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_draco_position_quantization=14,
    export_draco_normal_quantization=10,
    export_draco_texcoord_quantization=12,
    export_tangents=False,
    export_materials='EXPORT',
    export_colors=False,
    export_cameras=False,
    export_lights=False,
    export_yup=True,
    export_apply=True,
    export_animations=True,
    export_animation_mode='ACTIONS',
    export_nla_strips_merged_animation_name='Animation',
    export_def_bones=False,
    export_hierarchy_flatten_bone=False,
    export_armature_object_remove=False,
    export_vertex_influences_nb=4,
)

print(f"✓ Exported: {filepath}")
print(f"✓ File size: {os.path.getsize(filepath) / 1024:.1f} KB")
