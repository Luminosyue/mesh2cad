#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.03887429, -0.01815924000000002, -0.2111719], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.29384103, 'zmax': 0.29384103, 'profiles': [{'outer': [[-0.21473470000000003, -0.01089544], [-0.23994371, -0.010651279999999999], [-0.24269047000000002, -0.006500640000000002], [-0.23994371, -0.0024110300000000015], [-0.21473470000000003, -0.002166879999999996], [0.04598130832034649, -0.002166879999999996], [0.04468042, -0.0014954499999999954], [0.04315447, 3.051999999999916e-05], [0.042177820000000005, 0.0019227200000000028], [0.04187263999999999, 0.00405908], [0.042177820000000005, 0.006195449999999998], [0.04315447, 0.008087650000000002], [0.04468042, 0.009613620000000003], [0.046572630000000004, 0.01059024], [0.04870896999999999, 0.01089544], [0.06274793000000001, 0.009796730000000003], [0.06451804, 0.00949154], [0.06610506999999999, 0.008698040000000004], [0.06738686999999999, 0.007416220000000001], [0.06818036999999999, 0.005829210000000001], [0.06848557999999999, 0.00405908], [0.06818036999999999, 0.0022889599999999996], [0.06738686999999999, 0.0007019499999999998], [0.06610506999999999, -0.0005798699999999962], [0.06451804, -0.0013733699999999988], [0.06274793000000001, -0.0016785699999999973], [0.05650840641976884, -0.002166879999999996], [0.22450087, -0.002166879999999996], [0.23890604999999998, -0.0032045399999999988], [0.24110344, -0.0042422000000000015], [0.24226319999999998, -0.005035699999999997], [0.24269047, -0.006500640000000002], [0.24226319999999998, -0.00802661], [0.24110344, -0.008820119999999997], [0.23890604999999998, -0.00985778], [0.22450087, -0.01089544]], 'holes': []}], 'simplify_tolerance': 9.7076188e-05, 'sketch_entity_count': 42}
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
