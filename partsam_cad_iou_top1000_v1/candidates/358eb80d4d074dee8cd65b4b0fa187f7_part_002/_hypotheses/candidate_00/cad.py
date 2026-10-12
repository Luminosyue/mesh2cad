#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0006016199999999972, -0.185418825, -0.041101745], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.030215725, 'zmax': 0.030215725, 'profiles': [{'outer': [[-0.12278483500000001, -0.20150152], [-0.125797715, -0.2002548], [-0.125797715, -0.19537181], [-0.12278483500000001, -0.19537181], [-0.12278483500000001, -0.18899965], [-0.090300765, -0.18899965], [-0.090300765, -0.19537181], [-0.08808439500000001, -0.19537181], [-0.08808439500000001, -0.18899965], [-0.055565705, -0.18899965], [-0.055565705, -0.19537181], [-0.052587395, -0.19537181], [-0.052587395, -0.2002548], [-0.055565705, -0.20150152]], 'holes': []}, {'outer': [[-0.12278481499999999, 0.19537179], [-0.12579769500000001, 0.19537179], [-0.12579769500000001, 0.2002548], [-0.12278481499999999, 0.20150152], [-0.055565705, 0.20150152], [-0.052587395, 0.2002548], [-0.052587395, 0.19537179], [-0.055565705, 0.19537179], [-0.055565705, 0.18899962], [-0.08808437499999999, 0.18899962], [-0.08808437499999999, 0.19537179], [-0.090300765, 0.19537179], [-0.090300765, 0.18899962], [-0.12278481499999999, 0.18899962]], 'holes': []}, {'outer': [[0.052587425, -0.19537181], [0.055565705, -0.19537181], [0.055565705, -0.18899965], [0.08808439500000001, -0.18899965], [0.08808439500000001, -0.19537181], [0.090300765, -0.19537181], [0.090300765, -0.18899965], [0.122819455, -0.18899965], [0.122819455, -0.19537181], [0.125797715, -0.19537181], [0.125797715, -0.2002548], [0.122819455, -0.20150152], [0.055565705, -0.20150152], [0.052587425, -0.2002548]], 'holes': []}, {'outer': [[0.052587435, 0.19537179], [0.052587425, 0.2002548], [0.055565705, 0.20150152], [0.122819455, 0.20150152], [0.125797715, 0.2002548], [0.125797715, 0.19537179], [0.122819455, 0.19537179], [0.122819455, 0.18899962], [0.090300775, 0.18899962], [0.090300775, 0.19537179], [0.08808439500000001, 0.19537179], [0.08808439500000001, 0.18899962], [0.055565705, 0.18899962], [0.055565705, 0.19537179]], 'holes': []}], 'simplify_tolerance': 8.0600608e-05, 'sketch_entity_count': 59}
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
