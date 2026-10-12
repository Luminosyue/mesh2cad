#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.003980145000000004, -0.178725075, 0.25214515], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.010906239999999984, 'zmax': 0.010906240000000011, 'profiles': [{'outer': [[-0.018068744999999997, -0.14952628499999998], [-0.018068744999999997, -0.141006065], [-0.016709925000000014, -0.138472035], [-0.015791785000000003, -0.137994605], [-0.013478115000000013, -0.137994605], [-0.013478115000000013, -0.134542455], [-0.009181275000000017, -0.134542455], [-0.009181275000000017, -0.137994605], [-0.007320725, -0.137994605], [-0.007320725, 0.13799463499999998], [-0.009181275000000017, 0.13799463499999998], [-0.009181275000000017, 0.134542485], [-0.013478115000000013, 0.134542485], [-0.013478115000000013, 0.13799463499999998], [-0.015791785000000003, 0.13799463499999998], [-0.016709925000000014, 0.138472035], [-0.018068744999999997, 0.141006065], [-0.018068744999999997, 0.14952628499999998], [-0.016709925000000014, 0.152060315], [-0.015791785000000003, 0.152537775], [-0.013478115000000013, 0.152537775], [-0.013478115000000013, 0.16234336500000002], [-0.009181275000000017, 0.16234336500000002], [-0.009181275000000017, 0.152537775], [-0.007320725, 0.152537775], [-0.007320725, 0.15943036500000002], [0.006993054999999998, 0.15943036500000002], [0.006993054999999998, 0.152537775], [0.008960934999999975, 0.152537775], [0.008960934999999975, 0.16234336500000002], [0.013257764999999977, 0.16234336500000002], [0.013257764999999977, 0.152537775], [0.015791794999999997, 0.152537775], [0.016709924999999987, 0.152060315], [0.018068744999999997, 0.14952628499999998], [0.018068744999999997, 0.141006065], [0.016709924999999987, 0.138472035], [0.015791794999999997, 0.13799463499999998], [0.013257764999999977, 0.13799463499999998], [0.013257764999999977, 0.134542485], [0.008960934999999975, 0.134542485], [0.008960934999999975, 0.13799463499999998], [0.006993054999999998, 0.13799463499999998], [0.006993054999999998, -0.137994605], [0.008960934999999975, -0.137994605], [0.008960934999999975, -0.134542455], [0.013257764999999977, -0.134542455], [0.013257764999999977, -0.137994605], [0.015791794999999997, -0.137994605], [0.016709924999999987, -0.138472035], [0.018068744999999997, -0.141006065], [0.018068744999999997, -0.14952628499999998], [0.016709924999999987, -0.152060315], [0.015791794999999997, -0.152537745], [0.013257764999999977, -0.152537745], [0.013257764999999977, -0.16234336500000002], [0.008960934999999975, -0.16234336500000002], [0.008960934999999975, -0.152537745], [0.006993054999999998, -0.152537745], [0.006993054999999998, -0.15778510499999998], [-0.007320725, -0.15778510499999998], [-0.007320725, -0.152537745], [-0.009181275000000017, -0.152537745], [-0.009181275000000017, -0.16234336500000002], [-0.013478115000000013, -0.16234336500000002], [-0.013478115000000013, -0.152537745], [-0.015791785000000003, -0.152537745], [-0.016709925000000014, -0.152060315]], 'holes': []}], 'simplify_tolerance': 6.4937346e-05, 'sketch_entity_count': 71}
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
