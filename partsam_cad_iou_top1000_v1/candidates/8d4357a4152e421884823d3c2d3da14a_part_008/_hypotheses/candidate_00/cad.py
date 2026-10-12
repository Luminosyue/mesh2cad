#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.17340434500000002, 0.053909900000000004, -0.054843615000000005], 'basis': [[0.0, 0.7891449350671075, -0.6142070265455538], [-0.13142440501951325, 0.6088795148378328, 0.7823000461307109], [0.9913261954398598, 0.08072179302255378, 0.10371290356535703]], 'axis': [-0.6142070265455538, 0.7823000461307109, 0.10371290356535703], 'zmin': -0.14739833334520738, 'zmax': 0.15380641600068717, 'profiles': [{'outer': [[-0.0236776853849668, 0.03843604540816723], [-0.002557148028925872, 0.0409473068921066], [0.0011430907696178968, 0.03995175430060517], [0.016349561710760078, 0.04030087765273787], [0.034225709102441854, 0.03051760973218624], [0.0388189817519685, 0.027648444966231384], [0.047617736177174595, 0.012635645483545418], [0.04747349122626153, -0.004880145451072769], [0.03839393045335422, -0.020259058863201382], [0.033767031792062835, -0.02510173563659471], [0.015739844239537486, -0.03567307752311213], [-0.005005993187470591, -0.0361242588972778], [-0.01319338573315058, -0.03620034368185352], [-0.023644062214062643, -0.030474523320084487], [-0.031767326511002406, -0.02734454071252236], [-0.045050626433311404, -0.011513437990930013], [-0.04819596007365232, 0.00814224931103558], [-0.04035332169756454, 0.02645959862883985]], 'holes': []}], 'simplify_tolerance': 1.9162739250165386e-05, 'sketch_entity_count': 18}
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
