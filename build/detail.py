"""
Geometry detail generation — the part shading cannot fake.

You cannot shade your way into rice. A smooth dome with noise displacement
reads as minced meat because the SILHOUETTE is wrong: real risotto has
thousands of discrete grain edges catching light. This module scatters real
instanced geometry over the source surfaces.
"""
import bpy, math, random, bmesh
from mathutils import Vector, Euler

def _grain_mesh(name, rx, ry, rz, subdiv=1):
    """One rice grain: a squashed ellipsoid with a slight taper."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=1.0)
    for v in bm.verts:
        v.co.x *= rx; v.co.y *= ry; v.co.z *= rz
        # taper the ends so it's grain-shaped, not pill-shaped
        t = abs(v.co.y / ry) if ry else 0
        v.co.x *= (1.0 - 0.28*t*t)
        v.co.z *= (1.0 - 0.28*t*t)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return me

def _leaf_mesh(name, w=1.0, l=1.0):
    """A flat-parsley leaflet: three lobes, serrated edge, curled midrib.
    Built as a centre spine with left/right blade verts so it curls like a
    real leaf instead of reading as a floating disc."""
    me = bpy.data.meshes.new(name)
    verts, faces = [], []
    N = 13
    for i in range(N):
        t = i/(N-1)
        # three-lobed outline, pointed tip
        lobe = abs(math.sin(t*math.pi*3.0))**0.55
        base = math.sin(t*math.pi)**0.6
        hw = w * base * (0.45 + 0.55*lobe) * (1.0 - 0.30*t)
        y = (t - 0.5) * l
        # midrib sits lower, blade curls up at the edges
        curl = 0.16*l*(base**2)
        verts.append(Vector((0.0,  y, math.sin(t*math.pi)*0.04*l)))       # spine
        verts.append(Vector((-hw,  y, math.sin(t*math.pi)*0.04*l + curl)))
        verts.append(Vector(( hw,  y, math.sin(t*math.pi)*0.04*l + curl)))
    for i in range(N-1):
        a = i*3; b = (i+1)*3
        faces.append((a, a+1, b+1, b))     # left blade
        faces.append((a, b,   b+2, a+2))   # right blade
    me.from_pydata([v[:] for v in verts], [], faces)
    me.update()
    for p in me.polygons: p.use_smooth = True
    return me

def _surface_samples(obj, count, seed=0, top_only=True, min_z_frac=0.35):
    """Sample points on the upper surface of a mesh, area-weighted."""
    rng = random.Random(seed)
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps)
    me = ev.to_mesh()
    mw = obj.matrix_world
    tris = []
    me.calc_loop_triangles()
    # Height range is measured over UPWARD-FACING geometry only. Using all
    # vertices includes the underside/skirt, which drags zmin down and makes
    # min_z_frac reject the entire usable top surface.
    up_tris = []
    for t in me.loop_triangles:
        vs = [mw @ me.vertices[i].co for i in t.vertices]
        n = (mw.to_3x3() @ t.normal).normalized()
        if top_only and n.z < 0.10: continue
        up_tris.append((vs, n, sum(v.z for v in vs)/3))
    if not up_tris:
        ev.to_mesh_clear(); return []
    zcs = [t[2] for t in up_tris]
    zmin, zmax = min(zcs), max(zcs)
    span = max(zmax - zmin, 1e-9)
    for vs, n, zc in up_tris:
        if top_only and (zc - zmin)/span < min_z_frac: continue
        a = (vs[1]-vs[0]).cross(vs[2]-vs[0]).length * 0.5
        if a <= 0: continue
        tris.append((a, vs, n))
    ev.to_mesh_clear()
    if not tris: return []
    total = sum(t[0] for t in tris)
    cum, acc = [], 0.0
    for a, vs, n in tris:
        acc += a/total; cum.append((acc, vs, n))
    out = []
    for _ in range(count):
        r = rng.random()
        lo, hi = 0, len(cum)-1
        while lo < hi:
            mid = (lo+hi)//2
            if cum[mid][0] < r: lo = mid+1
            else: hi = mid
        _, vs, n = cum[lo]
        u, v = rng.random(), rng.random()
        if u+v > 1: u, v = 1-u, 1-v
        p = vs[0] + u*(vs[1]-vs[0]) + v*(vs[2]-vs[0])
        out.append((p, n, rng))
    return out

def scatter_grains(target, count=2600, grain_len=None, mat=None, seed=1,
                   jitter=0.55, sink=0.35, name="Grains", min_z=0.30, grain_scale=1.0):
    """Scatter rice grains over the top surface of `target`.
    Grains are real geometry joined into one mesh — instancing via a single
    joined object keeps the render fast while giving true silhouette detail."""
    dims = target.dimensions
    span = max(dims.x, dims.y)
    gl = (grain_len if grain_len else span * 0.030) * grain_scale
    rng = random.Random(seed)
    samples = _surface_samples(target, count, seed=seed, min_z_frac=min_z)
    if not samples: return None

    proto = _grain_mesh(name+"_proto", gl*0.30, gl*0.5, gl*0.27)
    bm = bmesh.new()
    for p, n, _ in samples:
        m = bmesh.new()
        m.from_mesh(proto)
        # orient mostly flat-ish but randomly rotated, tilted toward normal
        yaw = rng.uniform(0, math.tau)
        pitch = rng.gauss(0, 0.45)
        roll = rng.gauss(0, 0.5)
        e = Euler((pitch, roll, yaw), 'XYZ')
        s = rng.uniform(0.80, 1.25)
        for v in m.verts:
            v.co = v.co * s
            v.co.rotate(e)
            v.co += p + Vector((rng.gauss(0, gl*jitter*0.18),
                                rng.gauss(0, gl*jitter*0.18),
                                -gl*sink*rng.uniform(0.4, 1.0)))
        me_tmp = bpy.data.meshes.new("tmp")
        m.to_mesh(me_tmp); m.free()
        bm.from_mesh(me_tmp)
        bpy.data.meshes.remove(me_tmp)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    bpy.data.meshes.remove(proto)
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    if mat: o.data.materials.append(mat)
    o.parent = target.parent
    o.matrix_parent_inverse = target.matrix_parent_inverse.copy()
    return o

def scatter_leaves(target, count=26, size=None, mat=None, seed=3, name="Leaves", min_z=0.45):
    """Scatter small herb leaves over the top of the dish."""
    dims = target.dimensions
    span = max(dims.x, dims.y)
    sz = size if size else span * 0.085
    rng = random.Random(seed)
    samples = _surface_samples(target, count, seed=seed, min_z_frac=min_z)
    if not samples: return None
    proto = _leaf_mesh(name+"_proto", w=sz*0.55, l=sz)
    bm = bmesh.new()
    for p, n, _ in samples:
        m = bmesh.new(); m.from_mesh(proto)
        e = Euler((rng.gauss(0, 0.22), rng.gauss(0, 0.22), rng.uniform(0, math.tau)), 'XYZ')
        s = rng.uniform(0.7, 1.3)
        for v in m.verts:
            v.co = v.co * s
            v.co.rotate(e)
            v.co += p + Vector((0, 0, sz*0.06))
        me_tmp = bpy.data.meshes.new("tmpl")
        m.to_mesh(me_tmp); m.free()
        bm.from_mesh(me_tmp)
        bpy.data.meshes.remove(me_tmp)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    bpy.data.meshes.remove(proto)
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    if mat: o.data.materials.append(mat)
    o.parent = target.parent
    o.matrix_parent_inverse = target.matrix_parent_inverse.copy()
    return o

def add_sauce_pool(target, mat=None, name="Sauce", inset=0.90, drop=0.004):
    """A thin glossy sauce film hugging the food surface. Real plated food
    almost always has a wet layer; it's a major photographic cue."""
    deps = bpy.context.evaluated_depsgraph_get()
    ev = target.evaluated_get(deps)
    me = ev.to_mesh().copy()
    ev.to_mesh_clear()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.matrix_world = target.matrix_world.copy()
    o.scale = o.scale * inset
    sh = o.modifiers.new("Shrink", 'DISPLACE')
    sh.strength = drop
    if mat:
        o.data.materials.clear()
        o.data.materials.append(mat)
    o.parent = target.parent
    o.matrix_parent_inverse = target.matrix_parent_inverse.copy()
    return o
