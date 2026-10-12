#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.05112561, 0.010510814999999979, -0.08855230999999998], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.26807151, 'zmax': 0.26807151, 'profiles': [{'outer': [[-0.26807152, 2.150000000204072e-07], [-0.26738424, 0.03083889500000002], [-0.26538797, 0.061519425000000016], [-0.2620172, 0.09167276500000002], [-0.25737015999999996, 0.12114085500000002], [-0.25144679999999997, 0.14966002500000003], [-0.24431257, 0.17707216500000003], [-0.23600028, 0.20311370500000003], [-0.22677164, 0.22736291500000003], [-0.21780479999999997, 0.248291065], [-0.21024519999999997, 0.26452745499999997], [-0.19869304, 0.28772236500000004], [-0.19754764999999996, 0.28930379500000003], [-0.19470052, 0.289514735], [0.19470103000000005, 0.28951443500000007], [0.19754814000000004, 0.28930349499999997], [0.19869356000000005, 0.28772206499999997], [0.21024566000000006, 0.26452709500000005], [0.21780525, 0.24829070500000003], [0.22677203, 0.22736256500000002], [0.23600064000000004, 0.20311331500000002], [0.24431293000000004, 0.177071785], [0.25144707000000005, 0.14965960500000003], [0.25737034000000003, 0.12114043500000002], [0.26201733000000005, 0.09167234500000002], [0.26538806000000004, 0.06151899500000002], [0.26738431, 0.030838465000000023], [0.26807152, -2.1499999997877384e-07], [0.26738425000000005, -0.03089163499999998], [0.26538794000000004, -0.061519434999999976], [0.26201721000000006, -0.09167280499999998], [0.25737016, -0.12114087499999998], [0.25144683, -0.14966006499999998], [0.24431263000000003, -0.177072195], [0.23600032000000004, -0.20311376499999997], [0.22683711, -0.227310255], [0.21813212000000004, -0.247711205], [0.21112882000000005, -0.262787895], [0.19898762000000003, -0.2871425249999999], [0.19767855, -0.289198445], [0.19548597, -0.289514735], [0.16730924000000003, -0.289514735], [-0.19548642, -0.28951443499999996], [-0.19767902999999998, -0.28919814499999996], [-0.19898805999999997, -0.287142225], [-0.21112920999999998, -0.26278753499999996], [-0.21813247999999996, -0.24771085499999998], [-0.22683744, -0.22730989499999998], [-0.23600061, -0.20311337499999998], [-0.24431286999999996, -0.17707180499999997], [-0.25144703999999996, -0.14965964499999998], [-0.25737034, -0.12114045499999998], [-0.26201732, -0.09167238499999998], [-0.26538808999999997, -0.06151900499999998], [-0.26738429999999996, -0.03089120499999998]], 'holes': []}], 'simplify_tolerance': 0.00011580589400000001, 'sketch_entity_count': 61}
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
