import bpy
import math
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

OUTPUT_BLEND_DIR = os.path.join(REPO_ROOT, "brand-source", "lee-wuh", "blender")
OUTPUT_GLB_DIR = os.path.join(REPO_ROOT, "lwa-web", "public", "brand", "lee-wuh", "3d")

OUTPUT_BLEND = os.path.join(OUTPUT_BLEND_DIR, "lee-wuh-character-blockout.blend")
OUTPUT_GLB = os.path.join(OUTPUT_GLB_DIR, "lee-wuh-mascot.glb")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()


def make_mat(name, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


fur = make_mat("Lee-Wuh black warm fur", (0.045, 0.035, 0.032, 1), 0.0, 0.75)
muzzle = make_mat("Soft dark muzzle", (0.16, 0.12, 0.10, 1), 0.0, 0.65)
gold = make_mat("Royal gold metal", (1.0, 0.66, 0.16, 1), 1.0, 0.22)
purple = make_mat("Purple realm energy", (0.48, 0.12, 1.0, 1), 0.0, 0.18)
black_cloth = make_mat("Black embroidered robe", (0.015, 0.014, 0.018, 1), 0.0, 0.5)
white = make_mat("Eye white", (0.92, 0.88, 1.0, 1), 0.0, 0.25)
sole = make_mat("Sneaker sole", (0.92, 0.88, 0.78, 1), 0.0, 0.4)


def sphere(name, loc, scale, material, segments=48):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=24, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj


def cube(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("soft bevel", "BEVEL")
    bevel.width = 0.08
    bevel.segments = 6
    obj.modifiers.new("smooth", "WEIGHTED_NORMAL")
    return obj


def cylinder(name, loc, radius, depth, material, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def torus(name, loc, major, minor, material):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


body = sphere("small chibi body / hoodie base", (0, 0, 1.25), (0.72, 0.52, 0.82), black_cloth)
head = sphere("oversized Lee-Wuh head", (0, -0.02, 2.55), (1.08, 0.92, 0.95), fur)
sphere("cute muzzle", (0, -0.74, 2.42), (0.36, 0.20, 0.22), muzzle)
left_iris = sphere("left purple iris", (-0.34, -0.845, 2.75), (0.085, 0.022, 0.12), purple)
right_iris = sphere("right purple iris", (0.34, -0.845, 2.75), (0.085, 0.022, 0.12), purple)
sphere("left eye white", (-0.34, -0.80, 2.75), (0.17, 0.055, 0.22), white)
sphere("right eye white", (0.34, -0.80, 2.75), (0.17, 0.055, 0.22), white)
sphere("small black nose", (0, -0.93, 2.52), (0.12, 0.06, 0.08), fur)
sphere("left pointed ear", (-0.82, -0.05, 2.75), (0.20, 0.12, 0.32), fur)
sphere("right pointed ear", (0.82, -0.05, 2.75), (0.20, 0.12, 0.32), fur)

for i, x in enumerate([-0.82, -0.62, -0.42, -0.22, 0.0, 0.22, 0.42, 0.62, 0.82]):
    dread = cylinder(f"dreadlock_{i + 1}", (x, 0.18, 2.35), 0.06, 1.35, fur, vertices=24)
    dread.rotation_euler[0] = math.radians(18 + (i % 3) * 8)
    dread.rotation_euler[1] = math.radians(x * 12)
    for j, z in enumerate([2.65, 2.34, 2.04]):
        bead = torus(f"gold_bead_{i + 1}_{j + 1}", (x, -0.03, z), 0.075, 0.012, gold)
        bead.rotation_euler[0] = math.radians(90)

cube("left embroidered coat panel", (-0.42, -0.08, 1.18), (0.18, 0.08, 0.72), black_cloth).rotation_euler[2] = math.radians(-10)
cube("right embroidered coat panel", (0.42, -0.08, 1.18), (0.18, 0.08, 0.72), black_cloth).rotation_euler[2] = math.radians(10)
torus("purple waist sash", (0, -0.02, 1.44), 0.58, 0.035, purple).scale.y = 0.55

left_arm = cylinder("left arm", (-0.72, -0.08, 1.45), 0.09, 0.7, fur)
left_arm.rotation_euler[1] = math.radians(-55)
right_arm = cylinder("right arm", (0.72, -0.08, 1.45), 0.09, 0.7, fur)
right_arm.rotation_euler[1] = math.radians(55)
sphere("left paw", (-1.0, -0.22, 1.24), (0.18, 0.14, 0.18), fur)
sphere("right paw", (1.0, -0.22, 1.24), (0.18, 0.14, 0.18), fur)

cube("left sneaker", (-0.34, -0.12, 0.35), (0.28, 0.42, 0.13), black_cloth)
cube("right sneaker", (0.34, -0.12, 0.35), (0.28, 0.42, 0.13), black_cloth)
cube("left sneaker sole", (-0.34, -0.16, 0.25), (0.30, 0.45, 0.055), sole)
cube("right sneaker sole", (0.34, -0.16, 0.25), (0.30, 0.45, 0.055), sole)

tail = cylinder("curved tail placeholder", (0.72, 0.34, 0.98), 0.08, 0.95, fur)
tail.rotation_euler[0] = math.radians(35)
tail.rotation_euler[1] = math.radians(-35)

torus("oversized gold chain", (0, -0.48, 1.78), 0.48, 0.035, gold).rotation_euler[0] = math.radians(72)
sphere("purple chest gem", (0, -0.78, 1.72), (0.12, 0.04, 0.16), purple)
torus("forehead gold sigil", (0, -0.90, 3.05), 0.11, 0.01, gold).rotation_euler[0] = math.radians(90)

blade = cube("realm blade purple gold", (-1.34, -0.62, 1.02), (0.08, 0.10, 1.05), purple)
blade.rotation_euler[1] = math.radians(-35)
blade.rotation_euler[2] = math.radians(-25)
torus("realm blade guard", (-1.0, -0.45, 1.42), 0.18, 0.025, gold).rotation_euler[1] = math.radians(55)

cylinder("black gold platform", (0, 0, 0.08), 1.45, 0.16, black_cloth, vertices=96)
torus("platform gold trim", (0, 0, 0.18), 1.45, 0.025, gold)
for i, radius in enumerate([1.25, 1.65, 2.05]):
    aura = torus(f"purple realm aura ring {i + 1}", (0, 0, 0.45 + i * 0.45), radius, 0.012, purple)
    aura.rotation_euler[0] = math.radians(90)
    aura.rotation_euler[2] = math.radians(i * 20)

bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0.25))
armature = bpy.context.object
armature.name = "Lee-Wuh_Rig_Starter"
bones = armature.data.edit_bones
root = bones[0]
root.name = "root"
root.head = (0, 0, 0.25)
root.tail = (0, 0, 1.1)
spine = bones.new("spine")
spine.head = (0, 0, 1.1)
spine.tail = (0, 0, 2.05)
spine.parent = root
head_bone = bones.new("head")
head_bone.head = (0, 0, 2.05)
head_bone.tail = (0, 0, 3.25)
head_bone.parent = spine
for side, x in [("L", -0.55), ("R", 0.55)]:
    arm = bones.new(f"{side}_arm")
    arm.head = (x * 0.7, 0, 1.65)
    arm.tail = (x * 1.45, -0.12, 1.2)
    arm.parent = spine
    leg = bones.new(f"{side}_leg")
    leg.head = (x * 0.45, 0, 0.95)
    leg.tail = (x * 0.55, -0.1, 0.25)
    leg.parent = root
bpy.ops.object.mode_set(mode="OBJECT")

mesh_objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in mesh_objs:
    o.select_set(True)
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
try:
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
except Exception:
    bpy.ops.object.parent_set(type="ARMATURE")

bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 96
for frame, scale in [(1, 1.0), (48, 1.035), (96, 1.0)]:
    bpy.context.scene.frame_set(frame)
    body.scale = (0.72, 0.52, 0.82 * scale)
    head.location.z = 2.55 + (scale - 1.0) * 0.18
    body.keyframe_insert(data_path="scale")
    head.keyframe_insert(data_path="location")

for obj in [left_iris, right_iris]:
    original_x = obj.scale.x
    for frame, sx in [(1, original_x), (45, original_x), (48, original_x * 0.12), (51, original_x), (96, original_x)]:
        bpy.context.scene.frame_set(frame)
        obj.scale.x = sx
        obj.keyframe_insert(data_path="scale")

bpy.ops.object.light_add(type="AREA", location=(0, -4.5, 5.2))
key = bpy.context.object
key.name = "large cinematic softbox"
key.data.energy = 900
key.data.size = 5.5
bpy.ops.object.light_add(type="POINT", location=(-2.8, -2.0, 2.6))
rim = bpy.context.object
rim.name = "purple rim aura"
rim.data.color = (0.55, 0.2, 1.0)
rim.data.energy = 420
bpy.ops.object.camera_add(location=(0, -6.3, 2.35), rotation=(math.radians(74), 0, 0))
bpy.context.scene.camera = bpy.context.object
bpy.context.scene.render.resolution_x = 1600
bpy.context.scene.render.resolution_y = 900

os.makedirs(OUTPUT_BLEND_DIR, exist_ok=True)
os.makedirs(OUTPUT_GLB_DIR, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
bpy.ops.export_scene.gltf(filepath=OUTPUT_GLB, export_format="GLB", export_animations=True, export_apply=True)
print(f"Saved Blender file to {OUTPUT_BLEND}")
print(f"Exported GLB to {OUTPUT_GLB}")
