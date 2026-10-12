#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.39356738, 0.223561995, -0.10597996999999999], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.08810111999999998, 'zmax': 0.08810112000000003, 'profiles': [{'outer': [[0.0881011, -0.04224098500000001], [-0.08810109999999999, -0.04224098500000001], [-0.08810109999999999, -0.028033395000000016], [-0.07020447999999999, -0.017063105000000023], [-0.05628725999999999, -0.017063105000000023], [-0.05628725999999999, -0.01456790500000002], [-0.0645365, -0.01456790500000002], [-0.0645365, 0.03509954500000001], [-0.05757788999999999, 0.04224098500000001], [0.05757787000000002, 0.04224098500000001], [0.06453649000000002, 0.03509954500000001], [0.06453649000000002, -0.01456790500000002], [0.05628725, -0.01456790500000002], [0.05628725, -0.017063105000000023], [0.07020446000000001, -0.017063105000000023], [0.0881011, -0.028033395000000016]], 'holes': []}], 'simplify_tolerance': 3.524044e-05, 'sketch_entity_count': 16}
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
    elif kind == "loft":
        wires = [cq.Wire.makePolygon([vec(p) for p in section], close=True) for section in s["sections"]]
        result = cq.Solid.makeLoft(wires, ruled=bool(s.get("ruled", True)))
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
