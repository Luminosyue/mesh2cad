#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [8.879999999999305e-06, 0.093583415, 0.21665742], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.08435568999999998, 'zmax': 0.08435568999999998, 'profiles': [{'outer': [[-0.017457114999999995, -0.007263619999999999], [-0.018555815000000003, -0.0037233699999999993], [-0.018922054999999993, 6.945670167485263e-19], [-0.018555815000000003, 0.0036623300000000005], [-0.017457114999999995, 0.007202590000000001], [-0.015748025, 0.010498690000000001], [-0.013367494999999993, 0.01336752], [-0.010498674999999999, 0.01574803], [-0.007263624999999996, 0.01745712], [-0.0037233549999999976, 0.01855582], [4.999999997368221e-09, 0.01892205], [0.0036623449999999974, 0.01855582], [0.007263644999999999, 0.01745712], [0.010498674999999999, 0.01574803], [0.013367505000000002, 0.01336752], [0.015748035000000007, 0.010498690000000001], [0.017457125000000004, 0.007202590000000001], [0.018555824999999998, 0.0036623300000000005], [0.018922055000000007, 6.945670167485263e-19], [0.018555824999999998, -0.0037233699999999993], [0.017457125000000004, -0.007263619999999999], [0.015748035000000007, -0.01049869], [0.013367505000000002, -0.013367509999999999], [0.010498674999999999, -0.015748019999999998], [0.007263644999999999, -0.01751815], [0.0036623449999999974, -0.01855581], [4.999999997368221e-09, -0.01892205], [-0.0037233549999999976, -0.01855581], [-0.007263624999999996, -0.01751815], [-0.010498674999999999, -0.015748019999999998], [-0.013367494999999993, -0.013367509999999999], [-0.015748025, -0.01049869]], 'holes': []}], 'simplify_tolerance': 7.5688220000000005e-06, 'sketch_entity_count': 32}
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
