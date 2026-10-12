#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.14453336, 0.020825089999999997, 0.41805598], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.027781379999999998, 'zmax': 0.02778138, 'profiles': [{'outer': [[-0.05818146000000002, -0.04059040999999999], [-0.06142649, -0.038142449999999994], [-0.06239425999999998, -0.03512522000000001], [-0.06040173999999998, -0.030912460000000003], [-0.054993479999999983, -0.02516262999999999], [-0.04856046999999997, -0.021017301869102674], [-0.04856046999999997, -0.01679407999999999], [-0.04200657905137791, -0.01679407999999999], [-0.03370198000000002, -0.011442730000000012], [-0.032278799999999996, -0.01043272976665873], [-0.032278799999999996, 0.0030172400000000044], [-0.013326598465165668, 0.0030172400000000044], [-0.009222510000000017, 0.005929823304620998], [-0.009222510000000017, 0.021633040000000006], [0.024823991430243292, 0.021633040000000006], [0.033627491424706814, 0.026265414852439505], [0.045941710000000024, 0.03495444], [0.06239425999999998, 0.042184429999999995], [0.05949089000000002, 0.0274398], [0.04895902000000002, 0.005863690000000005], [0.04662493000000001, 0.0023910199999999937], [0.03284806000000001, -0.016053979999999995], [0.02527651000000003, -0.022600819999999994], [0.01639560000000001, -0.028464519999999993], [-0.0029602599999999923, -0.03597916000000001], [-0.010987250000000004, -0.03916718999999999], [-0.022316159999999974, -0.04110277000000001], [-0.03210792000000001, -0.042184429999999995], [-0.04081812000000001, -0.042184429999999995], [-0.052092418907810606, -0.04088135842505975], [-0.05698597, -0.04098890999999999]], 'holes': []}], 'simplify_tolerance': 2.4957703999999994e-05, 'sketch_entity_count': 34}
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
