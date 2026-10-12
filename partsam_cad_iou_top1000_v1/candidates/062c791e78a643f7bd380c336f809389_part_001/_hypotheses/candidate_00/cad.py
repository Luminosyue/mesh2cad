#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.47353193, -0.01670366499999998, 0.023545325000000006], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.025040449999999992, 'zmax': 0.025040449999999992, 'profiles': [{'outer': [[-0.313749965, -0.060042915000000016], [-0.306873975, -0.04038954500000002], [-0.318622705, -0.02322669500000002], [-0.318622705, 0.02322670499999998], [-0.306873975, 0.04038955499999998], [-0.313749965, 0.05998878499999998], [-0.301730575, 0.10487207499999998], [-0.285975395, 0.11840745499999998], [-0.287545505, 0.13919781499999997], [-0.264318795, 0.17942494499999997], [-0.245531705, 0.18841242499999997], [-0.24168762500000002, 0.20887790499999997], [-0.208877895, 0.24168764499999998], [-0.188412415, 0.24553172499999998], [-0.17942492499999999, 0.264318795], [-0.13919779499999999, 0.28754553499999996], [-0.118461595, 0.285921245], [-0.10487206499999999, 0.301730605], [-0.059988765, 0.31374996499999996], [-0.040389545, 0.306874005], [-0.02322669499999999, 0.318622705], [0.023226705000000007, 0.318622705], [0.040389565, 0.306874005], [0.060042935000000006, 0.31374996499999996], [0.10492622500000001, 0.301730605], [0.11846160500000001, 0.285975425], [0.139197795, 0.28754553499999996], [0.179424925, 0.264318795], [0.188412415, 0.24553172499999998], [0.208877925, 0.24168764499999998], [0.241741795, 0.20887790499999997], [0.245585845, 0.18841242499999997], [0.264318795, 0.17942494499999997], [0.287545505, 0.13919781499999997], [0.285975395, 0.11840745499999998], [0.301730575, 0.10487207499999998], [0.313804145, 0.05998878499999998], [0.306874035, 0.04038955499999998], [0.318622705, 0.02322670499999998], [0.318622705, -0.02322669500000002], [0.306874035, -0.04038954500000002], [0.313804145, -0.060042915000000016], [0.301730575, -0.10492621500000002], [0.285975395, -0.11846159500000003], [0.287545505, -0.13919778500000002], [0.264318795, -0.17942491500000002], [0.245585845, -0.188412395], [0.241741795, -0.20887790500000003], [0.208877925, -0.24174177500000005], [0.188412415, -0.24558582500000004], [0.179424925, -0.264318795], [0.139197795, -0.287545475], [0.11846160500000001, -0.28597536500000004], [0.10492622500000001, -0.301730545], [0.060042935000000006, -0.31380412500000004], [0.040443715000000005, -0.306874005], [0.023226705000000007, -0.318622705], [-0.02322669499999999, -0.318622705], [-0.040389545, -0.306874005], [-0.059988765, -0.31380412500000004], [-0.10487206499999999, -0.301730545], [-0.118461595, -0.28597536500000004], [-0.13919779499999999, -0.287545475], [-0.17942492499999999, -0.264318795], [-0.188412415, -0.24558582500000004], [-0.208877895, -0.24174177500000005], [-0.24168762500000002, -0.20887790500000003], [-0.245531705, -0.188412395], [-0.264318795, -0.17942491500000002], [-0.287545505, -0.13919778500000002], [-0.285921215, -0.11846159500000003], [-0.301730575, -0.10492621500000002]], 'holes': []}], 'simplify_tolerance': 0.00012744908200000002, 'sketch_entity_count': 93}
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
