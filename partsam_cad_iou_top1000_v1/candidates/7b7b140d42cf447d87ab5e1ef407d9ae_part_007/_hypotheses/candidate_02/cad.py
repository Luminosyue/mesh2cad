#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.22593998999999998, 0.187478695, -9.644999999999099e-06], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.04723704000000001, 'zmax': 0.04723703999999998, 'profiles': [{'outer': [[-0.047115055, -0.098407895], [-0.046932085, -0.098285945], [-0.046932085, -0.092369885], [-0.047237025, -0.092308915], [-0.047237025, -0.091516055], [-0.046993065, -0.091455015], [-0.04474800424690655, -0.091455015], [-0.042357795000000004, -0.087063705], [-0.035526875, -0.069254555], [-0.008508114999999998, 0.01161864500000001], [-0.009118024999999998, 0.01161864500000001], [-0.009483954999999999, 0.011923634999999988], [-0.002226094999999999, 0.03168448500000001], [-0.002226094999999999, 0.036014825], [-0.001982134999999999, 0.03613677500000001], [-0.0007013336517114737, 0.03631969500000001], [-0.0007013049999999991, 0.098529905], [-0.009117984999999999, 0.098529905], [-0.009117974999999999, 0.099810745], [-0.0007013049999999991, 0.099810745], [-0.0007012949999999991, 0.10780045499999999], [0.0007014650000000009, 0.10780045499999999], [0.0007014650000000009, 0.099810745], [0.009118135000000001, 0.099810745], [0.009118135000000001, 0.098529905], [0.0007014650000000009, 0.098529905], [0.0007014267977180348, 0.03631969500000001], [0.0010063950000000009, 0.03631969500000001], [0.001921245000000001, 0.03613677500000001], [0.0021652050000000008, 0.036014825], [0.0021652050000000008, 0.03168448500000001], [0.009484035, 0.011923634999999988], [0.009118095000000001, 0.01161864500000001], [0.008508185000000001, 0.01161864500000001], [0.024182675, -0.035587885000000014], [0.035526865000000005, -0.069254555], [0.042357795000000004, -0.087063705], [0.04474796779133961, -0.091455015], [0.046932075000000004, -0.091455015], [0.047237025, -0.091516055], [0.047237025, -0.092308915], [0.046932075000000004, -0.092369885], [0.046932075000000004, -0.098285945], [0.047054055, -0.098407895], [0.046932075000000004, -0.098895825], [0.043943545, -0.098895825], [0.043943535000000006, -0.102311285], [0.042906694999999995, -0.102311285], [0.042906694999999995, -0.107800455], [-0.042967715000000004, -0.107800455], [-0.042967715000000004, -0.102311285], [-0.043943554999999995, -0.102311285], [-0.043943554999999995, -0.098895825], [-0.046932085, -0.098895825]], 'holes': []}], 'simplify_tolerance': 4.3120182e-05, 'sketch_entity_count': 54}
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
