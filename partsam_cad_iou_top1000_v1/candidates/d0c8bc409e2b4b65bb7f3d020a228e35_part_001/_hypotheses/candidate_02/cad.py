#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.05112562999999999, -0.314016835, -0.08855225], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.1961539, 'zmax': 0.1961539, 'profiles': [{'outer': [[-0.035020665000000006, -0.19263385], [-0.035020665000000006, 0.19263382], [-0.03489925500000002, 0.19615391999999998], [-0.03406952499999999, 0.19605811], [-0.02399130500000002, 0.18858697000000002], [-0.01854749499999997, 0.18434854], [-0.012678634999999994, 0.17936774], [-0.006668165000000004, 0.17381226], [-0.0006981349999999886, 0.16772996], [0.005656374999999991, 0.16078563], [0.012759665000000031, 0.15269186], [0.02026773500000001, 0.14380787], [0.027391264999999998, 0.13499574000000003], [0.032592285, 0.1283627], [0.034717184999999984, 0.12544127], [0.035020755000000015, 0.12371716], [0.035020755000000015, -0.12371718999999999], [0.034717184999999984, -0.12544129999999998], [0.032592285, -0.12836271999999999], [0.02026773500000001, -0.14380790999999998], [0.012759665000000031, -0.15269188], [0.005656374999999991, -0.16078564], [-0.0006981349999999886, -0.16772998], [-0.006668165000000004, -0.17381228999999998], [-0.012678634999999994, -0.17936776999999998], [-0.01854749499999997, -0.18434854], [-0.02399130500000002, -0.18858695999999997], [-0.03406952499999999, -0.19605814], [-0.03489925500000002, -0.19615391999999998]], 'holes': []}], 'simplify_tolerance': 7.8461568e-05, 'sketch_entity_count': 35}
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
