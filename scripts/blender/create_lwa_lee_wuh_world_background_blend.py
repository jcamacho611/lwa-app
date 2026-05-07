
import bpy
import math
import random
from math import radians, sin, cos, pi

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def mat(name, color, metallic=0, roughness=.35, emission=None, strength=0, alpha=1):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.blend_method = 'BLEND' if alpha < 1 else 'OPAQUE'
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Alpha"].default_value = alpha
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = strength
    return m

realm_black = mat("Deep Realm Black", (0.018, 0.016, 0.026, 1), .1, .55)
dark_purple = mat("Dark Purple Atmosphere", (0.07, 0.025, 0.13, 1), 0, .68)
purple = mat("Purple Realm Energy", (0.42, 0.04, 0.95, 1), 0, .16, (0.45, 0.02, 1, 1), 1.35)
gold = mat("Ancient Gold Trim", (0.92, 0.62, 0.18, 1), 1, .22)
stone = mat("Black Stone Platform", (0.045, 0.04, 0.052, 1), .08, .58)
mist = mat("Soft Purple Mist", (0.28, 0.12, 0.52, .45), 0, .45, (0.22, 0.04, .55, 1), .35, .45)

def cube(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    return o

def cyl(name, loc, radius, depth, material, verts=96, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def sphere(name, loc, radius, material, segments=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=max(8, segments//2), radius=radius, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

def cone_obj(name, loc, radius, depth, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=radius, radius2=0, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o

# Background/world layer only: no character, no sword.
cube("Deep Black Purple World Backdrop", (0, 2.2, 3.0), (11.5, .18, 6.5), dark_purple)

# Floating platform
cyl("Floating Black Stone Realm Platform", (0, -0.4, 0), 3.2, .18, stone)
for i, r in enumerate([3.05, 2.25, 1.35]):
    cyl(f"Engraved Gold Platform Ring {i+1}", (0, -0.4, .12 + i*.035), r, .04, gold)
    cyl(f"Dark Inner Ring Mask Proxy {i+1}", (0, -0.4, .16 + i*.035), r-.06, .06, stone)

cyl("Purple Center Portal Pool", (0, -0.4, .27), 1.1, .045, purple)

# Portal pillars and arch
for label, x in [("Left", -2.05), ("Right", 2.05)]:
    cyl(f"{label} Black Gold Realm Pillar", (x, .8, 1.9), .22, 3.7, stone, 48)
    cyl(f"{label} Gold Pillar Top Cap", (x, .8, 3.85), .34, .22, gold, 48)
    cyl(f"{label} Gold Pillar Bottom Cap", (x, .8, .18), .34, .22, gold, 48)

for i in range(18):
    t = pi * i / 17
    x = 2.05 * cos(t)
    z = 3.55 + .85 * sin(t)
    sphere(f"Gold Portal Arch Segment {i+1}", (x, .8, z), .16, gold)

# Purple portal energy
for i in range(34):
    t = i / 33
    ang = t * pi * 6
    r = .35 + .75 * sin(pi*t)
    x = cos(ang) * r
    z = .45 + t * 3.4
    y = .76 + .04 * sin(ang)
    sphere(f"Vertical Purple Portal Energy {i+1}", (x, y, z), .05 + .055 * sin(pi*t), purple, 24)

# Floating crystals/sigils
for i in range(20):
    ang = 2*pi*i/20
    radius = 3.3 + .7 * sin(i)
    x = cos(ang) * radius
    y = 1.35 + .1 * sin(i * 1.7)
    z = 1.5 + 2.8 * (.5 + .5 * sin(ang + .8))
    cone_obj(f"Floating Realm Crystal {i+1}", (x, y, z), .09 + .04*(i%3), .45 + .16*(i%4), gold if i%2==0 else purple, (radians(20), 0, ang))

# Mist and atmosphere
random.seed(7)
for i in range(44):
    x = random.uniform(-4.8, 4.8)
    y = random.uniform(-.9, 1.3)
    z = random.uniform(.18, 1.25)
    sphere(f"Soft Purple Realm Mist {i+1}", (x, y, z), random.uniform(.12, .38), mist, 16)

for i in range(80):
    x = random.uniform(-5.2, 5.2)
    y = 2.05
    z = random.uniform(.8, 6.0)
    sphere(f"Background Gold Purple Star Speck {i+1}", (x, y, z), random.uniform(.018, .055), gold if i%3==0 else purple, 12)

# Lighting and camera
bpy.ops.object.light_add(type='AREA', location=(0, -3.8, 5.5))
key = bpy.context.object
key.name = "Large Realm Softbox"
key.data.energy = 850
key.data.size = 7

bpy.ops.object.light_add(type='POINT', location=(0, .4, 1.1))
portal_light = bpy.context.object
portal_light.name = "Purple Portal Light"
portal_light.data.energy = 520
portal_light.data.color = (0.55, 0.1, 1.0)

bpy.ops.object.camera_add(location=(0, -7.8, 3.2), rotation=(radians(68), 0, 0))
bpy.context.scene.camera = bpy.context.object

# Render settings: full world background, not transparent by default.
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 96
bpy.context.scene.render.film_transparent = False
bpy.context.scene.view_settings.view_transform = 'Filmic'
bpy.context.scene.view_settings.look = 'Medium High Contrast'

bpy.ops.wm.save_as_mainfile(filepath="//lwa_lee_wuh_world_background_no_character_no_sword.blend")
