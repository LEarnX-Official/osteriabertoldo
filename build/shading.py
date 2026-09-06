"""
Photoreal shading library for Osteria il Bertoldo.
Everything procedural — no texture files to ship or manage.

The core idea: real surfaces vary per-pixel in BOTH colour and roughness.
Flat GLB materials vary in neither, which is exactly what makes them read
as plastic. Every shader here drives roughness with noise.
"""
import bpy, math

def _new(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (600, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (300, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m, nt, bsdf

def _set(b, key, val):
    """Blender renames Principled sockets between versions; fail soft."""
    if key in b.inputs:
        b.inputs[key].default_value = val
        return True
    return False

def _noise(nt, scale, detail=8.0, rough=0.5, loc=(-600, 0)):
    n = nt.nodes.new('ShaderNodeTexNoise'); n.location = loc
    n.inputs['Scale'].default_value = scale
    n.inputs['Detail'].default_value = detail
    if 'Roughness' in n.inputs: n.inputs['Roughness'].default_value = rough
    return n

def _ramp(nt, stops, loc=(-380, 0)):
    r = nt.nodes.new('ShaderNodeValToRGB'); r.location = loc
    el = r.color_ramp.elements
    while len(el) > 1: el.remove(el[-1])
    el[0].position = stops[0][0]; el[0].color = stops[0][1]
    for pos, col in stops[1:]:
        e = el.new(pos); e.color = col
    return r

def _bump(nt, bsdf, src, strength=0.12, dist=0.006, loc=(60, -320)):
    b = nt.nodes.new('ShaderNodeBump'); b.location = loc
    b.inputs['Strength'].default_value = strength
    b.inputs['Distance'].default_value = dist
    nt.links.new(src, b.inputs['Height'])
    nt.links.new(b.outputs['Normal'], bsdf.inputs['Normal'])
    return b

# ---------------------------------------------------------------- porcelain
def porcelain(name="Porcelain_PR", tint=(0.94, 0.93, 0.90)):
    """Glazed white ceramic: near-white, low roughness, but with a faint
    uneven glaze so the specular highlight breaks up like real fired clay."""
    m, nt, b = _new(name)
    _set(b, 'Base Color', (*tint, 1))
    _set(b, 'Metallic', 0.0)
    _set(b, 'IOR', 1.52)
    # glaze unevenness -> roughness variation (the whole trick)
    n = _noise(nt, 42.0, detail=6, loc=(-620, -180))
    r = _ramp(nt, [(0.38, (0.045,)*3 + (1,)), (0.62, (0.115,)*3 + (1,))], loc=(-400, -180))
    nt.links.new(n.outputs['Fac'], r.inputs['Fac'])
    nt.links.new(r.outputs['Color'], b.inputs['Roughness'])
    # clearcoat = the glaze layer itself
    _set(b, 'Coat Weight', 0.55) or _set(b, 'Clearcoat', 0.55)
    _set(b, 'Coat Roughness', 0.06) or _set(b, 'Clearcoat Roughness', 0.06)
    # micro surface undulation
    n2 = _noise(nt, 120.0, detail=4, loc=(-620, -520))
    _bump(nt, b, n2.outputs['Fac'], strength=0.06, dist=0.0012)
    return m

# ---------------------------------------------------------------- risotto
def risotto(name="Risotto_PR", sauce=(0.42, 0.045, 0.055)):
    """Amarone risotto. Grains = high-freq noise bump + colour variance.
    Starch = subsurface. Wet sauce = clearcoat with varying roughness.
    This is the single biggest upgrade over a flat maroon blob."""
    m, nt, b = _new(name)
    # colour: sauce base, lighter rice showing through
    n_grain = _noise(nt, 190.0, detail=10, rough=0.62, loc=(-900, 120))
    ramp = _ramp(nt, [
        (0.34, (sauce[0]*0.42, sauce[1]*0.40, sauce[2]*0.48, 1)),
        (0.52, (*sauce, 1)),
        (0.72, (0.90, 0.82, 0.66, 1)),   # exposed rice grain (butter/parmesan)
    ], loc=(-660, 120))
    nt.links.new(n_grain.outputs['Fac'], ramp.inputs['Fac'])
    # large-scale sauce pooling on top of grain colour
    n_pool = _noise(nt, 9.0, detail=4, loc=(-900, -140))
    mix = nt.nodes.new('ShaderNodeMixRGB'); mix.location = (-420, 60)
    mix.blend_type = 'MULTIPLY'; mix.inputs['Fac'].default_value = 0.35
    nt.links.new(ramp.outputs['Color'], mix.inputs['Color1'])
    nt.links.new(n_pool.outputs['Color'], mix.inputs['Color2'])
    nt.links.new(mix.outputs['Color'], b.inputs['Base Color'])
    # wetness: roughness driven by the pooling noise (wet spots = glossy)
    # Wet risotto is GLOSSY: real mantecatura leaves a sheen. Keep the whole
    # roughness range low so grains read creamy rather than dry and dusty.
    rr = _ramp(nt, [(0.28, (0.055,)*3+(1,)), (0.72, (0.26,)*3+(1,))], loc=(-420, -220))
    nt.links.new(n_pool.outputs['Fac'], rr.inputs['Fac'])
    nt.links.new(rr.outputs['Color'], b.inputs['Roughness'])
    # starch translucency
    if not _set(b, 'Subsurface Weight', 0.42): _set(b, 'Subsurface', 0.42)
    _set(b, 'Subsurface Radius', (0.9, 0.5, 0.35))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.012
    _set(b, 'Coat Weight', 0.85) or _set(b, 'Clearcoat', 0.85)
    _set(b, 'Coat Roughness', 0.09) or _set(b, 'Clearcoat Roughness', 0.09)
    # grain relief
    _bump(nt, b, n_grain.outputs['Fac'], strength=0.40, dist=0.0018)
    return m

# ---------------------------------------------------------------- prawn
def prawn(name="Prawn_PR"):
    """Cooked prawn flesh: strong SSS, banded colour, glossy wet coat."""
    m, nt, b = _new(name)
    n = _noise(nt, 26.0, detail=8, loc=(-880, 100))
    ramp = _ramp(nt, [
        (0.30, (0.88, 0.30, 0.16, 1)),
        (0.55, (0.95, 0.48, 0.28, 1)),
        (0.78, (0.98, 0.78, 0.62, 1)),
    ], loc=(-640, 100))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    if not _set(b, 'Subsurface Weight', 0.65): _set(b, 'Subsurface', 0.65)
    _set(b, 'Subsurface Radius', (1.0, 0.32, 0.18))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.02
    rr = _ramp(nt, [(0.35, (0.12,)*3+(1,)), (0.7, (0.30,)*3+(1,))], loc=(-400, -200))
    nt.links.new(n.outputs['Fac'], rr.inputs['Fac'])
    nt.links.new(rr.outputs['Color'], b.inputs['Roughness'])
    _set(b, 'Coat Weight', 0.6) or _set(b, 'Clearcoat', 0.6)
    _set(b, 'Coat Roughness', 0.1) or _set(b, 'Clearcoat Roughness', 0.1)
    _bump(nt, b, n.outputs['Fac'], strength=0.3, dist=0.003)
    return m

# ---------------------------------------------------------------- shells
def nacre(name="Nacre_PR", base=(0.06, 0.05, 0.09)):
    """Mussel shell: dark base, iridescent inner sheen via thin film / coat."""
    m, nt, b = _new(name)
    n = _noise(nt, 34.0, detail=9, loc=(-880, 60))
    ramp = _ramp(nt, [
        (0.35, (*base, 1)),
        (0.55, (base[0]*1.8, base[1]*1.8, base[2]*2.0, 1)),
        (0.80, (0.20, 0.20, 0.24, 1)),
    ], loc=(-640, 60))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    rr = _ramp(nt, [(0.3, (0.08,)*3+(1,)), (0.75, (0.28,)*3+(1,))], loc=(-400, -200))
    nt.links.new(n.outputs['Fac'], rr.inputs['Fac'])
    nt.links.new(rr.outputs['Color'], b.inputs['Roughness'])
    _set(b, 'Coat Weight', 0.9) or _set(b, 'Clearcoat', 0.9)
    _set(b, 'Coat Roughness', 0.05) or _set(b, 'Clearcoat Roughness', 0.05)
    # thin-film iridescence (Blender 4.x+ Principled)
    # Subtle only: real mussel shells are near-black with a faint sheen.
    # Strong thin-film reads as purple plastic, which is worse than flat.
    if 'Coat Tint' in b.inputs: b.inputs['Coat Tint'].default_value = (0.90, 0.93, 1.0, 1)
    if 'Thin Film Thickness' in b.inputs:
        b.inputs['Thin Film Thickness'].default_value = 210.0
        if 'Thin Film IOR' in b.inputs: b.inputs['Thin Film IOR'].default_value = 1.32
    _bump(nt, b, n.outputs['Fac'], strength=0.25, dist=0.002)
    return m

def clamshell(name="Clam_PR"):
    m = nacre(name, base=(0.62, 0.55, 0.44))
    return m

# ---------------------------------------------------------------- pasta
def pasta(name="Pasta_PR", tint=(0.86, 0.72, 0.44)):
    """Egg tagliatelle: matte-ish, slight SSS, oil sheen in patches."""
    m, nt, b = _new(name)
    n = _noise(nt, 60.0, detail=8, loc=(-880, 80))
    ramp = _ramp(nt, [
        (0.35, (tint[0]*0.80, tint[1]*0.78, tint[2]*0.72, 1)),
        (0.60, (*tint, 1)),
        (0.82, (0.95, 0.88, 0.66, 1)),
    ], loc=(-640, 80))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    if not _set(b, 'Subsurface Weight', 0.22): _set(b, 'Subsurface', 0.22)
    _set(b, 'Subsurface Radius', (0.7, 0.55, 0.35))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.01
    n2 = _noise(nt, 14.0, detail=4, loc=(-880, -220))
    rr = _ramp(nt, [(0.35, (0.16,)*3+(1,)), (0.68, (0.46,)*3+(1,))], loc=(-620, -220))
    nt.links.new(n2.outputs['Fac'], rr.inputs['Fac'])
    nt.links.new(rr.outputs['Color'], b.inputs['Roughness'])
    _set(b, 'Coat Weight', 0.3) or _set(b, 'Clearcoat', 0.3)
    _bump(nt, b, n.outputs['Fac'], strength=0.2, dist=0.0018)
    return m

# ---------------------------------------------------------------- herbs
def herb(name="Herb_PR", tint=(0.13, 0.31, 0.09)):
    """Parsley/basil: waxy leaf, translucent when backlit, veins."""
    m, nt, b = _new(name)
    n = _noise(nt, 90.0, detail=8, loc=(-880, 60))
    ramp = _ramp(nt, [
        (0.35, (tint[0]*0.6, tint[1]*0.65, tint[2]*0.5, 1)),
        (0.60, (*tint, 1)),
        (0.80, (0.30, 0.52, 0.18, 1)),
    ], loc=(-640, 60))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    if not _set(b, 'Subsurface Weight', 0.45): _set(b, 'Subsurface', 0.45)
    _set(b, 'Subsurface Radius', (0.35, 0.85, 0.25))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.008
    _set(b, 'Roughness', 0.34)
    _set(b, 'Coat Weight', 0.45) or _set(b, 'Clearcoat', 0.45)
    _set(b, 'Coat Roughness', 0.12) or _set(b, 'Clearcoat Roughness', 0.12)
    _bump(nt, b, n.outputs['Fac'], strength=0.35, dist=0.0012)
    return m

# ---------------------------------------------------------------- glass/wine
def crystal(name="Crystal_PR"):
    """Real lead crystal: full transmission, dispersion, tiny roughness.
    This is what the Three.js opacity=.17 hack was pretending to be."""
    m, nt, b = _new(name)
    _set(b, 'Base Color', (1, 1, 1, 1))
    _set(b, 'Metallic', 0.0)
    _set(b, 'Roughness', 0.012)
    _set(b, 'IOR', 1.55)                      # lead crystal
    if not _set(b, 'Transmission Weight', 1.0): _set(b, 'Transmission', 1.0)
    # dispersion = the rainbow glints in the stem
    for k in ('Dispersion',):
        if k in b.inputs: b.inputs[k].default_value = 0.06
    m.use_screen_refraction = True
    if hasattr(m, 'refraction_depth'): m.refraction_depth = 0.0
    m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else m.blend_method
    return m

def wine(name="Wine_PR", col=(0.42, 0.055, 0.070)):
    """Amarone: dense absorbing volume, not a coloured surface.
    Beer's-law absorption through the body is what sells real wine."""
    m, nt, b = _new(name)
    _set(b, 'Base Color', (*col, 1))
    _set(b, 'Roughness', 0.02)
    _set(b, 'IOR', 1.35)
    if not _set(b, 'Transmission Weight', 1.0): _set(b, 'Transmission', 1.0)
    # volume absorption inside the liquid
    nt_out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    vol = nt.nodes.new('ShaderNodeVolumeAbsorption'); vol.location = (300, -260)
    vol.inputs['Color'].default_value = (0.62, 0.10, 0.13, 1)
    vol.inputs['Density'].default_value = 26.0
    nt.links.new(vol.outputs['Volume'], nt_out.inputs['Volume'])
    m.use_screen_refraction = True
    return m

# ---------------------------------------------------------------- metal
def brass(name="Brass_PR", polish=0.78):
    """Antique brass: anisotropic-ish brushed metal with tarnish variation."""
    m, nt, b = _new(name)
    _set(b, 'Base Color', (0.72, 0.53, 0.24, 1))
    _set(b, 'Metallic', 1.0)
    n = _noise(nt, 55.0, detail=7, loc=(-880, -160))
    rr = _ramp(nt, [(0.35, (0.14,)*3+(1,)), (0.72, (0.42,)*3+(1,))], loc=(-620, -160))
    nt.links.new(n.outputs['Fac'], rr.inputs['Fac'])
    nt.links.new(rr.outputs['Color'], b.inputs['Roughness'])
    if 'Anisotropic' in b.inputs: b.inputs['Anisotropic'].default_value = 0.5
    _bump(nt, b, n.outputs['Fac'], strength=0.12, dist=0.0008)
    return m

def gold(name="Gold_PR"):
    m, nt, b = _new(name)
    _set(b, 'Base Color', (0.86, 0.66, 0.30, 1))
    _set(b, 'Metallic', 1.0)
    n = _noise(nt, 80.0, detail=6, loc=(-880, -160))
    rr = _ramp(nt, [(0.35, (0.10,)*3+(1,)), (0.7, (0.32,)*3+(1,))], loc=(-620, -160))
    nt.links.new(n.outputs['Fac'], rr.inputs['Fac'])
    nt.links.new(rr.outputs['Color'], b.inputs['Roughness'])
    _bump(nt, b, n.outputs['Fac'], strength=0.15, dist=0.0006)
    return m

def emissive(name="Bulb_PR", col=(1.0, 0.72, 0.40), power=28.0):
    m, nt, b = _new(name)
    out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    e = nt.nodes.new('ShaderNodeEmission'); e.location = (300, 0)
    e.inputs['Color'].default_value = (*col, 1)
    e.inputs['Strength'].default_value = power
    nt.links.new(e.outputs['Emission'], out.inputs['Surface'])
    nt.nodes.remove(b)
    return m

def generic_food(name, tint, rough=0.32, sss=0.3):
    """Fallback for meats/fish/cheese: SSS + noisy roughness + wet coat."""
    m, nt, b = _new(name)
    n = _noise(nt, 45.0, detail=8, loc=(-880, 60))
    ramp = _ramp(nt, [
        (0.32, (tint[0]*0.72, tint[1]*0.72, tint[2]*0.72, 1)),
        (0.58, (*tint, 1)),
        (0.80, (min(tint[0]*1.35,1), min(tint[1]*1.3,1), min(tint[2]*1.25,1), 1)),
    ], loc=(-640, 60))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    if not _set(b, 'Subsurface Weight', sss): _set(b, 'Subsurface', sss)
    _set(b, 'Subsurface Radius', (1.0, 0.45, 0.28))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.015
    rr = _ramp(nt, [(0.32, (max(rough-0.18,0.05),)*3+(1,)), (0.7, (rough+0.16,)*3+(1,))], loc=(-400, -200))
    nt.links.new(n.outputs['Fac'], rr.inputs['Fac'])
    nt.links.new(rr.outputs['Color'], b.inputs['Roughness'])
    _set(b, 'Coat Weight', 0.42) or _set(b, 'Clearcoat', 0.42)
    _set(b, 'Coat Roughness', 0.14) or _set(b, 'Clearcoat Roughness', 0.14)
    _bump(nt, b, n.outputs['Fac'], strength=0.28, dist=0.0025)
    return m


# ---------------------------------------------------------------- extras
def mushroom(name="Porcini_PR", cap=(0.36, 0.22, 0.12)):
    """Porcini: matte suede cap, pale spongy stem, seared glossy edges."""
    m, nt, b = _new(name)
    n = _noise(nt, 38.0, detail=9, loc=(-880, 80))
    ramp = _ramp(nt, [
        (0.30, (cap[0]*0.55, cap[1]*0.50, cap[2]*0.45, 1)),
        (0.55, (*cap, 1)),
        (0.78, (0.62, 0.47, 0.30, 1)),
    ], loc=(-640, 80))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    # caps are suede-matte; the seared faces are glossy. wide roughness range.
    rr = _ramp(nt, [(0.28, (0.22,)*3+(1,)), (0.72, (0.62,)*3+(1,))], loc=(-400, -200))
    nt.links.new(n.outputs['Fac'], rr.inputs['Fac'])
    nt.links.new(rr.outputs['Color'], b.inputs['Roughness'])
    if not _set(b, 'Subsurface Weight', 0.22): _set(b, 'Subsurface', 0.22)
    _set(b, 'Subsurface Radius', (0.6, 0.42, 0.28))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.008
    _set(b, 'Coat Weight', 0.30) or _set(b, 'Clearcoat', 0.30)
    _bump(nt, b, n.outputs['Fac'], strength=0.42, dist=0.0022)
    return m

def truffle(name="Truffle_PR"):
    """Black truffle shaving: near-black, marbled white veins, matte."""
    m, nt, b = _new(name)
    n = _noise(nt, 130.0, detail=10, loc=(-880, 60))
    ramp = _ramp(nt, [
        (0.42, (0.030, 0.024, 0.020, 1)),
        (0.60, (0.075, 0.062, 0.050, 1)),
        (0.74, (0.30, 0.27, 0.22, 1)),      # marbling
    ], loc=(-640, 60))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    _set(b, 'Roughness', 0.52)
    _bump(nt, b, n.outputs['Fac'], strength=0.5, dist=0.0012)
    return m

def raw_fish(name="Tuna_PR", flesh=(0.62, 0.10, 0.10)):
    """Seared tuna: deep red translucent flesh with fibrous banding."""
    m, nt, b = _new(name)
    # stretched noise = muscle fibre direction
    n = _noise(nt, 55.0, detail=9, loc=(-1080, 80))
    mp = nt.nodes.new('ShaderNodeMapping'); mp.location = (-1260, 80)
    mp.inputs['Scale'].default_value = (1.0, 5.5, 1.0)
    tc = nt.nodes.new('ShaderNodeTexCoord'); tc.location = (-1440, 80)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
    ramp = _ramp(nt, [
        (0.34, (flesh[0]*0.55, flesh[1]*0.55, flesh[2]*0.60, 1)),
        (0.56, (*flesh, 1)),
        (0.78, (0.88, 0.42, 0.32, 1)),
    ], loc=(-640, 80))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    if not _set(b, 'Subsurface Weight', 0.55): _set(b, 'Subsurface', 0.55)
    _set(b, 'Subsurface Radius', (1.0, 0.25, 0.16))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.014
    _set(b, 'Roughness', 0.26)
    _set(b, 'Coat Weight', 0.55) or _set(b, 'Clearcoat', 0.55)
    _set(b, 'Coat Roughness', 0.12) or _set(b, 'Clearcoat Roughness', 0.12)
    _bump(nt, b, n.outputs['Fac'], strength=0.22, dist=0.0015)
    return m

def cream(name="Cream_PR", tint=(0.95, 0.92, 0.84)):
    """Whipped cream / panna: bright, soft SSS, gentle sheen."""
    m, nt, b = _new(name)
    _set(b, 'Base Color', (*tint, 1))
    if not _set(b, 'Subsurface Weight', 0.62): _set(b, 'Subsurface', 0.62)
    _set(b, 'Subsurface Radius', (1.0, 0.92, 0.80))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.02
    n = _noise(nt, 70.0, detail=7, loc=(-880, -160))
    rr = _ramp(nt, [(0.35, (0.18,)*3+(1,)), (0.7, (0.40,)*3+(1,))], loc=(-620, -160))
    nt.links.new(n.outputs['Fac'], rr.inputs['Fac'])
    nt.links.new(rr.outputs['Color'], b.inputs['Roughness'])
    _bump(nt, b, n.outputs['Fac'], strength=0.30, dist=0.0018)
    return m

def berry(name="Cherry_PR", tint=(0.42, 0.03, 0.06)):
    """Cherry: glossy skin, deep translucent flesh."""
    m, nt, b = _new(name)
    _set(b, 'Base Color', (*tint, 1))
    _set(b, 'Roughness', 0.10)
    if not _set(b, 'Subsurface Weight', 0.45): _set(b, 'Subsurface', 0.45)
    _set(b, 'Subsurface Radius', (1.0, 0.18, 0.14))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.01
    _set(b, 'Coat Weight', 0.9) or _set(b, 'Clearcoat', 0.9)
    _set(b, 'Coat Roughness', 0.04) or _set(b, 'Clearcoat Roughness', 0.04)
    return m

def crumb(name="Crumb_PR", tint=(0.68, 0.50, 0.28)):
    """Toasted crumb / pistachio dust: dry, matte, high micro-relief."""
    m, nt, b = _new(name)
    n = _noise(nt, 220.0, detail=10, loc=(-880, 60))
    ramp = _ramp(nt, [
        (0.32, (tint[0]*0.55, tint[1]*0.55, tint[2]*0.55, 1)),
        (0.58, (*tint, 1)),
        (0.80, (min(tint[0]*1.4,1), min(tint[1]*1.35,1), min(tint[2]*1.3,1), 1)),
    ], loc=(-640, 60))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    _set(b, 'Roughness', 0.72)
    _bump(nt, b, n.outputs['Fac'], strength=0.8, dist=0.0016)
    return m

def hard_cheese(name="Grana_PR"):
    """Grana/parmesan shaving: pale, granular, slightly waxy."""
    m, nt, b = _new(name)
    n = _noise(nt, 150.0, detail=9, loc=(-880, 60))
    ramp = _ramp(nt, [
        (0.35, (0.80, 0.73, 0.55, 1)),
        (0.62, (0.92, 0.87, 0.70, 1)),
        (0.82, (0.98, 0.95, 0.84, 1)),
    ], loc=(-640, 60))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    if not _set(b, 'Subsurface Weight', 0.30): _set(b, 'Subsurface', 0.30)
    _set(b, 'Subsurface Radius', (0.9, 0.80, 0.62))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.006
    _set(b, 'Roughness', 0.44)
    _bump(nt, b, n.outputs['Fac'], strength=0.45, dist=0.0010)
    return m

def seed(name="Sesame_PR", tint=(0.92, 0.86, 0.70)):
    """Sesame seed: small, smooth, faintly translucent, slight sheen."""
    m, nt, b = _new(name)
    _set(b, 'Base Color', (*tint, 1))
    _set(b, 'Roughness', 0.26)
    if not _set(b, 'Subsurface Weight', 0.35): _set(b, 'Subsurface', 0.35)
    _set(b, 'Subsurface Radius', (0.8, 0.70, 0.50))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.004
    _set(b, 'Coat Weight', 0.4) or _set(b, 'Clearcoat', 0.4)
    return m

def allium(name="Onion_PR", tint=(0.88, 0.86, 0.90)):
    """Onion / spring onion: thin translucent layers, wet cut face."""
    m, nt, b = _new(name)
    _set(b, 'Base Color', (*tint, 1))
    if not _set(b, 'Subsurface Weight', 0.60): _set(b, 'Subsurface', 0.60)
    _set(b, 'Subsurface Radius', (0.9, 0.88, 0.85))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.01
    _set(b, 'Roughness', 0.20)
    _set(b, 'Coat Weight', 0.6) or _set(b, 'Clearcoat', 0.6)
    _set(b, 'Coat Roughness', 0.08) or _set(b, 'Clearcoat Roughness', 0.08)
    return m

def beef_tartare(name="Beef_PR", tint=(0.46, 0.075, 0.075)):
    """Hand-cut raw beef: deep red, wet, visible cut-cube facets."""
    m, nt, b = _new(name)
    n = _noise(nt, 95.0, detail=10, loc=(-880, 60))
    ramp = _ramp(nt, [
        (0.32, (tint[0]*0.50, tint[1]*0.55, tint[2]*0.55, 1)),
        (0.58, (*tint, 1)),
        (0.80, (0.72, 0.22, 0.18, 1)),
    ], loc=(-640, 60))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    if not _set(b, 'Subsurface Weight', 0.50): _set(b, 'Subsurface', 0.50)
    _set(b, 'Subsurface Radius', (1.0, 0.22, 0.16))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.012
    rr = _ramp(nt, [(0.30, (0.08,)*3+(1,)), (0.70, (0.30,)*3+(1,))], loc=(-400, -200))
    nt.links.new(n.outputs['Fac'], rr.inputs['Fac'])
    nt.links.new(rr.outputs['Color'], b.inputs['Roughness'])
    _set(b, 'Coat Weight', 0.75) or _set(b, 'Clearcoat', 0.75)
    _set(b, 'Coat Roughness', 0.10) or _set(b, 'Clearcoat Roughness', 0.10)
    _bump(nt, b, n.outputs['Fac'], strength=0.35, dist=0.0018)
    return m

def bisque(name="Bisque_PR", tint=(0.80, 0.34, 0.14)):
    """Shellfish bisque: opaque warm liquid, glossy, slight surface film."""
    m, nt, b = _new(name)
    n = _noise(nt, 12.0, detail=6, loc=(-880, 60))
    ramp = _ramp(nt, [
        (0.35, (tint[0]*0.72, tint[1]*0.68, tint[2]*0.62, 1)),
        (0.62, (*tint, 1)),
        (0.82, (min(tint[0]*1.2,1), min(tint[1]*1.3,1), min(tint[2]*1.5,1), 1)),
    ], loc=(-640, 60))
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    if not _set(b, 'Subsurface Weight', 0.40): _set(b, 'Subsurface', 0.40)
    _set(b, 'Subsurface Radius', (1.0, 0.5, 0.28))
    if 'Subsurface Scale' in b.inputs: b.inputs['Subsurface Scale'].default_value = 0.015
    _set(b, 'Roughness', 0.08)
    _set(b, 'Coat Weight', 0.8) or _set(b, 'Clearcoat', 0.8)
    _set(b, 'Coat Roughness', 0.05) or _set(b, 'Clearcoat Roughness', 0.05)
    _bump(nt, b, n.outputs['Fac'], strength=0.10, dist=0.0008)
    return m
