"""
Food-photography lighting rig + Cycles render setup.

Real food photography: one large soft key slightly behind the subject
(backlight makes food glisten), a bounce card opposite to open shadows,
a subtle warm rim. Large area lights, not directionals — the softness of
the shadow edge is a huge part of why a render reads as a photograph.
"""
import bpy, math
from mathutils import Vector

def purge_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.lights,
                bpy.data.cameras, bpy.data.images):
        for b in list(blk):
            if b.users == 0:
                blk.remove(b)

def world_interior(strength=0.42, warm=(1.0, 0.62, 0.32), cool=(0.09, 0.10, 0.16)):
    """A procedural interior environment: warm lamp pool overhead, dark
    oxblood walls, cool spill from a window on one side. This is what the
    glass and glaze actually reflect — a flat gradient is why they looked
    like plastic before."""
    w = bpy.data.worlds.new("Interior")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); out.location = (600, 0)
    bg = nt.nodes.new('ShaderNodeBackground'); bg.location = (400, 0)
    bg.inputs['Strength'].default_value = strength
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

    tc = nt.nodes.new('ShaderNodeTexCoord'); tc.location = (-900, 0)
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); sep.location = (-700, 0)
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])

    # vertical gradient: floor -> wall -> warm ceiling pool
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.location = (-480, 120)
    el = ramp.color_ramp.elements
    while len(el) > 1: el.remove(el[-1])
    el[0].position = 0.0;  el[0].color = (0.020, 0.012, 0.010, 1)   # dark floor
    e = el.new(0.45); e.color = (*[c*0.30 for c in warm], 1)         # oxblood wall
    e = el.new(0.72); e.color = (*[c*0.42 for c in warm], 1)         # lamp falloff
    e = el.new(1.00); e.color = (warm[0]*1.15, warm[1]*0.95, warm[2]*0.70, 1)
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])

    # a cool "window" on -X so highlights have two colour temperatures.
    # Real rooms are never lit by one colour; this is a big realism cue.
    win = nt.nodes.new('ShaderNodeTexGradient'); win.location = (-700, -280)
    mapn = nt.nodes.new('ShaderNodeMapping'); mapn.location = (-880, -280)
    mapn.inputs['Rotation'].default_value = (0, math.radians(90), 0)
    nt.links.new(tc.outputs['Generated'], mapn.inputs['Vector'])
    nt.links.new(mapn.outputs['Vector'], win.inputs['Vector'])
    wramp = nt.nodes.new('ShaderNodeValToRGB'); wramp.location = (-480, -280)
    wl = wramp.color_ramp.elements
    while len(wl) > 1: wl.remove(wl[-1])
    wl[0].position = 0.55; wl[0].color = (0, 0, 0, 1)
    e = wl.new(1.0); e.color = (*cool, 1)
    nt.links.new(win.outputs['Fac'], wramp.inputs['Fac'])

    add = nt.nodes.new('ShaderNodeMixRGB'); add.location = (-200, 0)
    add.blend_type = 'ADD'; add.inputs['Fac'].default_value = 1.0
    nt.links.new(ramp.outputs['Color'], add.inputs['Color1'])
    nt.links.new(wramp.outputs['Color'], add.inputs['Color2'])
    nt.links.new(add.outputs['Color'], bg.inputs['Color'])
    return w

def _area(name, loc, rot, size, energy, color, shape='SQUARE', size_y=None):
    d = bpy.data.lights.new(name, 'AREA')
    d.shape = shape
    d.size = size
    if size_y is not None and shape in ('RECTANGLE', 'ELLIPSE'):
        d.size_y = size_y
    d.energy = energy
    d.color = color
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = rot
    bpy.context.collection.objects.link(o)
    return o

def foodlight(target_h=0.06, scale=1.0, key=140.0):
    """Classic three-quarter-backlit food setup, scaled to subject size."""
    s = scale
    lights = []
    # KEY: large softbox, high and BEHIND-left. Backlight = glisten.
    lights.append(_area("Key", (-0.55*s, 0.85*s, 1.15*s),
                        (math.radians(-38), math.radians(-18), math.radians(-150)),
                        1.6*s, key, (1.0, 0.90, 0.78), 'RECTANGLE', 1.1*s))
    # FILL: big dim bounce card, front-right, cooler and much weaker
    lights.append(_area("Fill", (1.05*s, -0.75*s, 0.42*s),
                        (math.radians(72), 0, math.radians(58)),
                        2.2*s, key*0.10, (0.82, 0.87, 1.0), 'RECTANGLE', 1.6*s))
    # RIM: tight warm kicker, low and behind-right, separates from background
    lights.append(_area("Rim", (0.95*s, 0.95*s, 0.30*s),
                        (math.radians(-78), 0, math.radians(135)),
                        0.5*s, key*0.32, (1.0, 0.74, 0.42)))
    # TOP: soft overhead ambience, mimics the pendant lamp pool
    lights.append(_area("Top", (0, 0, 1.9*s),
                        (0, 0, 0), 2.4*s, key*0.16, (1.0, 0.82, 0.62)))
    return lights

