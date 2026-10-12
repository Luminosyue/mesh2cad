#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0003130899999999881, -0.02314709000000001, 0.021596010000000002], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.08289519000000001, 'zmax': 0.08289519000000001, 'profiles': [{'outer': [[-0.24084455000000002, -0.05107623999999999], [-0.24225952, -0.04710162999999999], [-0.24456774, -0.03861850999999999], [-0.24544515, -0.03413965999999999], [-0.24663086, -0.024870529999999988], [-0.24693127, -0.020139559999999987], [-0.24693127, -0.010603469999999988], [-0.24663086, -0.005872509999999988], [-0.24544515, 0.003396640000000012], [-0.24456774, 0.007875480000000011], [-0.24225952, 0.01637343000000001], [-0.24084455000000002, 0.020333200000000013], [-0.23764064305563776, 0.02739774524597349], [-0.23833276, 0.033978490000000014], [-0.21579879000000002, 0.10471752000000001], [-0.12606364, 0.19108538], [0.04782705999999999, 0.27753509], [0.23867217999999998, 0.32208963], [0.23867217999999998, 0.18846695000000002], [-0.02785130671247391, -0.02096801955862141], [0.24144654000000002, -0.21469227999999999], [0.2470261, -0.32208963], [0.07871492999999999, -0.29324574999999997], [-0.06999075000000002, -0.22782544999999998], [-0.15695152, -0.16756021], [-0.22705035, -0.07329609], [-0.22726075798961223, -0.07129550443271292], [-0.22935098, -0.06949586999999999], [-0.23157224, -0.06715263999999999], [-0.23368282, -0.06451277999999999], [-0.23568274, -0.06156148999999999], [-0.23754826, -0.05831357999999999]], 'holes': []}], 'simplify_tolerance': 0.000128835852, 'sketch_entity_count': 32}
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
