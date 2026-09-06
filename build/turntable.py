"""
Render a photoreal 36-frame turntable for one asset.
Usage: blender -b -P turntable.py -- --asset dish_risotto --frames 36 --res 512
"""
import bpy, sys, os, math, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shading as SH
import studio as ST
import detail as DT
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Per-asset overrides. White porcelain against a dark room clips easily;
# deep bowls trap light and need less key than flat plates.
ASSET_CFG = {
    'dish_risotto': dict(key=125.0, exposure=-0.35),
    'dish_scoglio': dict(key=78.0,  exposure=-1.30, world=0.32),
    'dish_tonno':   dict(key=88.0,  exposure=-1.15, world=0.36),
    'dish_tartare': dict(key=95.0,  exposure=-1.00, world=0.38),
    'dish_porcini': dict(key=100.0, exposure=-0.85, world=0.42),
    'dish_bisque':  dict(key=88.0,  exposure=-1.10, world=0.36),
    'dish_dolce':   dict(key=88.0,  exposure=-1.15, world=0.36),
    'wineglass':    dict(key=150.0, exposure=-0.20, world=0.55),
    'pendant_lamp': dict(key=60.0,  exposure=-0.30, world=0.30),
    'monogram':     dict(key=140.0, exposure=-0.20, world=0.60),
}

def argv():
    a = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--asset", required=True)
    p.add_argument("--frames", type=int, default=36)
    p.add_argument("--res", type=int, default=512)
    p.add_argument("--samples", type=int, default=256)
    p.add_argument("--elev", type=float, default=34.0)
    p.add_argument("--out", default=None)
    p.add_argument("--single", type=int, default=-1, help="render only this frame index")
    p.add_argument("--nogpu", action="store_true")
    return p.parse_args(a)

# --------------------------------------------------- material assignment
# Map source GLB/blend material names onto the procedural shaders.
def assign_materials(objs):
    import re
    cache = {}
    def get(key, fn, *a, **kw):
        if key not in cache: cache[key] = fn(*a, **kw)
        return cache[key]

    for o in objs:
        if o.type != 'MESH' or not o.data.materials: continue
        for i, src in enumerate(o.data.materials):
            if src is None: continue
            n = src.name
            # carry the authored base colour through as the tint, so the
            # procedural shader keeps the art direction of the original
            tint = (0.7, 0.6, 0.5)
            try:
                b = src.node_tree.nodes.get("Principled BSDF")
                if b: tint = tuple(b.inputs['Base Color'].default_value)[:3]
            except Exception: pass

            # Order matters: more specific patterns first.
            if re.search(r'porcelain|glaze|bowl|plate', n, re.I):
                m = get('porc', SH.porcelain)
            elif re.search(r'crystal', n, re.I):
                m = get('cry', SH.crystal)
            elif re.search(r'risotto', n, re.I):
                m = get('ris', SH.risotto, sauce=tint)
            elif re.search(r'^wine$|amarone', n, re.I):
                m = get('wine', SH.wine, col=tint)
            elif re.search(r'prawn|shrimp|gambero', n, re.I):
                m = get('prawn', SH.prawn)
            elif re.search(r'mussel', n, re.I):
                m = get('mus', SH.nacre)
            elif re.search(r'clam|vongole', n, re.I):
                m = get('clam', SH.clamshell)
            elif re.search(r'porcini|mushroom|funghi', n, re.I):
                m = get('porcini', SH.mushroom, cap=tint)
            elif re.search(r'truffle|tartufo', n, re.I):
                m = get('truf', SH.truffle)
            elif re.search(r'tuna|tonno|salmon', n, re.I):
                m = get('tuna', SH.raw_fish, flesh=tint)
            elif re.search(r'beef|manzo|tartare', n, re.I):
                m = get('beef', SH.beef_tartare, tint=tint)
            elif re.search(r'sesame', n, re.I):
                m = get('ses', SH.seed)
            elif re.search(r'onion|scallion|shallot', n, re.I):
                m = get('onion', SH.allium, tint=tint)
            elif re.search(r'grana|parmes|pecorino|cheese', n, re.I):
                m = get('grana', SH.hard_cheese)
            elif re.search(r'cherry|berry|amarena', n, re.I):
                m = get('cherry', SH.berry, tint=tint)
            elif re.search(r'cream|panna|gelato|custard', n, re.I):
                m = get('cream', SH.cream, tint=tint)
            elif re.search(r'crumb|pistachio|nut|praline', n, re.I):
                m = get('crumb'+n, SH.crumb, name="Crumb_"+n, tint=tint)
            elif re.search(r'bisque|soup|broth|zuppa', n, re.I):
                m = get('bisque', SH.bisque, tint=tint)
            elif re.search(r'tagliatelle|tagliolini|pasta|spaghetti|noodle', n, re.I):
                m = get('pasta'+n, SH.pasta, name="Pasta_"+n, tint=tint)
            elif re.search(r'parsley|herb|basil|rocket|leaf|mint|celery', n, re.I):
                m = get('herb'+n, SH.herb, name="Herb_"+n, tint=tint)
            elif re.search(r'brass|bronze|copper', n, re.I):
                m = get('brass', SH.brass)
            elif re.search(r'gold', n, re.I):
                m = get('gold', SH.gold)
            elif re.search(r'glow|bulb|emis', n, re.I):
                m = get('bulb', SH.emissive)
            elif re.search(r'cord|wire|rope', n, re.I):
                m = get('cord', SH.generic_food, "Cord_PR", (0.05,0.04,0.035), 0.55, 0.0)
            else:
                m = get('gen'+n, SH.generic_food, "Food_"+n, tint)
            o.data.materials[i] = m

