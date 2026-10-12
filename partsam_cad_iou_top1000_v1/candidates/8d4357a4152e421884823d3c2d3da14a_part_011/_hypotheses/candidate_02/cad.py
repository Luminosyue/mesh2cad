#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.271797715, -0.09506701, -0.019491790000000002], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.04714255, 'zmax': 0.047142550000000005, 'profiles': [{'outer': [[-0.03268138999999999, 0.016926145000000004], [-0.028819579999999997, 0.018528374999999986], [-0.02483455999999999, 0.021321984999999988], [-0.0031838899999999948, 0.028347135000000023], [0.006400514832016513, 0.02815622374671651], [0.007703020000000005, 0.02847042500000002], [0.02335559000000001, 0.02403345499999998], [0.02394893296258977, 0.023434147008152512], [0.028901770000000007, 0.022636655000000006], [0.037159399999999995, 0.014748725000000018], [0.04254125000000002, 0.006039175000000008], [0.04525272000000001, -0.0029579350000000226], [0.04533489, -0.011914044999999984], [0.04311640000000001, -0.01959651499999998], [0.03913139, -0.02485510499999999], [0.03370844000000002, -0.027771975000000004], [0.027710330000000005, -0.028470424999999994], [0.02286263000000001, -0.027073595000000006], [0.021540769936719634, -0.023684258876040882], [0.017727240000000005, -0.022965294999999997], [0.016929951525808316, -0.02125908089753263], [0.01550876000000001, -0.02173280500000002], [0.012057800000000007, -0.02259555499999999], [0.008894430000000009, -0.021773904999999982], [0.006881370000000012, -0.02021276500000002], [0.005977560000000007, -0.01717263499999999], [0.0058132300000000026, -0.015529304999999993], [0.006224050000000009, -0.01117452499999999], [0.00827818000000001, -0.007559264999999982], [0.008507948184658738, -0.00660188591215495], [-0.0012940899999999977, -0.011667515000000017], [-0.008500295726372, -0.014488238246713987], [-0.008976589999999993, -0.01622775500000001], [-0.011232854890524235, -0.017501422419066475], [-0.012838379999999996, -0.019226754999999984], [-0.018014799999999997, -0.019925144999999977], [-0.021794449999999993, -0.020253834999999998], [-0.02490276569905242, -0.018874797505237698], [-0.028819579999999997, -0.01910349499999997], [-0.03251702999999999, -0.017624525000000002], [-0.04299316999999999, -0.012858925000000021], [-0.044352502476378015, -0.011084229444773356], [-0.045334889999999996, -0.010640444999999998], [-0.04422564999999999, 0.006080244999999984]], 'holes': []}], 'simplify_tolerance': 1.8133956000000003e-05, 'sketch_entity_count': 50}
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
