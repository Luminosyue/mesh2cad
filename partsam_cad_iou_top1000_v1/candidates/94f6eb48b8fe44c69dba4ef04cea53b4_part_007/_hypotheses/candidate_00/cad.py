#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.08586613, -0.11741119, 0.27982142], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.023911019999999998, 'zmax': 0.023911020000000005, 'profiles': [{'outer': [[-0.006791480000000016, -0.04133919999999999], [-0.013342390000000037, -0.03894304000000001], [-0.019356609999999996, -0.03504649000000001], [-0.02464915000000001, -0.029806319999999997], [-0.02897939999999999, -0.023424050000000002], [-0.032199330000000026, -0.01612363], [-0.034179400000000026, -0.008218560000000014], [-0.03484560000000003, -9.999999994736442e-09], [-0.034179400000000026, 0.008218569999999994], [-0.032199330000000026, 0.016146019999999997], [-0.02897939999999999, 0.023424050000000002], [-0.02464915000000001, 0.029828709999999994], [-0.019356609999999996, 0.035068890000000005], [-0.013342390000000037, 0.038965429999999995], [-0.006791480000000016, 0.041361579999999995], [-9.999999994736442e-09, 0.04216776], [0.006791469999999966, 0.041361579999999995], [0.01332386999999996, 0.03896542], [0.0193566, 0.035068890000000005], [0.024630629999999987, 0.0298287], [0.028960879999999967, 0.023424050000000002], [0.032180809999999976, 0.016146010000000002], [0.03416089, 0.008218569999999994], [0.03484559999999998, -9.999999994736442e-09], [0.03416089, -0.008218560000000014], [0.032180809999999976, -0.01612363], [0.028960879999999967, -0.023424050000000002], [0.024630629999999987, -0.029806319999999997], [0.0193566, -0.03504649000000001], [0.01332386999999996, -0.03894304000000001], [0.006791469999999966, -0.04133919999999999], [-9.999999994736442e-09, -0.04216776]], 'holes': []}], 'simplify_tolerance': 1.6867104e-05, 'sketch_entity_count': 32}
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
