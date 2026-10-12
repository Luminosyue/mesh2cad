#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.035065439999999996, -0.370401135, 0.36921227], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.10052486999999999, 'zmax': 0.10052486999999999, 'profiles': [{'outer': [[-0.10987203499999998, 0.07340094], [-0.07340096499999998, 0.10987200999999999], [-0.02580504499999997, 0.12959853], [0.02574766500000003, 0.12959853], [0.073400925, 0.10987200999999999], [0.109871995, 0.07340094], [0.12959850500000003, 0.025747679999999995], [0.12959850500000003, -0.025805], [0.109871995, -0.07340094999999999], [0.073400925, -0.10987201999999999], [0.02574766500000003, -0.12959853], [-0.02580504499999997, -0.12959853], [-0.07340096499999998, -0.10987201999999999], [-0.10987203499999998, -0.07340094999999999], [-0.129598505, -0.025805], [-0.129598505, 0.025747679999999995]], 'holes': [[[-0.01582705499999998, 0.07953679], [-0.04507272499999998, 0.06743714], [-0.06743707500000001, 0.04501545], [-0.07953672499999997, 0.015827089999999995], [-0.07953672499999997, -0.015827060000000004], [-0.06743707500000001, -0.04507271000000001], [-0.04507272499999998, -0.06743714], [-0.01582705499999998, -0.07953677], [0.01582706500000003, -0.07953677], [0.045015344999999984, -0.06743714], [0.06743706500000002, -0.04507271000000001], [0.07953674500000002, -0.015827060000000004], [0.07953674500000002, 0.015827089999999995], [0.06743706500000002, 0.04501545], [0.045015344999999984, 0.06743714], [0.01582706500000003, 0.07953679]]]}], 'simplify_tolerance': 5.1839411999999997e-05, 'sketch_entity_count': 50}
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
