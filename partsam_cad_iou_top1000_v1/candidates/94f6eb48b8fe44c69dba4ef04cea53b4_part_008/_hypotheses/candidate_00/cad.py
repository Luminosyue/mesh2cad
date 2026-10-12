#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.08586613, -0.11741121, -0.209020385], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.023911019999999998, 'zmax': 0.023911020000000005, 'profiles': [{'outer': [[-0.006791485000000014, -0.04133919000000001], [-0.013342385000000012, -0.03894304], [-0.019356614999999994, -0.03504649], [-0.024649155000000006, -0.02980632000000001], [-0.02897939499999999, -0.023424049999999988], [-0.032199334999999996, -0.01612361999999999], [-0.034179395, -0.008218569999999994], [-0.03484559500000001, 0.0], [-0.034179395, 0.008218580000000003], [-0.032199334999999996, 0.016146030000000006], [-0.02897939499999999, 0.023424050000000002], [-0.024649155000000006, 0.02982871000000001], [-0.019356614999999994, 0.035068890000000005], [-0.013342385000000012, 0.038965429999999995], [-0.006791485000000014, 0.04136158000000001], [-4.999999997368221e-09, 0.04216777000000001], [0.006791474999999991, 0.04136158000000001], [0.01332386499999999, 0.038965429999999995], [0.019356614999999994, 0.03506888], [0.02463062499999999, 0.0298287], [0.028960884999999992, 0.023424040000000007], [0.03218080500000001, 0.016146019999999997], [0.034160885, 0.008218570000000008], [0.03484559500000001, 0.0], [0.034160885, -0.008218569999999994], [0.03218080500000001, -0.01612361999999999], [0.028960884999999992, -0.023424049999999988], [0.02463062499999999, -0.02980632000000001], [0.019356614999999994, -0.03504649], [0.01332386499999999, -0.03894304], [0.006791474999999991, -0.04133919000000001], [-4.999999997368221e-09, -0.04216777000000001]], 'holes': []}], 'simplify_tolerance': 1.6867108000000005e-05, 'sketch_entity_count': 32}
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