def ground(scale=1.0, color=(0.045, 0.030, 0.026), rough=0.42, catcher=False):
    """A dark table surface. Needed so the subject has something to cast
    onto and bounce off — floating in void never looks photographic."""
    bpy.ops.mesh.primitive_plane_add(size=14*scale, location=(0, 0, 0))
    p = bpy.context.object
    p.name = "Table"
    m = bpy.data.materials.new("Table_PR")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value = (*color, 1)
    # noisy roughness so the table reflection isn't a perfect mirror streak
    n = nt.nodes.new('ShaderNodeTexNoise'); n.location = (-600, -200)
    n.inputs['Scale'].default_value = 18.0
    n.inputs['Detail'].default_value = 8.0
    r = nt.nodes.new('ShaderNodeValToRGB'); r.location = (-380, -200)
    el = r.color_ramp.elements
    el[0].position = 0.35; el[0].color = (rough-0.14,)*3 + (1,)
    el[1].position = 0.72; el[1].color = (rough+0.16,)*3 + (1,)
    nt.links.new(n.outputs['Fac'], r.inputs['Fac'])
    nt.links.new(r.outputs['Color'], b.inputs['Roughness'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.location = (-160, -320)
    bump.inputs['Strength'].default_value = 0.10
    bump.inputs['Distance'].default_value = 0.004
    nt.links.new(n.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    p.data.materials.append(m)
    if catcher:
        # Shadow catcher: the plane still bounces light and receives the
        # contact shadow, but composites out to alpha so the PNG drops
        # cleanly onto whatever background the site uses.
        p.is_shadow_catcher = True
    return p

def camera(target=(0, 0, 0.05), dist=0.62, elev_deg=32.0, azim_deg=0.0,
           lens=85.0, sensor=36.0, fstop=None, focus_obj=None):
    """85mm is the food-photography default: compresses nicely, minimal
    distortion. A wide lens close-up is an instant CG tell."""
    cd = bpy.data.cameras.new("Cam")
    cd.lens = lens
    cd.sensor_width = sensor
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        if focus_obj is not None:
            cd.dof.focus_object = focus_obj
        else:
            cd.dof.focus_distance = dist
    cam = bpy.data.objects.new("Cam", cd)
    bpy.context.collection.objects.link(cam)
    e = math.radians(elev_deg); a = math.radians(azim_deg)
    cam.location = (dist*math.cos(e)*math.sin(a),
                    -dist*math.cos(e)*math.cos(a),
                    target[2] + dist*math.sin(e))
    # aim at target
    tgt = bpy.data.objects.new("CamTarget", None)
    tgt.location = target
    bpy.context.collection.objects.link(tgt)
    c = cam.constraints.new('TRACK_TO')
    c.target = tgt
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
    bpy.context.scene.camera = cam
    return cam, tgt

def cycles(res=512, samples=256, transparent=True, gpu=True):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    if gpu:
        for dt in ('OPTIX', 'CUDA'):
            try:
                prefs.compute_device_type = dt
                prefs.get_devices()
                devs = [d for d in prefs.devices if d.type == dt]
                if devs:
                    for d in prefs.devices:
                        d.use = (d.type == dt) or (d.type == 'CPU')
                    sc.cycles.device = 'GPU'
                    print(f"[render] GPU via {dt}: {[d.name for d in devs]}")
                    break
            except Exception as ex:
                print("[render] device probe failed", dt, ex)
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = 'OPTIX'
    except Exception:
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    # light paths: transmission depth matters for the glass
    sc.cycles.max_bounces = 16
    sc.cycles.transmission_bounces = 20
    sc.cycles.transparent_max_bounces = 24
    sc.cycles.glossy_bounces = 8
    sc.cycles.caustics_reflective = True
    sc.cycles.caustics_refractive = True
    sc.cycles.blur_glossy = 0.6

    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.compression = 15
    # Filmic/AgX tonemap — linear sRGB output is another instant CG tell
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        try: sc.view_settings.view_transform = 'Filmic'
        except Exception: pass
    sc.view_settings.exposure = 0.0
    return sc
