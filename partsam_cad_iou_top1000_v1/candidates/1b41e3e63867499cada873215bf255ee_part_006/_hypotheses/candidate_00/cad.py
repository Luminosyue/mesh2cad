#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0, -0.132000005, -0.203161795], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.13233845, 'zmax': 0.13233845, 'profiles': [{'outer': [[-0.03562981500000001, 0.035629825000000004], [-0.027997615000000003, 0.04188420500000001], [-0.019281734999999994, 0.046544025], [-0.009838244999999995, 0.049408035], [-7.72500000001397e-06, 0.050383335], [0.009822794999999995, 0.04940802500000001], [0.019281754999999984, 0.04654401500000001], [0.02798215499999998, 0.041884185000000004], [0.035629835, 0.035629805], [0.04188420500000001, 0.02798212500000001], [0.04654402499999999, 0.019281725], [0.049408024999999994, 0.009822764999999997], [0.050383344999999996, -7.75499999999818e-06], [0.049408024999999994, -0.009838275000000007], [0.046544014999999994, -0.019281765000000006], [0.041884194999999985, -0.027997634999999993], [0.03562980499999999, -0.035629835], [0.027982124999999997, -0.04188420500000001], [0.019281725, -0.04654402499999999], [0.009822764999999983, -0.049408044999999984], [-7.75499999999818e-06, -0.050383335], [-0.009838275000000007, -0.049408024999999994], [-0.019281765000000006, -0.046544005], [-0.027997634999999993, -0.041884194999999985], [-0.035629825000000004, -0.03562981500000001], [-0.04188420500000001, -0.02799760500000001], [-0.04654403500000001, -0.019281734999999994], [-0.04940803500000002, -0.009838244999999995], [-0.050383344999999996, -7.724999999986215e-06], [-0.04940803500000002, 0.00982279500000001], [-0.046544005, 0.019281754999999998], [-0.04188418500000002, 0.02798215500000001]], 'holes': []}], 'simplify_tolerance': 2.0153338e-05, 'sketch_entity_count': 35}
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
