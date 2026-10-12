#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0, -0.13199999, 0.41068737499999997], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.13312081, 'zmax': 0.13312081, 'profiles': [{'outer': [[-0.04940803500000002, 0.009822790000000012], [-0.04654399500000006, 0.01928176000000001], [-0.04188419500000001, 0.02798215000000001], [-0.03562982500000006, 0.035629830000000015], [-0.027997595000000042, 0.04188420000000001], [-0.019281725000000027, 0.046544030000000014], [-0.009838235000000028, 0.049408030000000006], [-7.735000000008707e-06, 0.05038334000000001], [0.00982280499999999, 0.04940802000000001], [0.01928176499999995, 0.04654401000000001], [0.027982164999999948, 0.041884190000000016], [0.03562982499999995, 0.03562981000000001], [0.04188420499999995, 0.027982130000000008], [0.046544034999999984, 0.01928173000000001], [0.04940803499999996, 0.009822760000000014], [0.05038334499999997, -7.759999999995548e-06], [0.04940803499999996, -0.009838279999999977], [0.046544004999999944, -0.019281769999999976], [0.04188420499999995, -0.02799763999999999], [0.03562982499999995, -0.03562983], [0.027982134999999964, -0.04188420999999998], [0.019281734999999967, -0.04654401999999999], [0.00982277499999995, -0.04940802999999999], [-7.765000000048428e-06, -0.05038334], [-0.009838265000000013, -0.04940802999999999], [-0.01928175500000001, -0.04654401], [-0.027997625000000026, -0.04188418999999999], [-0.03562982500000006, -0.03562981999999998], [-0.04188419500000001, -0.02799762], [-0.046544025000000044, -0.01928173999999999], [-0.04940803500000002, -0.009838249999999993], [-0.050383345000000024, -7.729999999983583e-06]], 'holes': []}], 'simplify_tolerance': 2.0153338e-05, 'sketch_entity_count': 35}
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
