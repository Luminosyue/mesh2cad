#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.22593998999999998, 0.187478695, -9.644999999999099e-06], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.107800455, 'zmax': 0.10780045499999999, 'profiles': [{'outer': [[-0.03924728500000001, 0.026256379999999968], [-0.033392204999999994, 0.03339218999999999], [-0.026256345, 0.039308309999999985], [-0.018083645000000002, 0.04363864999999997], [-0.009179035, 0.04632216999999997], [3.0494999999999097e-05, 0.04723703999999998], [0.009240044999999999, 0.04632216999999997], [0.018083645, 0.04363864999999997], [0.026256355, 0.039308309999999985], [0.033392225, 0.03339218999999999], [0.03930829499999999, 0.026256379999999968], [0.043638605, 0.01808362999999999], [0.04632217499999999, 0.009240089999999979], [0.047237025, 3.0459999999982168e-05], [0.04632217499999999, -0.009179050000000022], [0.043638605, -0.018083630000000017], [0.03930829499999999, -0.02625632], [0.033392225, -0.033392190000000044], [0.026256355, -0.03924727], [0.018083645, -0.04363859000000003], [0.009240044999999999, -0.046322169999999996], [3.0494999999999097e-05, -0.04723704000000001], [-0.009179035, -0.046322169999999996], [-0.018083645000000002, -0.04363859000000003], [-0.026256345, -0.03924727], [-0.033392204999999994, -0.033392190000000044], [-0.03924728500000001, -0.02625632], [-0.043638605, -0.018083630000000017], [-0.046322155000000004, -0.009179050000000022], [-0.047237025, 3.0459999999982168e-05], [-0.046322155000000004, 0.009240089999999979], [-0.043638605, 0.01808362999999999]], 'holes': []}], 'simplify_tolerance': 1.8894815999999998e-05, 'sketch_entity_count': 35}
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
