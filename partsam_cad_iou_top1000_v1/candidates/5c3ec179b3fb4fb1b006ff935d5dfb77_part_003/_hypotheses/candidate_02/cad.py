#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-1.2686409950000002, 4.72080994, 14.33284378], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -2.788905625, 'zmax': 2.788905625, 'profiles': [{'outer': [[-3.9889984100000024, 1.1554183900000004], [-2.6314430200000007, 1.2126007000000003], [-1.1993722900000012, 1.6211776700000007], [-0.9318113300000004, 2.6508636400000007], [-0.8141211054296168, 2.64598796512959], [-0.5655841800000001, 2.6642227100000007], [-0.4325828773892354, 2.6578158931145204], [-0.23886108000000128, 2.67012024], [0.9309115867203324, 2.6494965661513303], [1.0614108999999985, 2.6521301200000007], [2.374010075712687, 2.6473325207649485], [5.4368152599999995, 2.6470489500000003], [5.61370468, 2.64282226], [5.59078789, 1.4194030700000004], [5.560707089999999, 0.45732879000000004], [5.5206298799999995, 0.039886470000000784], [5.31627464, -1.3204498299999998], [4.853935239999998, -1.9299087599999996], [3.817604059999999, -2.3565826499999996], [3.6925125099999985, -2.3890152], [2.308633799999999, -2.5783309999999995], [1.0958461799999988, -2.6306838999999997], [-0.13558579000000037, -2.6581039499999997], [-1.385731700000001, -2.6701202399999997], [-2.625370030000001, -2.6632309], [-4.12947846, -2.4765853899999994], [-5.091732030000001, -2.21851349], [-5.61370468, -1.1060714799999998], [-5.275432589999999, 0.5275726300000008], [-4.453048709999999, 0.9006500200000005]], 'holes': []}], 'simplify_tolerance': 0.002245481872, 'sketch_entity_count': 39}
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
