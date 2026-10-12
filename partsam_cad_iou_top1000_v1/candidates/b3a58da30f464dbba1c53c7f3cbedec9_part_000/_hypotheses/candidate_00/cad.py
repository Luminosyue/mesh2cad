#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.04565291, 0.40542519, -1.1999999999234845e-07], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.017140939999999997, 'zmax': 0.01714094, 'profiles': [{'outer': [[-0.25919074, -0.09260564999999998], [-0.26113966, -0.08912313], [-0.26171476, -0.08640742000000001], [-0.26136329999999997, -0.08544891999999998], [-0.2551012, -0.08155107], [-0.22219313999999998, -0.06183826999999997], [-0.21960522, -0.058259899999999976], [-0.20938136999999998, -0.04637468], [-0.19529162, -0.03889847000000002], [-0.18190476, -0.025767209999999985], [-0.17177673999999998, -0.009952189999999972], [-0.16283086, 0.007779839999999982], [-0.15426837, 0.02595913999999999], [-0.14247896999999998, 0.043882790000000005], [-0.12790996999999998, 0.05883521000000003], [-0.11193521, 0.07065653999999999], [-0.09394760999999999, 0.0797621], [-0.07541685999999999, 0.08576857999999998], [-0.05653467999999999, 0.08998597000000003], [-0.03742882999999999, 0.09273362000000002], [-0.017971559999999994, 0.09413939999999998], [-1.5909999999992348e-05, 0.09458666999999998], [0.017971680000000007, 0.09413939999999998], [0.03742896000000001, 0.09273362000000002], [0.05653478000000001, 0.08998597000000003], [0.07541699, 0.08576857999999998], [0.09394771, 0.0797621], [0.11193529, 0.07065642], [0.12791008, 0.058835090000000034], [0.14247908, 0.04388267000000001], [0.15426846, 0.02595902], [0.16283092000000002, 0.00777971999999999], [0.17177682, -0.009952309999999964], [0.18190479, -0.025767329999999977], [0.19529165, -0.03889859000000001], [0.2093814, -0.046374799999999994], [0.21960528, -0.05826001999999997], [0.22219317, -0.061838389999999965], [0.25510120000000003, -0.08155124999999996], [0.26136333, -0.0854491], [0.26171476, -0.08640759999999997], [0.26113966, -0.08912331000000001], [0.25919074000000003, -0.09260583], [0.25727379, -0.09439498000000002], [0.25625139, -0.09455471999999998], [0.21714514000000001, -0.07091206], [0.21315145000000002, -0.06886726999999998], [0.19759202, -0.06292468000000001], [0.18206456000000001, -0.05394678999999997], [0.16608977, -0.03877079], [0.15458791, -0.021198510000000004], [0.14535454, -0.0022844100000000145], [0.13707958, 0.015319830000000034], [0.12704743000000002, 0.03081529999999999], [0.11458710000000001, 0.04369097999999999], [0.10046543000000001, 0.054202379999999994], [0.08538524, 0.061710600000000004], [0.06880342, 0.06679057999999999], [0.05151871000000001, 0.07024109], [0.03385060000000001, 0.07247757999999999], [0.016022760000000007, 0.07375556], [-1.5909999999992348e-05, 0.07413893999999999], [-0.01602263999999999, 0.07375556], [-0.03385049999999999, 0.07247757999999999], [-0.05151858999999999, 0.07024109], [-0.06880330999999999, 0.06679057999999999], [-0.08538512999999999, 0.061710600000000004], [-0.10046530999999999, 0.05420249999999999], [-0.11458702, 0.04369109999999998], [-0.12704736, 0.030815419999999982], [-0.13707951999999998, 0.015319880000000008], [-0.14535445, -0.0022843499999999906], [-0.15458787999999998, -0.02119839000000001], [-0.16608973, -0.03877067000000001], [-0.18206451999999998, -0.053946669999999974], [-0.19759200999999998, -0.06292456000000002], [-0.21315144, -0.06886714999999999], [-0.21714513, -0.07091194], [-0.2562514, -0.09455453999999996], [-0.25727376, -0.0943948]], 'holes': []}], 'simplify_tolerance': 0.000104685904, 'sketch_entity_count': 116}
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
