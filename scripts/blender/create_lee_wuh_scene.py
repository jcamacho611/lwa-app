import bpy
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# Materials
def mat(name, color):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    return material

fur = mat("Lee-Wuh warm dark fur", (0.18, 0.10, 0.06, 1))
gold = mat("Royal gold jewelry", (0.95, 0.62, 0.12, 1))
purple = mat("Purple aura cloth", (0.34, 0.14, 0.92, 1))
black = mat("Black streetwear armor", (0.02, 0.02, 0.025, 1))
cream = mat("Soft muzzle", (0.82, 0.62, 0.42, 1))

def add_uv_sphere(name, location, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj

def add_cube(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj

# Chibi body blockout
head = add_uv_sphere("Oversized chibi head", (0, 0, 2.8), (1.05, 0.92, 0.95), fur)
body = add_uv_sphere("Small hoodie body", (0, 0, 1.35), (0.78, 0.55, 0.9), black)
muzzle = add_uv_sphere("Soft cute muzzle", (0, -0.78, 2.65), (0.42, 0.18, 0.25), cream)

# Eyes
left_eye = add_uv_sphere("Left big anime eye", (-0.35, -0.82, 2.95), (0.13, 0.05, 0.18), purple)
right_eye = add_uv_sphere("Right big anime eye", (0.35, -0.82, 2.95), (0.13, 0.05, 0.18), purple)

# Dreadlocks as stylized tubes/cylinders
for i, x in enumerate([-0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75]):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.08, depth=1.45, location=(x, 0.28, 2.35))
    dread = bpy.context.object
    dread.name = f"Jeweled dreadlock {i+1}"
    dread.rotation_euler[0] = 0.35
    dread.data.materials.append(fur)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.09, minor_radius=0.015, location=(x, 0.05, 2.0))
    bead = bpy.context.object
    bead.name = f"Gold dread bead {i+1}"
    bead.data.materials.append(gold)

# Arms / legs
add_uv_sphere("Left paw glove", (-0.9, -0.05, 1.25), (0.22, 0.18, 0.22), fur)
add_uv_sphere("Right paw glove", (0.9, -0.05, 1.25), (0.22, 0.18, 0.22), fur)
add_cube("Left sneaker", (-0.35, -0.1, 0.35), (0.28, 0.45, 0.14), black)
add_cube("Right sneaker", (0.35, -0.1, 0.35), (0.28, 0.45, 0.14), black)

# Jewelry / chain
bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.035, location=(0, -0.35, 1.95))
chain = bpy.context.object
chain.name = "Oversized final-boss gold chain"
chain.rotation_euler[0] = 1.2
chain.data.materials.append(gold)

# LEE-WUH chest plate
bpy.ops.object.text_add(location=(-0.48, -0.62, 1.55), rotation=(1.35, 0, 0))
text = bpy.context.object
text.name = "LEE-WUH chest text"
text.data.body = "LEE-WUH"
text.data.align_x = "LEFT"
text.data.size = 0.22
text.data.materials.append(gold)

# Aura rings
for z, radius in [(0.9, 1.4), (1.65, 1.75), (2.45, 1.35)]:
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=0.012, location=(0, 0, z))
    aura = bpy.context.object
    aura.name = f"Purple/gold aura ring {z}"
    aura.data.materials.append(purple)

# Camera / light
bpy.ops.object.light_add(type="AREA", location=(0, -4, 5))
light = bpy.context.object
light.name = "Softbox key light"
light.data.energy = 700
light.data.size = 5

bpy.ops.object.camera_add(location=(0, -6, 2.5), rotation=(1.25, 0, 0))
bpy.context.scene.camera = bpy.context.object

# Set origin view and render resolution
bpy.context.scene.render.resolution_x = 1600
bpy.context.scene.render.resolution_y = 900

# Save file
bpy.ops.wm.save_as_main_file(filepath="/Users/bdm/LWA/lwa-app/brand-source/lee-wuh/lee-wuh-character-blockout.blend")
