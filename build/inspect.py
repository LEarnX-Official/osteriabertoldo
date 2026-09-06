import bpy, sys
print("=== OBJECTS ===")
for o in bpy.data.objects:
    print(f"{o.name:28s} {o.type:8s} verts={len(o.data.vertices) if o.type=='MESH' else '-'} mats={[m.name for m in o.data.materials] if o.type=='MESH' and o.data.materials else []}")
print("=== SCENE ===")
sc=bpy.context.scene
print("engine:", sc.render.engine, "res:", sc.render.resolution_x, sc.render.resolution_y)
print("world:", sc.world.name if sc.world else None)
