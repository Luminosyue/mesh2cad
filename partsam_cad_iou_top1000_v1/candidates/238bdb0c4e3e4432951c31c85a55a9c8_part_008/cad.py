#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.009993465, 0.17974335, 0.373804435], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.06603405500000001, 'zmax': 0.06603405500000001, 'profiles': [{'outer': [[-0.11586897499999999, -0.0875233], [-0.11124698500000002, -0.0875233], [-0.11124698500000002, 0.010876059999999993], [-0.10271781018473988, 0.010876059999999993], [-0.09115962500000002, 0.04662579], [-0.0846505752558055, 0.044531077147370104], [-0.07183896500000003, 0.08417177], [-0.06790608699569256, 0.08289761681207415], [-0.03289107499999999, 0.12991038000000002], [-0.027586530339790097, 0.1259659835935179], [0.016724834999999993, 0.15253872], [0.01975474995711959, 0.14748482654326847], [0.060776724999999976, 0.16498106999999998], [0.06340171127201986, 0.1588377570233866], [0.11168499500000001, 0.17943865], [0.11586897499999999, 0.16962501], [0.05672420499999997, 0.1443899], [0.054095661475729966, 0.1505552589517279], [0.005794004999999991, 0.12995419], [0.004565815201505058, 0.13282854073108205], [-0.03295682500000002, 0.11032688999999998], [-0.03351226259571029, 0.11125337393481699], [-0.06277011500000002, 0.07197043], [-0.06422786155273497, 0.07305439472908325], [-0.08147744500000004, 0.01968206], [-0.08798875585135266, 0.021791566757866376], [-0.10060088500000003, -0.01723212410247828], [-0.10060088500000003, -0.14000882], [-0.10520105499999999, -0.14000882], [-0.10520105499999999, -0.17943865], [-0.11586897499999999, -0.17943865]], 'holes': []}], 'simplify_tolerance': 7.177546e-05, 'sketch_entity_count': 31}
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
