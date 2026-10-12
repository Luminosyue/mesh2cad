#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.33903194000000003, 0.08800563, -0.154320645], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.11423720999999998, 'zmax': 0.11423721000000003, 'profiles': [{'outer': [[-0.203903845, 0.01955408], [-0.192829745, 0.03613711], [-0.17624667500000002, 0.04721122999999999], [-0.156687625, 0.05110437000000001], [-0.13713482500000002, 0.04721122999999999], [-0.12055174500000002, 0.03613711], [-0.10947764500000001, 0.01955408], [-0.105584555, 1.2499999999943112e-06], [-0.10947764500000001, -0.019557770000000002], [-0.12055174500000002, -0.036140860000000004], [-0.13713482500000002, -0.04721495], [-0.156687625, -0.051108060000000004], [-0.17624667500000002, -0.04721495], [-0.192829745, -0.036140860000000004], [-0.203903845, -0.019557770000000002], [-0.207796945, 1.2499999999943112e-06]], 'holes': []}, {'outer': [[0.11285693500000002, -0.04346585], [0.10138602500000002, -0.0401634], [0.09166170499999998, -0.030736529999999998], [0.085171195, -0.016634339999999997], [0.08288311500000001, 0.0], [0.085171195, 0.016634289999999996], [0.09166170499999998, 0.030736509999999995], [0.10138602500000002, 0.04015577000000001], [0.11285693500000002, 0.04346585], [0.14061971941808113, 0.04346585], [0.144485785, 0.047210699999999994], [0.15797026499999997, 0.05110806000000001], [0.172560525, 0.05110806000000001], [0.186044945, 0.047210699999999994], [0.19747771499999997, 0.036136390000000004], [0.20511229499999997, 0.019555450000000002], [0.20779694499999998, 0.0], [0.20511229499999997, -0.019563079999999997], [0.19747771499999997, -0.036136390000000004], [0.186044945, -0.04721832], [0.172560525, -0.051108060000000004], [0.15797026499999997, -0.051108060000000004], [0.144485785, -0.04721832], [0.1406145165077879, -0.04346585]], 'holes': []}], 'simplify_tolerance': 8.311877800000001e-05, 'sketch_entity_count': 40}
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
