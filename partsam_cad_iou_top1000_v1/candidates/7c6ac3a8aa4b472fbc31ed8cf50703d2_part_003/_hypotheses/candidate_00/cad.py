#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.00265352499999999, -0.19034632, 0.368705155], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.286852165, 'zmax': 0.286852165, 'profiles': [{'outer': [[-0.1274733818635695, 0.03720293995325784], [-0.127388055, 0.04318497000000002], [-0.10938167500000001, 0.08005244000000002], [-0.08075442500000002, 0.10861864000000002], [-0.07123531989165996, 0.11345885912837818], [-0.04474148499999997, 0.12821211000000002], [-0.04004147499999999, 0.12931081], [-0.03778305500000001, 0.12998224000000003], [0.0021363850000000184, 0.13626925], [0.04205578500000001, 0.12998224000000003], [0.078068735, 0.11160954000000001], [0.10663485500000003, 0.08304334000000001], [0.125007605, 0.04703042000000002], [0.131294605, 0.007111020000000023], [0.131294605, 0.00534088000000002], [0.1304900711576074, 0.00023247912305630238], [0.130501065, -0.0008850599999999931], [0.1304063906846274, -0.0013678295660056075], [0.131294605, -0.007111039999999985], [0.125007605, -0.04703043999999998], [0.10663485500000003, -0.08304338], [0.078068735, -0.11160956], [0.04205578500000001, -0.12992124], [0.0021363850000000184, -0.13626925], [-0.03778305500000001, -0.12992124], [-0.073796005, -0.11160956], [-0.10242321500000001, -0.08304338], [-0.1141830597375581, -0.05991566715364282], [-0.12128418499999999, -0.04690839999999999], [-0.131294605, -0.0083318], [-0.12940233499999998, 0.033418750000000025]], 'holes': []}], 'simplify_tolerance': 5.450770000000001e-05, 'sketch_entity_count': 34}
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
