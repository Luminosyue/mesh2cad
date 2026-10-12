#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.11559052, 0.150696425, 0.02161631], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.104759335, 'zmax': 0.10475933499999998, 'profiles': [{'outer': [[-0.09860634, -0.0036978800000000006], [-0.09883553, 1.8199999999995997e-06], [-0.09860634, 0.0036978599999999973], [-0.09795153, 0.007226579999999996], [-0.09695476, 0.010464260000000003], [-0.09571425, 0.013327249999999985], [-0.09434278, 0.015793699999999994], [-0.09292766, 0.01787820000000001], [-0.09152345, 0.019624360000000007], [-0.09018108, 0.021072229999999997], [-0.08874413, 0.022425499999999987], [-0.08701616, 0.023840609999999984], [-0.08494622, 0.02527029], [-0.08250160000000001, 0.026652690000000007], [-0.07966407, 0.02790047000000001], [-0.07645549, 0.02890814], [-0.07295225, 0.029570230000000003], [-0.06928893, 0.029799419999999993], [-0.06562198999999999, 0.029570230000000003], [-0.06212237, 0.02890814], [-0.0589138, 0.02790047000000001], [-0.05607264, 0.026652690000000007], [-0.05362801, 0.02527029], [-0.05155807, 0.02384063], [-0.0498301, 0.022425499999999987], [-0.048393149999999996, 0.021072229999999997], [-0.04705078, 0.019624360000000007], [-0.04565021, 0.01787820000000001], [-0.04423144, 0.015793699999999994], [-0.04285999, 0.013327249999999985], [-0.04161948, 0.010464260000000003], [-0.04094588974457691, 0.00827635197388022], [0.09883552, 0.008276369999999991], [0.09883552, -0.021087560000000005], [-0.04840944797912547, -0.02108757898861541], [-0.0498301, -0.022425509999999996], [-0.05155808, -0.02384063], [-0.05362801, -0.025270310000000004], [-0.05607265, -0.026652690000000007], [-0.0589138, -0.027900460000000002], [-0.06212238, -0.028908160000000002], [-0.06562198999999999, -0.029570239999999998], [-0.06928895, -0.029799420000000007], [-0.07295225, -0.029570239999999998], [-0.07645550000000001, -0.028908160000000002], [-0.07966408, -0.027900460000000002], [-0.08250160000000001, -0.026652690000000007], [-0.08494624, -0.025270310000000004], [-0.08701617, -0.02384063], [-0.08874415, -0.022425509999999996], [-0.09018108, -0.021072229999999997], [-0.09152346, -0.019624370000000002], [-0.09292767, -0.017878199999999997], [-0.09434279, -0.015793719999999997], [-0.09571425, -0.013327260000000007], [-0.09695476, -0.010464269999999998], [-0.09795153, -0.007226590000000005]], 'holes': []}], 'simplify_tolerance': 3.9534212000000005e-05, 'sketch_entity_count': 78}
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
