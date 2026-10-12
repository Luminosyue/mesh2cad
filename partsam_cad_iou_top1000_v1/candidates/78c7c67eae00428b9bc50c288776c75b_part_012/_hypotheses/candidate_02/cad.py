#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.22426531500000002, -0.18144281, -0.007360250000000002], 'basis': [[0.0, 0.8152988659051649, 0.5790403779131055], [-0.7200096440654306, 0.4018332098421127, -0.5657881086774065], [-0.6939640570323308, -0.41691465640072745, 0.5870230462473269]], 'axis': [0.5790403779131055, -0.5657881086774065, 0.5870230462473269], 'zmin': -0.0278315266007375, 'zmax': 0.02690286756812275, 'profiles': [{'outer': [[-0.04785154234485541, -0.03904882686891804], [-0.04900425053144831, -0.034429585586373955], [-0.05022892905237437, -0.026219442727320928], [-0.05099545558896617, -0.021600110378588836], [-0.051049053500242234, -0.021076765611352802], [-0.05013573500848018, -0.012506724286877678], [-0.04606826321066602, 0.0014079435655855212], [-0.039466125360507726, 0.010486657425463607], [-0.0350945802254983, 0.016401160997491143], [-0.031241238084426044, 0.02037155358322397], [-0.028317167302737676, 0.024127279746703995], [-0.024524544176208127, 0.030412631898229122], [-0.016870611862220747, 0.040580199448394055], [-0.006405489643086535, 0.04693638278668963], [0.0009131606507273156, 0.0510765656379095], [0.0055000747787260496, 0.052212973425743305], [0.01097774148784212, 0.04952993666330218], [0.013440069527215874, 0.04850426022299872], [0.02125659544919986, 0.045054134477079386], [0.029718152538374575, 0.0404530957908902], [0.03715365476192533, 0.03520174838847337], [0.044517479256437335, 0.028904913271381266], [0.05107465142120631, 0.021486382819769768], [0.054642624847207194, 0.01416669669748246], [0.056055132367837275, 0.010903400158448488], [0.058145325032081044, 0.004352102391640767], [0.058142251350987134, 0.0005387893106624502], [0.05678535194765659, -0.0045553167868056495], [0.053705943112096616, -0.011958647751922994], [0.048669273700215794, -0.020701051167383758], [0.04223410395619929, -0.02847594687775685], [0.03609885600653684, -0.03333871020262368], [0.03142433699636878, -0.035937931489974935], [0.02385000292439275, -0.0357560199486408], [0.019796640672513556, -0.03462781845253268], [0.013240386698767714, -0.031848926849757604], [0.010153716378334555, -0.029675332566592594], [0.0037380799874453677, -0.023369342689009594], [-0.0028395709157948597, -0.016402694564811332], [-0.0036632210586668547, -0.015822712784075713], [-0.010639878207580939, -0.011713414324045714], [-0.02318033192129168, -0.013762282400976314], [-0.02460675329190511, -0.014337728973792188], [-0.03318935837461637, -0.02705507036635342], [-0.039137508600578436, -0.040541199724960064], [-0.04318146775679483, -0.04324719637565464], [-0.044388415396675845, -0.042663331124386104], [-0.04706584397550057, -0.04106059174955891]], 'holes': []}], 'simplify_tolerance': 2.1838875706464655e-05, 'sketch_entity_count': 48}
OUT = Path(__file__).resolve().parent

def vec(v):
    return cq.Vector(float(v[0]), float(v[1]), float(v[2]))

def build():
    s = SPEC
    kind = s["kind"]
    B = s.get("basis")
    center = s.get("center")
    if kind == "extrusion":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["zmin"] * axis[i] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        result = None
        height = s["zmax"] - s["zmin"]
        for profile in s["profiles"]:
            solid = cq.Workplane(plane).polyline(profile["outer"]).close().extrude(height)
            for hole in profile["holes"]:
                cutter = cq.Workplane(plane).polyline(hole).close().extrude(height)
                solid = solid.cut(cutter)
            result = solid if result is None else result.union(solid)
    elif kind == "multi_loft":
        def loft(track):
            wires = [cq.Wire.makePolygon([vec(p) for p in section], close=True) for section in track]
            return cq.Solid.makeLoft(wires, ruled=bool(s.get("ruled", True)))
        outer = [loft(track) for track in s["outer_tracks"]]
        # Keep disjoint solids as a legal STEP compound.  Global Boolean fusion
        # is unnecessary for training geometry and scales poorly with profiles.
        for track in s.get("hole_tracks", []):
            cutter = loft(track)
            cut_outer = []
            for solid in outer:
                try:
                    cut_outer.append(solid.cut(cutter))
                except Exception:
                    cut_outer.append(solid)
            outer = cut_outer
        result = outer[0] if len(outer) == 1 else cq.Compound.makeCompound(outer)
    elif kind == "box":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["mins"][0]*B[i][0] + s["mins"][1]*B[i][1] + s["mins"][2]*B[i][2] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        dx=s["maxs"][0]-s["mins"][0]; dy=s["maxs"][1]-s["mins"][1]; dz=s["maxs"][2]-s["mins"][2]
        result = cq.Workplane(plane).rect(dx,dy,centered=False).extrude(dz)
    elif kind == "cylinder":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["zmin"] * axis[i] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        result = cq.Workplane(plane).circle(s["radius"]).extrude(s["zmax"]-s["zmin"])
    else:
        raise ValueError(kind)
    cq.exporters.export(result, str(OUT / "reconstructed.step"))
    cq.exporters.export(result, str(OUT / "reconstructed.stl"), tolerance=0.001, angularTolerance=0.05)
    return result

if __name__ == "__main__":
    build()
