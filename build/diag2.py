import bpy, sys, os, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import studio as ST, detail as DT
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST.purge_scene()
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,"models","dish_risotto.glb"))
r=[o for o in bpy.data.objects if o.name=='Risotto'][0]
s=DT._surface_samples(r, 3000, seed=1, min_z_frac=0.05)
print("samples:",len(s))
# radial distribution
import mathutils
ctr=sum((p for p,_,_ in s), mathutils.Vector())/len(s)
rad=[ (p-ctr).xy.length for p,_,_ in s]
rmax=max(rad)
h=collections.Counter(round(x/rmax,1) for x in rad)
print("radial histogram (0=centre,1=rim):", dict(sorted(h.items())))
# also raw mesh radial face distribution
zs=[(r.matrix_world@v.co).z for v in r.data.vertices]
print("mesh z range",min(zs),max(zs))
h2=collections.Counter()
for p in r.data.polygons:
    n=(r.matrix_world.to_3x3()@p.normal).normalized()
    c=r.matrix_world@p.center
    h2[(round(c.xy.length/0.075,1), n.z>0.10)] += 1
ups=collections.Counter()
for (rr,up),c in h2.items():
    if up: ups[rr]+=c
print("upward faces by radius:", dict(sorted(ups.items())))
