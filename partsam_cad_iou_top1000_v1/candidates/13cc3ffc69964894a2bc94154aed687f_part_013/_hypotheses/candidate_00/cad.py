#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.14455234, 0.020825085, 0.418055965], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.027781375, 'zmax': 0.027781374999999997, 'profiles': [{'outer': [[-0.054993464999999964, 0.02516265000000001], [-0.06040172499999996, 0.030912469999999997], [-0.06239424499999996, 0.03512520999999999], [-0.06142647499999998, 0.038142449999999994], [-0.058181445, 0.0405904], [-0.05698595499999998, 0.04093197000000001], [-0.0520943002325724, 0.04082447395535447], [-0.04081810499999999, 0.04218442], [-0.032107934999999976, 0.04218442], [-0.022316174999999994, 0.04110275999999999], [-0.010987264999999968, 0.039167179999999996], [-0.0029602749999999567, 0.03597914999999999], [0.016395585000000046, 0.02846454000000001], [0.02527649500000001, 0.022600819999999994], [0.03284804500000005, 0.016053999999999985], [0.046624915000000045, -0.0023910299999999884], [0.048959005, -0.0058636999999999995], [0.059490875, -0.027439790000000006], [0.062394245000000015, -0.04218442], [0.045941725000000044, -0.035011379999999995], [0.033472394135905165, -0.026183781962594636], [0.024823979774800827, -0.021633029999999998], [-0.009222464999999958, -0.021633029999999998], [-0.009222494999999997, -0.0059298231203100535], [-0.013246331009526525, -0.0030741900000000044], [-0.032278784999999977, -0.0030741900000000044], [-0.032278784999999977, 0.0104327486146202], [-0.033701965, 0.011442750000000002], [-0.042006517495280546, 0.016794069999999994], [-0.04856045499999995, 0.016794069999999994], [-0.04856045499999995, 0.02101732186910268]], 'holes': []}], 'simplify_tolerance': 2.4957697999999994e-05, 'sketch_entity_count': 37}
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
