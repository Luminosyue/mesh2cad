#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.06199122999999998, -0.350624665, -0.047277894999999986], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.35615530500000003, 'zmax': 0.35615530500000003, 'profiles': [{'outer': [[-0.05761875500000002, -0.24089583999999997], [-0.05761875500000002, -0.15926573], [-0.057975604999999986, -0.15926573], [-0.057975604999999986, -0.07611815999999998], [-0.05355714500000003, -0.07611815999999998], [-0.028876194999999993, -0.06679029999999998], [-0.02851913500000003, -0.06451408999999998], [-0.024279225000000015, -0.06451408999999998], [-0.023877515000000016, -0.06670100999999998], [0.0017406449999999851, -0.06317518999999998], [0.027403485000000005, -0.06670100999999998], [0.02776052499999998, -0.06482649999999998], [0.03150953499999998, -0.06482649999999998], [0.03186656500000001, -0.06679029999999998], [0.05471764499999998, -0.07611815999999998], [0.057172375, -0.07611815999999998], [0.057172375, -0.15774827999999996], [0.05757384500000001, -0.15774827999999996], [0.05757384500000001, -0.24089583999999997], [0.055074524999999985, -0.24089583999999997], [0.03222344500000002, -0.2501791], [0.031866385, -0.25214285999999997], [0.028162014999999985, -0.25214285999999997], [0.02776034500000002, -0.25026835999999997], [0.002142144999999984, -0.25379421], [-0.023520664999999996, -0.25026835999999997], [-0.023877725000000016, -0.25245527999999995], [-0.02816228500000001, -0.25245527999999995], [-0.02851934500000003, -0.2501791], [-0.053200285000000014, -0.24089583999999997]], 'holes': []}, {'outer': [[-0.05797566500000001, 0.1577483], [-0.05797566500000001, 0.24089588000000003], [-0.053557205, 0.24089588000000003], [-0.028876255000000017, 0.25017913], [-0.028519194999999997, 0.25245531], [-0.024279284999999984, 0.25245531], [-0.023877574999999984, 0.25026841], [0.0017405950000000114, 0.25379421], [0.02740342499999998, 0.25026841], [0.027760465000000012, 0.25214292000000005], [0.03150947500000001, 0.25214292000000005], [0.031866534999999974, 0.25017913], [0.05471758500000001, 0.24089588000000003], [0.057172314999999974, 0.24089588000000003], [0.057172314999999974, 0.17796619000000002], [0.057440115000000014, 0.17796619000000002], [0.057797144999999994, 0.17685039000000002], [0.05797566500000001, 0.17452957000000002], [0.05775250500000001, 0.17234261], [0.057350824999999994, 0.17158397000000003], [0.057172314999999974, 0.17158397000000003], [0.057172314999999974, 0.1577483], [0.05471758500000001, 0.1577483], [0.031866534999999974, 0.14842041000000003], [0.03150947500000001, 0.14645667], [0.027760465000000012, 0.14645667], [0.02740342499999998, 0.14837582000000002], [0.0017405950000000114, 0.14484997000000002], [-0.023877574999999984, 0.14837582000000002], [-0.024279284999999984, 0.14614423], [-0.028519194999999997, 0.14614423], [-0.028876255000000017, 0.14842041000000003], [-0.053557205, 0.1577483]], 'holes': []}], 'simplify_tolerance': 0.00010151768400000002, 'sketch_entity_count': 63}
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
