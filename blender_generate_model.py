import bpy
import sys
argv = sys.argv
object_name = " ".join(argv[argv.index("--")+1:]) if "--" in argv else "Unbekannt"

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,0))
car_body = bpy.context.object
car_body.name = "Karosserie"

bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,1))
engine = bpy.context.object
engine.name = "Motor"

bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0.5,0.5,0.5))
interior = bpy.context.object
interior.name = "Innenraum"

bpy.ops.export_scene.gltf(filepath="model.glb", export_format='GLB', export_materials='EXPORT')
print(f"{object_name} Modell erstellt")
