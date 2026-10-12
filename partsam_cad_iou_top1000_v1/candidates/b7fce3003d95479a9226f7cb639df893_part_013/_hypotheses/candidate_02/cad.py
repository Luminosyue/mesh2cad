#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.28627834500000005, 0.25538057000000003, -0.194124495], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.059491925, 'zmax': 0.059491925, 'profiles': [{'outer': [[-0.22725057999999998, -0.041633534999999944], [-0.22725057999999998, 0.041620705000000036], [-0.22026484999999996, 0.052051435000000035], [-0.06933539999999999, 0.052051435000000035], [-0.06933539999999999, 0.060039635000000036], [-0.033051549999999985, 0.060039635000000036], [-0.033051549999999985, 0.052051435000000035], [-0.013229789999999964, 0.052051435000000035], [-0.006196199999999985, 0.041620705000000036], [-0.006196199999999985, 0.019100405000000042], [0.01165086000000004, 0.019100405000000042], [0.01165086000000004, 0.03578335500000007], [0.01720107000000004, 0.04257767500000004], [0.10480946000000002, 0.04257767500000004], [0.11035973000000002, 0.03578335500000007], [0.11035973000000002, 0.019100405000000042], [0.12858951000000002, 0.019100405000000042], [0.12858951000000002, 0.03410870500000007], [0.13413978000000004, 0.04061593500000005], [0.22174817000000002, 0.04061593500000005], [0.22725058000000004, 0.03410870500000007], [0.22725058000000004, -0.03416933499999997], [0.22174817000000002, -0.04062872499999998], [0.13413978000000004, -0.04062872499999998], [0.12858951000000002, -0.03416933499999997], [0.12858951000000002, -0.019146044999999945], [0.11035973000000002, -0.019146044999999945], [0.11035973000000002, -0.03579615499999994], [0.10480946000000002, -0.04259049499999995], [0.01720107000000004, -0.04259049499999995], [0.01165086000000004, -0.03579615499999994], [0.01165086000000004, -0.019146044999999945], [-0.006196199999999985, -0.019146044999999945], [-0.006196199999999985, -0.041633534999999944], [-0.013229789999999964, -0.05206423499999996], [-0.033051549999999985, -0.05206423499999996], [-0.033051549999999985, -0.06003963499999998], [-0.06933539999999999, -0.06003963499999998], [-0.06933539999999999, -0.05206423499999996], [-0.22026484999999996, -0.05206423499999996]], 'holes': []}], 'simplify_tolerance': 9.090023200000001e-05, 'sketch_entity_count': 40}
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
