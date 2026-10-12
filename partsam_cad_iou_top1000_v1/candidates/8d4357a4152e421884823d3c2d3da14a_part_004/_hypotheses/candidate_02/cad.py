#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.06596486, -0.46588063, -0.013473035000000001], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.034119279999999974, 'zmax': 0.03411928000000003, 'profiles': [{'outer': [[-0.07698923499999999, 0.015303339999999999], [-0.069429995, 0.028244449999999997], [-0.046136025, 0.04192503], [0.0005340750000000019, 0.0532639], [0.033646835, 0.0561397], [0.058255455000000005, 0.05642729], [0.07394909499999999, 0.05034702], [0.07920770499999999, 0.03896708], [0.074195595, 0.027751449999999997], [0.060350675, 0.02199985], [0.051517865, 0.01932946], [0.060350675, 0.016618], [0.074195595, 0.01115398], [0.07920770499999999, 0.0009243500000000043], [0.074195595, -0.009305270000000004], [0.060350675, -0.014769299999999999], [0.05153255406826022, -0.01772232091054041], [0.060350675, -0.020931710000000006], [0.074195595, -0.027381729999999993], [0.07920770499999999, -0.0391725], [0.07394909499999999, -0.05075786], [0.058255455000000005, -0.056427290000000005], [0.033646835, -0.05564672], [0.0005340750000000019, -0.052442260000000004], [-0.046136025, -0.033215480000000006], [-0.069429995, -0.019288390000000002], [-0.07698923499999999, -0.0060597200000000045], [-0.07920770499999999, 0.004662890000000003]], 'holes': []}], 'simplify_tolerance': 3.1683082e-05, 'sketch_entity_count': 31}
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
