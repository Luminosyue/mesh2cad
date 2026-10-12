#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0077239000000000006, 0.022211440000000002, -0.45114124], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.028063120000000004, 'zmax': 0.028063120000000004, 'profiles': [{'outer': [[-0.048858579999999985, 0.04513671], [-0.048858579999999985, 0.06856339], [-0.007248109999999974, 0.06698859], [0.010172720000000024, 0.06699838], [0.01161063000000001, 0.06859276], [0.03067475000000003, 0.07919592], [0.038949909999999976, 0.08012515], [0.04499489000000001, 0.07626146], [0.048858579999999985, 0.07041213], [0.048858579999999985, 0.05907538], [0.04505360000000003, 0.048364630000000006], [0.041268110000000024, 0.02821474], [0.03820657999999999, 0.008514799999999996], [0.03621112999999998, -0.015175990000000002], [0.036485009999999984, -0.036206220000000004], [0.03767836000000002, -0.05377378000000001], [0.040211739999999996, -0.06561919000000001], [0.03503734000000003, -0.07520505], [0.030097719999999994, -0.08012514], [0.022164940000000022, -0.08012515], [0.015092849999999991, -0.07520506], [0.006817760000000006, -0.06561919000000001], [0.004284320000000008, -0.05377379], [0.003090980000000021, -0.036206230000000006], [0.0028268699999999813, -0.015176000000000002], [0.004822309999999996, 0.008514789999999998], [0.0078839, 0.028214729999999997], [0.009884044409984673, 0.045660821438693294], [-0.0012129599999999852, 0.04513673]], 'holes': []}], 'simplify_tolerance': 3.2050060000000004e-05, 'sketch_entity_count': 29}
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
