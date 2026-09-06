import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import studio as ST
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST.purge_scene()
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,"models","dish_risotto.glb"))
for o in bpy.data.objects:
    if o.type!='MESH': continue
    zs=[(o.matrix_world @ v.co).z for v in o.data.vertices]
    ns=[ (o.matrix_world.to_3x3() @ p.normal).normalized().z for p in o.data.polygons]
    up=[n for n in ns if n>0.12]
    print(f"{o.name:14s} verts={len(o.data.vertices):5d} polys={len(o.data.polygons):5d} "
          f"z=[{min(zs):+.4f},{max(zs):+.4f}] span={max(zs)-min(zs):.4f} upfaces={len(up)}/{len(ns)}")
    # distribution of upward faces by height fraction
    zmin,zmax=min(zs),max(zs); sp=max(zmax-zmin,1e-6)
    import collections
    hist=collections.Counter()
    for p in o.data.polygons:
        n=(o.matrix_world.to_3x3()@p.normal).normalized()
        if n.z<0.12: continue
        c=(o.matrix_world@p.center).z
        hist[round((c-zmin)/sp,1)]+=1
    print("   up-face height histogram:", dict(sorted(hist.items())))
