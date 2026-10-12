#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [7.339999999999777e-06, -0.025252625, -0.210524495], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.025261190000000003, 'zmax': 0.025261190000000003, 'profiles': [{'outer': [[-0.020937974999999998, -0.087008585], [0.0021712949999999898, -0.0074833750000000004], [0.016401344999999984, 0.026172325], [0.04028606500000001, 0.070645975], [0.03943302499999998, 0.083596455], [0.03524543499999999, 0.092630755], [0.029351844999999988, 0.098485575], [0.01694415499999999, 0.098214195], [0.005467105, 0.094375595], [-0.010973005000000008, 0.08336384499999999], [-0.03974324500000001, 0.056105775], [-0.088559565, 0.011554615], [-0.09115738500000001, 0.013338225], [-0.090265595, 0.029972235], [-0.09018175811767959, 0.03004746755863508], [-0.075492705, 0.138345165], [-0.074794795, 0.140283865], [-0.06436460500000002, 0.140283865], [-0.054360935, 0.160485075], [0.0005040949999999822, 0.160485075], [0.0005040947892122114, 0.160136085], [0.028343695000000002, 0.160136085], [0.05498135499999998, 0.151295585], [0.07091737499999998, 0.13501058500000002], [0.08766770500000001, 0.112638105], [0.09115738500000001, 0.082898545], [0.07809055499999998, 0.023729575], [0.061223924999999985, -0.016517715000000002], [0.038269744999999994, -0.059556705], [0.01488911499999998, -0.100075375], [-0.007793634999999993, -0.131986275], [-0.03183343499999999, -0.160485075], [-0.041216695, -0.156064825], [-0.06099138500000001, -0.136600365], [-0.065838125, -0.126906885], [-0.034818985, -0.106434275]], 'holes': [[[0.000504064999999998, 0.110815685], [-0.014924742044830765, 0.09796369921752554], [0.000504064999999998, 0.110427995]]]}], 'simplify_tolerance': 6.419403e-05, 'sketch_entity_count': 45}
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
