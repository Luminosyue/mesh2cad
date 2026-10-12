#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.047769549999999994, -0.480030595, -0.08299788999999999], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.019969525000000043, 'zmax': 0.019969524999999988, 'profiles': [{'outer': [[-0.20336357000000002, -0.19147882], [-0.19563255, -0.19147882], [-0.19081053, -0.19438778], [-0.18792775000000003, -0.19920979], [-0.18792775000000003, -0.20694077], [-0.19081053, -0.21178898000000002], [-0.19563255, -0.21467173], [-0.20336357000000002, -0.21467173], [-0.20821169000000003, -0.21178898000000002], [-0.21109440999999998, -0.20694077], [-0.21109440999999998, -0.19920979], [-0.20821169000000003, -0.19438778]], 'holes': []}, {'outer': [[-0.21109440999999998, 0.19920981], [-0.21109440999999998, 0.20694076], [-0.20821169000000003, 0.211789], [-0.20336357000000002, 0.21467173], [-0.19563255, 0.21467173], [-0.19081053, 0.211789], [-0.18792775000000003, 0.20694076], [-0.18792775000000003, 0.19920981], [-0.19081053, 0.19438777999999998], [-0.19563255, 0.19147883999999998], [-0.20336357000000002, 0.19147883999999998], [-0.20821169000000003, 0.19438777999999998]], 'holes': []}, {'outer': [[0.19563249, -0.19147882], [0.20336345, -0.19147882], [0.20821168999999998, -0.19438778], [0.21109440999999998, -0.19920979], [0.21109440999999998, -0.20694077], [0.20821168999999998, -0.21178898000000002], [0.20336345, -0.21467173], [0.19563249, -0.21467173], [0.19081047, -0.21178898000000002], [0.18790152999999998, -0.20694077], [0.18790152999999998, -0.19920979], [0.19081047, -0.19438778]], 'holes': []}, {'outer': [[0.19081047, 0.19438777999999998], [0.18790152999999998, 0.19920981], [0.18790152999999998, 0.20694076], [0.19081047, 0.211789], [0.19563249, 0.21467173], [0.20336345, 0.21467173], [0.20821168999999998, 0.211789], [0.21109440999999998, 0.20694076], [0.21109440999999998, 0.19920981], [0.20821168999999998, 0.19438777999999998], [0.20336345, 0.19147883999999998], [0.19563249, 0.19147883999999998]], 'holes': []}], 'simplify_tolerance': 8.586869200000001e-05, 'sketch_entity_count': 66}
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
