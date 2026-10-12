#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0031893100000000008, -0.094582215, 0.243704825], 'basis': [[0.0, 0.9986490722236467, 0.05196181816343512], [-0.8627135271021773, 0.026276725652614772, -0.5050098056908382], [-0.5056929603572913, -0.04482816342241909, 0.8615480634353792]], 'axis': [0.05196181816343512, -0.5050098056908382, 0.8615480634353792], 'zmin': -0.0546254708804184, 'zmax': 0.06414934420818087, 'profiles': [{'outer': [[-0.11220844326844585, -0.06295925567721221], [-0.11220844326844585, -0.019607400127447588], [-0.11396548014628323, 0.017771653785988738], [-0.11440417566418554, 0.056781391159546495], [-0.11396548014628323, 0.08568075938679678], [-0.11396548014628323, 0.11893848981732065], [-0.11440417566418554, 0.14898411344282161], [-0.11396548014628323, 0.18417342291901892], [-0.11396548014628323, 0.22733696321323432], [-0.11339893370069601, 0.276262388205745], [-0.11406205600559946, 0.30309160135119645], [-0.10896657817998291, 0.3039540909303752], [-0.0999249848334391, 0.3045192028239927], [-0.08731089283555764, 0.3048119427256274], [-0.0710133003492932, 0.30551391461242217], [-0.055153361652411914, 0.3089066558337311], [-0.03520252825774804, 0.3099133414627978], [-0.014617947674571785, 0.31013368710640044], [0.03083303422244031, 0.3096837843326559], [0.054780293976151896, 0.3071555154419387], [0.09011888556321716, 0.3071491016583684], [0.09034775208321566, 0.2297688439836083], [0.09086269922474749, 0.18665095220820593], [0.09086269922474749, -0.1393729672228333], [0.08824120167033819, -0.2716291739514952], [0.08824120167033819, -0.30786239926569087], [0.08453943779973526, -0.31103896712300716], [0.004463352819288487, -0.3106967019469261], [-0.020752926732078195, -0.3094951587289001], [-0.04032346180523415, -0.30880983831101133], [-0.05862277882862906, -0.30765675812741033], [-0.07593701673026149, -0.3072665080170209], [-0.09006487389479856, -0.30761167758988295], [-0.10533484841857071, -0.3084181280580994], [-0.11263815665710698, -0.30746769677927793], [-0.11263815665710698, -0.27274102346894813], [-0.11395087789701408, -0.2364392223615533], [-0.11220844326844585, -0.20002036554113642], [-0.11220844326844585, -0.14190401274255346], [-0.11440417566418554, -0.10815145506665923]], 'holes': []}], 'simplify_tolerance': 0.00012423453084588152, 'sketch_entity_count': 49}
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
