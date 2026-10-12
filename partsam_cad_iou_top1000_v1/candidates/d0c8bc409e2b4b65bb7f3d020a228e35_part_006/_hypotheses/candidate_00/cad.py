#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.051125665, 0.381224095, -0.088552515], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.08390283500000001, 'zmax': 0.08390283500000001, 'profiles': [{'outer': [[-0.19392483500000002, 0.038582245], [-0.18919407500000002, 0.057384595], [-0.182653085, 0.075655915], [-0.17437424499999998, 0.093203195], [-0.16438173500000003, 0.109833255], [-0.152844475, 0.12542543499999997], [-0.139810765, 0.13981081499999998], [-0.125425385, 0.15284451500000001], [-0.109833235, 0.164381795], [-0.09320314500000002, 0.174374305], [-0.075655895, 0.18265313500000002], [-0.057384555000000004, 0.189194125], [-0.038582225, 0.193924885], [-0.019369545000000002, 0.196773005], [1.2064999999991666e-05, 0.19771430499999998], [0.019369565000000005, 0.196773005], [0.038582214999999996, 0.193924885], [0.057384565, 0.189194125], [0.075655905, 0.18265313500000002], [0.093203155, 0.174374305], [0.109833205, 0.164381795], [0.125425405, 0.15284451500000001], [0.139810755, 0.13981081499999998], [0.15284447499999998, 0.12542543499999997], [0.164381735, 0.109833255], [0.17437425499999998, 0.093203195], [0.182653075, 0.075655915], [0.18919407500000002, 0.057384595], [0.193924815, 0.038582245], [0.19677293499999998, 0.019369565000000005], [0.197714255, -1.2045000000002193e-05], [0.19677293499999998, -0.019369555000000004], [0.193924815, -0.038582215], [0.18919407500000002, -0.057384565], [0.182653075, -0.075655905], [0.17437425499999998, -0.093203165], [0.164381735, -0.109833225], [0.15284447499999998, -0.12542541499999998], [0.139810755, -0.139810795], [0.125425405, -0.152844495], [0.109833205, -0.164381745], [0.093203155, -0.17437428500000002], [0.075655905, -0.18265310499999998], [0.057384565, -0.189194105], [0.038582214999999996, -0.193924865], [0.019369565000000005, -0.19677296500000002], [1.2064999999991666e-05, -0.19771430499999998], [-0.019369545000000002, -0.19677296500000002], [-0.038582225, -0.193924865], [-0.057384555000000004, -0.189194105], [-0.075655895, -0.18265310499999998], [-0.09320314500000002, -0.17437428500000002], [-0.109833235, -0.164381745], [-0.125425385, -0.152844495], [-0.139810765, -0.139810795], [-0.152844475, -0.12542541499999998], [-0.16438173500000003, -0.109833225], [-0.17437424499999998, -0.093203165], [-0.182653085, -0.075655905], [-0.18919407500000002, -0.057384565], [-0.19392483500000002, -0.038582215], [-0.19677295500000003, -0.019369555000000004], [-0.197714255, -1.2045000000002193e-05], [-0.19677295500000003, 0.019369565000000005]], 'holes': []}], 'simplify_tolerance': 7.9085722e-05, 'sketch_entity_count': 67}
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
