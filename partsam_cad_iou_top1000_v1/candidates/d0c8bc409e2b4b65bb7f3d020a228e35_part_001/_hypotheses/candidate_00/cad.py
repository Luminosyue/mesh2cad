#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.05112562999999999, -0.314016835, -0.08855225], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.03502084500000002, 'zmax': 0.03502084499999997, 'profiles': [{'outer': [[-0.19522001, -0.01921670999999999], [-0.1961539, 1.19600000000053e-05], [-0.19522001, 0.019216670000000005], [-0.19239436, 0.038277720000000015], [-0.18770093999999998, 0.05693169000000001], [-0.18121157999999998, 0.07505883], [-0.17299809, 0.09246759], [-0.16308443, 0.10896643000000002], [-0.15163823, 0.12443554], [-0.13870736, 0.13870738999999999], [-0.12443555, 0.15163822999999998], [-0.10896643, 0.16308446], [-0.09246758999999999, 0.17299812000000003], [-0.07505882999999999, 0.18121157999999998], [-0.05693169000000001, 0.18770093999999998], [-0.03827773000000001, 0.19239439000000003], [-0.019216689999999995, 0.19522001], [-1.1970000000000036e-05, 0.19615391999999998], [0.019216689999999995, 0.19522001], [0.03827772, 0.19239439000000003], [0.05693168, 0.18770093999999998], [0.07505882, 0.18121157999999998], [0.09246759, 0.17299812000000003], [0.10896639999999999, 0.16308446], [0.12443552999999999, 0.15163822999999998], [0.13870738, 0.13870738999999999], [0.15163822999999998, 0.12443554], [0.16308442, 0.10896643000000002], [0.17299809, 0.09246759], [0.18121157999999998, 0.07505883], [0.18770095, 0.05693169000000001], [0.19239436999999998, 0.038277720000000015], [0.19522, 0.019216670000000005], [0.1961539, -1.1979999999994773e-05], [0.19522, -0.01921670999999999], [0.19239436999999998, -0.03827772999999999], [0.18770095, -0.05693169999999999], [0.18121157999999998, -0.07505885], [0.17299809, -0.09246760999999999], [0.16308442, -0.10896642999999999], [0.15163822999999998, -0.12443555999999999], [0.13870738, -0.13870740999999998], [0.12443552999999999, -0.15163826], [0.10896639999999999, -0.16308446999999998], [0.09246759, -0.17299811999999998], [0.07505882, -0.18121159999999997], [0.05693168, -0.18770096999999997], [0.03827772, -0.19239438999999997], [0.019216689999999995, -0.19522003999999998], [-1.1970000000000036e-05, -0.19615391999999998], [-0.019216689999999995, -0.19522003999999998], [-0.03827773000000001, -0.19239438999999997], [-0.05693169000000001, -0.18770096999999997], [-0.07505882999999999, -0.18121159999999997], [-0.09246758999999999, -0.17299811999999998], [-0.10896643, -0.16308446999999998], [-0.12443555, -0.15163826], [-0.13870736, -0.13870740999999998], [-0.15163823, -0.12443555999999999], [-0.16308443, -0.10896642999999999], [-0.17299809, -0.09246760999999999], [-0.18121157999999998, -0.07505885], [-0.18770093999999998, -0.05693169999999999], [-0.19239436, -0.03827772999999999]], 'holes': []}], 'simplify_tolerance': 7.8461568e-05, 'sketch_entity_count': 76}
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
