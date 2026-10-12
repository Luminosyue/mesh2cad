#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.074349025, -0.11741117000000001, 0.27982143000000004], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.023911015000000008, 'zmax': 0.023911015, 'profiles': [{'outer': [[-0.013342379999999987, -0.03894302999999999], [-0.019356599999999946, -0.03504649999999998], [-0.02464913999999996, -0.029806310000000003], [-0.028979389999999938, -0.023424059999999997], [-0.032199319999999976, -0.01612363], [-0.034179389999999976, -0.00821856999999998], [-0.03484558999999998, -9.999999994736442e-09], [-0.034179389999999976, 0.008218580000000003], [-0.032199319999999976, 0.01614602000000001], [-0.028979389999999938, 0.023424050000000016], [-0.02464913999999996, 0.02982871000000001], [-0.019356599999999946, 0.035068890000000005], [-0.013342379999999987, 0.03896543000000001], [-0.006791469999999966, 0.04136158000000001], [5.551115123125783e-17, 0.04216776000000001], [0.006791450000000032, 0.04136158000000001], [0.013323850000000026, 0.03896543000000001], [0.019356610000000052, 0.03506888000000001], [0.024630610000000053, 0.02982871000000001], [0.028960890000000017, 0.023424040000000007], [0.03218081000000003, 0.01614602000000001], [0.03416089000000003, 0.008218570000000008], [0.03484559000000004, -9.999999994736442e-09], [0.03416089000000003, -0.00821856999999998], [0.03218081000000003, -0.01612363], [0.028960890000000017, -0.023424059999999997], [0.024630610000000053, -0.029806310000000003], [0.019356610000000052, -0.03504649999999998], [0.013323850000000026, -0.03894302999999999], [0.006791480000000016, -0.04133919], [5.551115123125783e-17, -0.04216776], [-0.006791469999999966, -0.04133919]], 'holes': []}], 'simplify_tolerance': 1.6867104000000004e-05, 'sketch_entity_count': 32}
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
