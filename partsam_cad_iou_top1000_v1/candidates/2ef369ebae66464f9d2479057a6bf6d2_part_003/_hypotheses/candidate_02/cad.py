#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.12170084, -0.0076137500000000025, -0.0012000050000000005], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.37831335, 'zmax': 0.37831335, 'profiles': [{'outer': [[0.044606335, -0.4590362], [-0.044606335, -0.4590362], [-0.044606335, 0.43219390999999996], [-0.025105065, 0.43219390999999996], [-0.025105065, 0.43802187000000004], [-0.022079015, 0.44631556000000006], [-0.016419165, 0.45309612], [-0.008741945000000001, 0.45752314000000005], [4.999999999536625e-09, 0.4590362], [0.008685904999999999, 0.45752314000000005], [0.016363125, 0.45309612], [0.022022975, 0.44631556000000006], [0.025049035, 0.43802187000000004], [0.025049035, 0.43219390999999996], [0.044606335, 0.43219390999999996]], 'holes': [[[-0.018380495, 0.09204259000000001], [-0.022079015, 0.09652563], [-0.025105065, 0.10481925], [-0.025105065, 0.11367329], [-0.022079015, 0.12196697000000001], [-0.016419165, 0.12874754], [-0.008741945000000001, 0.13317456], [4.999999999536625e-09, 0.13468762], [0.008685904999999999, 0.13317456], [0.016363125, 0.12874754], [0.022022975, 0.12196697000000001], [0.025049035, 0.11367329], [0.025049035, 0.10481925], [0.022022975, 0.09652563], [0.017576899051535838, 0.0911991369838114], [0.019052955, 0.09204259000000001], [0.025553375, 0.09977587], [0.029027745, 0.10930236], [0.029027745, 0.11938919], [0.025553375, 0.12891568], [0.019052955, 0.13664891], [0.010311015, 0.14169236], [0.00033622499999999946, 0.14342953], [-0.009582515, 0.14169236], [-0.018380495, 0.13664891], [-0.024880915, 0.12891568], [-0.028299245, 0.11938919], [-0.028299245, 0.10930236], [-0.024880915, 0.09977587]]]}], 'simplify_tolerance': 0.00018361448, 'sketch_entity_count': 50}
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
