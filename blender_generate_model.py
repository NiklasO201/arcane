import bpy
import sys

argv = sys.argv
object_name = " ".join(argv[argv.index("--")+1:]) if "--" in argv else "Unbekannt"

# Lösche alle Standardobjekte
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Karosserie
bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,0))
car_body = bpy.context.object
car_body.name = "Karosserie"
mat_body = bpy.data.materials.new(name="KarosserieMaterial")
car_body.data.materials.append(mat_body)

# Motor
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,1))
engine = bpy.context.object
engine.name = "Motor"
mat_engine = bpy.data.materials.new(name="MotorMaterial")
engine.data.materials.append(mat_engine)

# Innenraum
bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0.5,0.5,0.5))
interior = bpy.context.object
interior.name = "Innenraum"
mat_interior = bpy.data.materials.new(name="InnenraumMaterial")
interior.data.materials.append(mat_interior)

# Export als GLB
bpy.ops.export_scene.gltf(filepath="model.glb", export_format='GLB', export_materials='EXPORT')
print(f"{object_name} Modell erstellt")