# --------------------------------------------------- geometry refinement
def refine(objs, span=1.0):
    """Subdivide + micro-displace food surfaces. Displacement is expressed
    as a FRACTION OF THE SUBJECT SPAN, so it stays grain-sized whatever
    scale the source model happens to import at."""
    import re
    food_re = r'risotto|prawn|pasta|tagliatelle|herb|parsley|food|tartare|tonno|porcini|dolce|bisque|sauce|cream|meat|fish'
    for o in objs:
        if o.type != 'MESH': continue
        names = " ".join(m.name for m in o.data.materials if m)
        is_food = re.search(food_re, names + " " + o.name, re.I)
        is_hard = re.search(r'porcelain|glaze|bowl|plate|crystal|glass|brass|gold|cord|bulb|shell', names, re.I)

        for p in o.data.polygons: p.use_smooth = True

        if is_food and not is_hard:
            sub = o.modifiers.new("Sub", 'SUBSURF')
            sub.levels = 1; sub.render_levels = 2
            disp = o.modifiers.new("MicroDisp", 'DISPLACE')
            tex = bpy.data.textures.new(f"disp_{o.name}", 'CLOUDS')
            tex.noise_scale = span * 0.035        # relative to subject size
            tex.noise_depth = 5
            disp.texture = tex
            disp.strength = span * 0.006          # subtle lumpiness only
            disp.mid_level = 0.5
        elif is_hard:
            sub = o.modifiers.new("Sub", 'SUBSURF')
            sub.levels = 1; sub.render_levels = 2

# ------------------------------------------------ per-dish detail recipes
def add_detail(objs, asset, span):
    """Scatter real geometry where a shader alone cannot do the job."""
    import re
    by_mat = {}
    for o in objs:
        if o.type != 'MESH': continue
        for m in o.data.materials:
            if m: by_mat.setdefault(m.name.lower(), []).append(o)

    def find(pat):
        for k, v in by_mat.items():
            if re.search(pat, k, re.I): return v[0]
        return None

    def hide(o):
        """Placeholder garnish (3 green spheres) is replaced by real leaves."""
        if o is None: return
        o.hide_render = True
        o.hide_viewport = True

    made = []
    if asset == 'dish_risotto':
        base = find(r'risotto')
        if base:
            # Two layers: a dense bed that hides the smooth dome entirely,
            # then a looser proud layer that breaks the silhouette.
            gm = SH.risotto("RiceGrain_PR")
            bed = DT.scatter_grains(base, count=5200, mat=gm, seed=11,
                                    sink=0.55, min_z=0.02, grain_scale=1.35,
                                    name="GrainBed")
            if bed: made.append(bed)
            top = DT.scatter_grains(base, count=2400, mat=gm, seed=27,
                                    sink=-0.10, min_z=0.02, grain_scale=1.5,
                                    jitter=0.9, name="GrainTop")
            if top: made.append(top)
            leaves = DT.scatter_leaves(base, count=16, mat=SH.herb("Parsley_PR2"),
                                       seed=5, min_z=0.30)
            if leaves: made.append(leaves)
        hide(find(r'parsley'))
    elif asset == 'dish_scoglio':
        base = find(r'tagliatelle|pasta')
        if base:
            leaves = DT.scatter_leaves(base, count=20, mat=SH.herb("Herb_S"),
                                       seed=7, min_z=0.25)
            if leaves: made.append(leaves)
        hide(find(r'^herbs_m$|^herbs'))
    else:
        base = find(r'risotto|pasta|food|cream|meat|fish|tartare|tonno|porcini|bisque|dolce')
        if base:
            leaves = DT.scatter_leaves(base, count=12, mat=SH.herb("Herb_G"),
                                       seed=9, min_z=0.30)
            if leaves: made.append(leaves)
        hide(find(r'parsley|^herbs'))
    return made

def import_asset(name):
    glb = os.path.join(ROOT, "models", f"{name}.glb")
    blend = os.path.join(ROOT, "models", f"{name}.blend")
    before = set(bpy.data.objects)
    if os.path.exists(blend):
        with bpy.data.libraries.load(blend) as (src, dst):
            dst.objects = [o for o in src.objects]
        for o in dst.objects:
            if o: bpy.context.collection.objects.link(o)
    elif os.path.exists(glb):
        bpy.ops.import_scene.gltf(filepath=glb)
    else:
        raise SystemExit(f"no model for {name}")
    return [o for o in bpy.data.objects if o not in before]

