#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.09779490999999998, 0.06325772, -0.32193441500000003], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.178062065, 'zmax': 0.17806206500000002, 'profiles': [{'outer': [[-0.03372127999999999, 0.004390850000000016], [-0.029775109999999994, 0.010957890000000012], [-0.027090647133578092, 0.013296421240919657], [-0.022407709999999997, 0.021096610000000016], [-0.014663789999999996, 0.027820760000000028], [-0.005214929999999993, 0.03183612000000002], [0.005014730000000002, 0.03272843], [0.015021290000000007, 0.03041800000000003], [0.02381685, 0.025127910000000017], [0.030541000000000006, 0.01738400000000001], [0.03393493, 0.009401050000000022], [0.03455637, 0.007935130000000012], [0.03544867, -0.002278559999999985], [0.03313824, -0.01228509999999998], [0.027864080000000006, -0.021080689999999985], [0.02010423, -0.027820759999999986], [0.010655370000000004, -0.03183611999999998], [0.000441640000000007, -0.03272842999999999], [-0.009564909999999996, -0.03041800999999998], [-0.011729287448176253, -0.029116246556036403], [-0.012724659999999999, -0.029203729999999983], [-0.020200059999999992, -0.027476349999999983], [-0.026767089999999993, -0.023545069999999987], [-0.03178543, -0.017752379999999984], [-0.03477854999999999, -0.010708829999999989], [-0.03544867, -0.0030696499999999793]], 'holes': []}], 'simplify_tolerance': 1.4179468000000001e-05, 'sketch_entity_count': 32}
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
