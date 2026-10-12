#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.271797715, -0.09506701, -0.019491790000000002], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.028470424999999994, 'zmax': 0.02847042500000002, 'profiles': [{'outer': [[-0.025368650000000003, -0.007456530000000003], [-0.02292635718145887, -0.006428204744813782], [-0.02011005, -0.001992540000000001], [-0.01649476, 0.005238039999999999], [-0.01670017, 0.016864519999999994], [-0.022086424490996855, 0.02221310177190406], [-0.02565622, 0.02216417999999999], [-0.028314611448547328, 0.020385263349473364], [-0.032270560000000004, 0.013372469999999997], [-0.03522852, 0.010291259999999997], [-0.039501140000000004, 0.00803168], [-0.04307535, 0.007867379999999993], [-0.04591006, 0.00922315], [-0.047142550000000005, 0.012263219999999991], [-0.04635771470176199, 0.018028720497702565], [-0.04664954, 0.023889709999999995], [-0.042869920000000006, 0.03354413999999999], [-0.03276355, 0.03909028999999999], [-0.021917680000000002, 0.04237691999999999], [-0.006470530000000002, 0.04422564999999999], [0.0022801099999999984, 0.045334889999999996], [0.01074317, 0.04447213999999999], [0.018918649999999995, 0.04299316999999999], [0.02672439, 0.039501119999999994], [0.028860699999999996, 0.038515139999999996], [0.03633778, 0.032763589999999995], [0.04340401, 0.023848549999999996], [0.04714255, 0.014153019999999988], [0.045910059999999996, 0.004046659999999994], [0.04492408, 0.00039027999999999285], [0.04011738, -0.016576900000000006], [0.03580368, -0.027710330000000005], [0.03210623, -0.033420870000000005], [0.026354619999999995, -0.042007190000000014], [0.0242594, -0.04443107], [0.01694665, -0.04525272000000001], [0.015549839999999995, -0.04533489], [0.009592829999999997, -0.04134984000000001], [0.009140919999999997, -0.039501120000000015], [0.008689009999999997, -0.033215449999999994], [0.008812259999999999, -0.031161320000000006], [0.009092976613774844, -0.03030794783503798], [0.008647929999999998, -0.030832630000000014], [0.006182959999999998, -0.033996029999999997], [0.00026701999999999976, -0.04011737], [-0.0010065400000000002, -0.04040493000000002], [-0.007292210000000002, -0.03991193999999999], [-0.011811320000000002, -0.03559826000000001], [-0.012098900000000003, -0.03391387], [-0.011605910000000002, -0.028326590000000013], [-0.011071830000000001, -0.02602597000000001], [-0.009305270000000003, -0.022657200000000002], [-0.0065797491590871395, -0.01923280759740084], [-0.006511630000000003, -0.018836480000000003], [-0.006881380000000001, -0.014235210000000012], [-0.010003670000000003, -0.016864520000000008], [-0.012920560000000001, -0.020890610000000004], [-0.015385530000000001, -0.023314520000000005], [-0.0173575, -0.02446480000000001], [-0.023355590000000002, -0.026601150000000004], [-0.024752410000000002, -0.026765480000000008], [-0.030462920000000004, -0.02335559000000001], [-0.03255815, -0.01702882], [-0.032311650000000004, -0.015878510000000012], [-0.02910719, -0.010537760000000007], [-0.02795687, -0.009223120000000001]], 'holes': []}], 'simplify_tolerance': 1.8857020000000004e-05, 'sketch_entity_count': 84}
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
