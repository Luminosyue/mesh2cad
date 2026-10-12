#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.002261474999999999, -0.064848975, -0.20692605], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.071188455, 'zmax': 0.071188455, 'profiles': [{'outer': [[-0.20633179, 0.271489205], [-0.16737055, 0.295317335], [-0.13706737, 0.295835365], [-0.08467503, 0.29949836500000004], [-0.019221640000000012, 0.302939405], [0.04538080000000003, 0.30308739500000004], [0.09747711, 0.30071942500000004], [0.12541228000000001, 0.296686395], [0.13225733999999997, 0.294577345], [0.12548627999999998, 0.25561612499999997], [0.1291863, 0.216173845], [0.15057245, 0.122970275], [0.15634446999999999, 0.097033115], [0.16222751, 0.068838935], [0.16877654, 0.035464735000000004], [0.17569559999999998, -0.0017574949999999978], [0.18261461999999998, -0.041680764999999995], [0.18927467, -0.08293600500000001], [0.19534272, -0.12437625499999999], [0.20033774000000001, -0.160969495], [0.20374176000000002, -0.18772067499999998], [0.20633179, -0.238410965], [0.13869536000000002, -0.265791165], [0.09570110000000001, -0.253803055], [0.05833086000000001, -0.26723416499999997], [0.02477164000000001, -0.278075235], [-0.03461371999999999, -0.30308739500000004], [-0.05374286, -0.236782955], [-0.02469692610787167, -0.23012052980313816], [-0.016705620000000004, -0.158379475], [-0.015299609999999991, -0.091557055], [-0.01737163, -0.035020714999999994], [-0.022514640000000002, 0.012783595000000002], [-0.030247689999999994, 0.053409865], [-0.04023776000000001, 0.088486085], [-0.05207782999999999, 0.119529275], [-0.0659159, 0.148352455], [-0.08204802, 0.17687962499999998], [-0.10073314, 0.206886795], [-0.17284660000000002, 0.235857975], [-0.17954363, 0.239299015], [-0.18546368, 0.243961055], [-0.19045868999999999, 0.249585105]], 'holes': []}], 'simplify_tolerance': 0.00012123495800000002, 'sketch_entity_count': 43}
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
