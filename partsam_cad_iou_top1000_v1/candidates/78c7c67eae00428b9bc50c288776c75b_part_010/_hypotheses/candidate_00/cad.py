#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.206314535, -0.0464638, -0.05166733], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.04764712, 'zmax': 0.04764712, 'profiles': [{'outer': [[-0.11069639, -0.040824534999999995], [-0.10936667, -0.01983447499999999], [-0.10867019, -0.016826864999999996], [-0.10151519, 0.007202475000000014], [-0.09784271, 0.01220463500000002], [-0.07061584, 0.03195999500000002], [-0.0364239, 0.04737803500000001], [0.004289849999999998, 0.05807885500000001], [0.03848182, 0.05950349499999999], [0.04209094000000001, 0.05950349499999999], [0.07090082, 0.05760392500000003], [0.09021290000000001, 0.052601784999999984], [0.10430123, 0.04927757499999999], [0.10892351, 0.046459885000000006], [0.10965164, 0.043547224999999995], [0.11060141000000001, 0.04060293500000001], [0.11069639, 0.035854045], [0.10870189999999999, 0.027717635000000018], [0.10680233, 0.02439343500000002], [0.10439624, 0.021005885000000002], [0.10284494, 0.019676205000000002], [0.0974312, 0.01878975500000002], [0.08626769886817974, 0.019252313496563242], [0.07086911, 0.017966595000000002], [0.044718640000000004, 0.015465525000000008], [0.020182779999999997, 0.014484095000000002], [-0.010526639999999997, 0.008468854999999997], [-0.04310401, -0.0026751949999999913], [-0.06517964431875706, -0.013128769886203599], [-0.06634183, -0.023791884999999985], [-0.0668167, -0.039621484999999984], [-0.06934947999999999, -0.04908758499999999], [-0.07299025, -0.05396309499999999], [-0.07450987, -0.057952165], [-0.08014525, -0.057920515000000006], [-0.08742685, -0.05950349499999999], [-0.09587987, -0.05912356499999999], [-0.1017368, -0.056749124999999984], [-0.10544093, -0.055102855000000006], [-0.10911341, -0.050448944999999995]], 'holes': []}], 'simplify_tolerance': 4.4278556000000006e-05, 'sketch_entity_count': 40}
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
