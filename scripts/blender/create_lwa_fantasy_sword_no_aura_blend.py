
import bpy
from mathutils import Vector
from math import radians, sin, pi

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Materials
def mat_principled(name, color, metallic=0.0, roughness=0.35, emission=None, strength=0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = strength
    return m

gold = mat_principled("Ancient Blackened Gold", (0.95, 0.62, 0.18, 1), 1, 0.22)
dark_gold = mat_principled("Engraved Dark Gold", (0.26, 0.14, 0.045, 1), 1, 0.28)
black = mat_principled("Wrapped Black Grip", (0.015, 0.012, 0.011, 1), 0.4, 0.32)
purple = mat_principled("Purple Gemstone", (0.42, 0.03, 0.95, 1), 0.2, 0.08, (0.34, 0.0, 0.9, 1), 0.8)
steel = mat_principled("Polished Dark Steel Edge", (0.62, 0.56, 0.47, 1), 1, 0.18)

# Blade mesh
L = 6.2
n = 38
verts = []
faces = []
for i in range(n):
    t = i / (n - 1)
    x = -L/2 + t * L
    curve = -0.35 * sin(pi * t) + 0.08 * sin(2 * pi * t)
    width = 0.22 + 0.68 * (sin(pi * t) ** 0.9)
    width *= 0.55 + 0.45 * ((1 - t) ** 0.35)
    thick = 0.055 * (0.7 + 0.3 * sin(pi * t))
    verts += [(x, curve + width/2, thick), (x, curve - width/2, thick), (x, curve + width/2, -thick), (x, curve - width/2, -thick)]
for i in range(n-1):
    a = 4*i
    b = 4*(i+1)
    faces += [(a,b,b+1),(a,b+1,a+1),(a+2,a+3,b+3),(a+2,b+3,b+2),(a,a+2,b+2),(a,b+2,b),(a+1,b+1,b+3),(a+1,b+3,a+3)]
faces += [(0,1,3),(0,3,2),(4*(n-1),4*(n-1)+2,4*(n-1)+3),(4*(n-1),4*(n-1)+3,4*(n-1)+1)]

mesh = bpy.data.meshes.new("ornate_curved_gold_blade_mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()
blade = bpy.data.objects.new("Ornate Curved Gold Blade", mesh)
bpy.context.collection.objects.link(blade)
blade.data.materials.append(gold)
blade.rotation_euler[2] = radians(-18)
bpy.context.view_layer.objects.active = blade
blade.select_set(True)
bpy.ops.object.shade_smooth()
blade.select_set(False)

# Helper primitives
def add_cube(name, loc, scale, material, rotz=-18):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0,0,radians(rotz)))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj

def add_cylinder(name, loc, radius, depth, material, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj

def add_sphere(name, loc, radius, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj

add_cube("Dark Engraved Blade Inlay", (-0.25, -0.03, 0.08), (5.2, 0.18, 0.075), dark_gold)
add_cube("Polished Lower Edge", (-0.25, -0.38, 0.11), (5.6, 0.055, 0.06), steel)

guard = add_cylinder("Ornate Crossguard Gold", (2.55, 0.15, 0.03), 0.13, 1.45, gold, (radians(90), 0, radians(-18)))
for dy in [-0.72, 0.72]:
    add_cylinder("Jagged Guard Spike", (2.55, dy, 0.03), 0.10, 0.52, gold, (radians(90), 0, radians(-18)))

handle = add_cylinder("Black Wrapped Handle", (3.25, 0.38, 0.03), 0.18, 1.35, black, (0, radians(90), radians(-18)))
add_sphere("Gold Pommel", (3.92, 0.58, 0.03), 0.28, gold)

for name, loc, radius in [
    ("Center Purple Gem", (2.55, 0.15, 0.24), 0.18),
    ("Pommel Purple Gem", (4.03, 0.60, 0.24), 0.12),
    ("Blade Purple Gem", (2.1, 0.05, 0.20), 0.10),
]:
    add_sphere(name, loc, radius, purple)

for i in range(10):
    t = 0.18 + (0.78-0.18) * i / 9
    x = -L/2 + t * L
    y = -0.02 - 0.35 * sin(pi * t)
    add_sphere(f"Raised Gold Engraving Stud {i+1}", (x, y, 0.16), 0.055, gold)

# Lighting, camera, transparent background
bpy.ops.object.light_add(type='AREA', location=(0, -4, 5))
light = bpy.context.object
light.name = "Large Softbox Reflection Light"
light.data.energy = 500
light.data.size = 6

bpy.ops.object.camera_add(location=(0, -8, 4), rotation=(radians(60), 0, 0))
bpy.context.scene.camera = bpy.context.object

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64
bpy.context.scene.render.film_transparent = True
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'

# Set origin/frame
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type == 'MESH')
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# Save true .blend
bpy.ops.wm.save_as_mainfile(filepath="//lwa_fantasy_sword_no_aura.blend")
