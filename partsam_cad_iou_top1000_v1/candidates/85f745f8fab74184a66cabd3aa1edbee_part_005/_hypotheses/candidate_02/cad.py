#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.13491846000000002, -0.331677915, -0.003773565000000003], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.03845873999999999, 'zmax': 0.03845874000000002, 'profiles': [{'outer': [[-0.03350858500000001, -0.006853995000000002], [-0.041752465, -0.01852488499999999], [-0.056431515, -0.017934704999999995], [-0.065436945, -0.009043485000000018], [-0.059953715000000005, 0.013194024999999998], [-0.054603755000000004, 0.022922934999999978], [-0.032213915, 0.047026275000000006], [-0.005418219812440377, 0.05909481120797093], [-0.018562965, 0.07111057500000001], [-0.018562965, 0.07796460499999996], [0.017268384999999997, 0.081601025], [0.05123391499999999, 0.07735532499999997], [0.051233904999999996, 0.070329965], [0.037662355788067974, 0.058232855854555815], [0.054908425, 0.04272341499999999], [0.064085195, 0.008700784999999989], [0.062200334999999995, -0.020885765], [0.062105125, -0.039182245000000004], [0.065436945, -0.053213924999999995], [0.065436945, -0.066465045], [0.041276485, -0.07185307499999999], [0.038382564999999993, -0.06240975500000001], [0.036821364999999995, -0.05323296500000002], [0.034803235, -0.03240436499999999], [0.031528534999999996, -0.060106035], [0.030728894999999996, -0.071910205], [0.030728884999999994, -0.081601025], [0.0034460449999999965, -0.081601025], [0.0031997481490208275, -0.06797576439433387], [0.0027035249999999966, -0.060048904999999986], [-0.0003617350000000032, -0.03229009500000002], [-0.0022656450000000028, -0.051081564999999995], [-0.003807805000000003, -0.060372585000000034], [-0.006739805000000003, -0.07072979499999998], [-0.030900255, -0.06536078500000003], [-0.030900255, -0.05209064499999999], [-0.02792583309098274, -0.039527844222848336], [-0.029015395000000003, -0.025988165000000008], [-0.030126633211520905, -0.007802215478793903]], 'holes': []}], 'simplify_tolerance': 3.264041e-05, 'sketch_entity_count': 39}
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
