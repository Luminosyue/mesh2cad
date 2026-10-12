#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.06597268, -0.46588063, -0.013473035000000001], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.034119279999999974, 'zmax': 0.03411928000000003, 'profiles': [{'outer': [[-0.046136025, 0.039439539999999995], [0.0005340750000000019, 0.05242171999999999], [0.033646835, 0.05562616999999999], [0.058255455000000005, 0.05640674999999999], [0.07394909499999999, 0.05073728999999999], [0.07920770499999999, 0.039151939999999996], [0.074195595, 0.027361159999999995], [0.060350675, 0.020911159999999998], [0.0515325540682602, 0.0177017609105404], [0.060350675, 0.014748739999999996], [0.074195595, 0.009284709999999988], [0.07920770499999999, -0.0009449100000000071], [0.074195595, -0.011174540000000004], [0.060350675, -0.016638560000000004], [0.051517865, -0.019350020000000002], [0.060350675, -0.022020410000000004], [0.074195595, -0.027772000000000005], [0.07920770499999999, -0.03898762], [0.07394909499999999, -0.050367560000000006], [0.058255455000000005, -0.056406750000000005], [0.033646835, -0.05616024000000001], [0.0005340750000000019, -0.05328444], [-0.046136025, -0.040425520000000006], [-0.069429995, -0.028264990000000004], [-0.07698923499999999, -0.015282810000000008], [-0.07920770499999999, -0.004642350000000003], [-0.07698923499999999, 0.006039179999999991], [-0.069429995, 0.01926784999999999]], 'holes': []}], 'simplify_tolerance': 3.1683082e-05, 'sketch_entity_count': 46}
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