def _bounds(objs, mw=True):
    import mathutils
    pts = []
    for o in objs:
        if o.type != 'MESH': continue
        for c in o.bound_box:
            pts.append(o.matrix_world @ mathutils.Vector(c))
    return pts

def food_span(objs):
    """Span of the FOOD only, ignoring the plate. Framing on the plate makes
    a small portion on a large charger read as a speck; framing on the food
    keeps every dish filling the card consistently."""
    import re, mathutils
    food = []
    for o in objs:
        if o.type != 'MESH' or not o.data.materials: continue
        names = " ".join(m.name for m in o.data.materials if m)
        if re.search(r'porcelain|glaze|bowl|plate', names, re.I): continue
        food.append(o)
    pts = _bounds(food)
    if not pts: return None
    xs=[p.x for p in pts]; ys=[p.y for p in pts]; zs=[p.z for p in pts]
    return (max(max(xs)-min(xs), max(ys)-min(ys)),
            max(zs)-min(zs), (min(zs)+max(zs))/2)

def fit_and_ground(objs):
    """Normalise size and sit the asset on the table at origin."""
    import mathutils
    pts = []
    deps = bpy.context.evaluated_depsgraph_get()
    for o in objs:
        if o.type != 'MESH': continue
        for c in o.bound_box:
            pts.append(o.matrix_world @ mathutils.Vector(c))
    if not pts: return 1.0, 0.1, 0.3
    xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
    cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    span = max(max(xs)-min(xs), max(ys)-min(ys)) or 0.2
    S = 0.30 / span                      # normalise to a 30cm plate
    pivot = bpy.data.objects.new("Pivot", None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = (0, 0, 0)
    for o in objs:
        if o.parent is None:
            o.parent = pivot
            o.matrix_parent_inverse = pivot.matrix_world.inverted()
    pivot.scale = (S, S, S)
    pivot.location = (-cx*S, -cy*S, -min(zs)*S)
    bpy.context.view_layer.update()
    height = (max(zs)-min(zs))*S
    return S, height, span*S

def main():
    a = argv()
    ST.purge_scene()
    objs = import_asset(a.asset)
    assign_materials(objs)
    S, height, span = fit_and_ground(objs)
    fs = food_span(objs)
    # Frame between the food and the plate: mostly the food, but never so
    # tight that the plate rim gets cropped awkwardly.
    frame_span = span
    if fs and fs[0] > 1e-6:
        frame_span = min(span, max(fs[0] * 1.85, span * 0.55))
    print(f"[fit] scale={S:.4f} height={height:.4f} span={span:.4f} "
          f"food={fs[0] if fs else 0:.4f} frame={frame_span:.4f}")
    refine(objs, span=span)
    extra = add_detail(objs, a.asset, span)
    print(f"[detail] added {len(extra)} scatter objects")

    cfg = ASSET_CFG.get(a.asset, {})
    ST.world_interior(strength=cfg.get('world', 0.50))
    ST.foodlight(scale=1.0, key=cfg.get('key', 125.0))
    ST.ground(scale=1.0, catcher=True)

    # Frame from the real bounding cylinder so the WHOLE subject fits at
    # every rotation. Tall subjects (the glass) and wide ones (plates) need
    # different distances; solving both axes and taking the max handles it.
    tgt_z = height * 0.52
    lens, sensor = 85.0, 36.0
    half_fov = math.atan(sensor / (2*lens))          # horizontal half-angle
    R = frame_span * 0.5                              # rotation radius
    # vertical extent about the look-at point, plus the radius for safety
    v_half = max(height - tgt_z, tgt_z) + R*math.sin(math.radians(a.elev))
    d_h = R / math.tan(half_fov) + R
    d_v = v_half / math.tan(half_fov) + R
    dist = max(d_h, d_v) * 1.18                       # margin
    cam, tgt = ST.camera(target=(0, 0, tgt_z), dist=dist, elev_deg=a.elev,
                         lens=lens, sensor=sensor, fstop=5.6)
    sc = ST.cycles(res=a.res, samples=a.samples, transparent=True, gpu=not a.nogpu)
    sc.view_settings.exposure = cfg.get('exposure', 0.0)

    outdir = a.out or os.path.join(ROOT, "renders", a.asset)
    os.makedirs(outdir, exist_ok=True)

    pivot = bpy.data.objects.get("Pivot")
    frames = range(a.frames) if a.single < 0 else [a.single]
    for i in frames:
        ang = (i / a.frames) * 2 * math.pi
        pivot.rotation_euler = (0, 0, ang)
        bpy.context.scene.render.filepath = os.path.join(outdir, f"{i:03d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[frame] {a.asset} {i+1}/{a.frames}")

    with open(os.path.join(outdir, "meta.json"), "w") as f:
        json.dump({"asset": a.asset, "frames": a.frames, "res": a.res,
                   "elev": a.elev, "height": height}, f)
    print("[done]", outdir)

main()
