#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.037932635, -0.370401365, -0.36921236], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.10052486999999999, 'zmax': 0.10052487000000004, 'profiles': [{'outer': [[-0.12959851499999997, 0.025804994999999997], [-0.10987202499999998, 0.073400885], [-0.07340095499999999, 0.10987201499999999], [-0.025805034999999976, 0.129598495], [0.025747675000000025, 0.129598495], [0.073400935, 0.10987201499999999], [0.109872005, 0.073400885], [0.12959851500000003, 0.025804994999999997], [0.12959851500000003, -0.025747685], [0.109872005, -0.07340097500000001], [0.073400935, -0.109872045], [0.025747675000000025, -0.129598495], [-0.025805034999999976, -0.129598495], [-0.07340095499999999, -0.109872045], [-0.10987202499999998, -0.07340097500000001], [-0.12959851499999997, -0.025747685]], 'holes': [[[-0.015827044999999984, 0.07953676500000001], [-0.045072714999999985, 0.06743708500000001], [-0.067437095, 0.045072735], [-0.07953674499999996, 0.015827064999999998], [-0.07953674499999996, -0.015827084999999998], [-0.067437095, -0.045015455], [-0.045072714999999985, -0.06743711499999999], [-0.015827044999999984, -0.079536795], [0.015827015, -0.079536795], [0.045015355000000035, -0.06743711499999999], [0.06743707500000001, -0.045015455], [0.07953669499999999, -0.015827084999999998], [0.07953669499999999, 0.015827064999999998], [0.06743707500000001, 0.045072735], [0.045015355000000035, 0.06743708500000001], [0.015827015, 0.07953676500000001]]]}], 'simplify_tolerance': 5.1839406e-05, 'sketch_entity_count': 32}
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
