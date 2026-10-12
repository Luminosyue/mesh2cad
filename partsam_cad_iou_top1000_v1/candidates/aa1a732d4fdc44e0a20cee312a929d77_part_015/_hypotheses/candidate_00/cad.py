#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.006794979999999999, 0.03608135, -0.46481073], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.03518891000000002, 'zmax': 0.03518891000000002, 'profiles': [{'outer': [[-0.07986935, -0.01165842], [-0.07596287, 0.0037233799999999992], [-0.06918755, 0.018006469999999997], [-0.059726520000000005, 0.03070255], [-0.048007060000000004, 0.04132332], [-0.03439541, 0.0494415], [-0.01950192, 0.054751879999999996], [-0.003814930000000001, 0.05701031], [0.011933099999999999, 0.056216789999999996], [0.027314899999999996, 0.05237135], [0.04159799, 0.04559604], [0.05429407, 0.036135009999999995], [0.06491483, 0.024354519999999998], [0.07303298999999999, 0.01080389], [0.07834337999999999, -0.0040896000000000005], [0.08066285000000001, -0.01977659], [0.07986935, -0.03558567], [0.07596286, -0.05090641], [0.06918755, -0.06525054999999999], [0.05972653, -0.07794662999999999], [0.04800706, -0.08850636], [0.0343954, -0.09662453000000001], [0.019501909999999997, -0.10193490999999999], [0.003814930000000001, -0.10425439], [-0.01199414, -0.10346088], [-0.02731488, -0.09961544], [-0.04159797, -0.09277908000000001], [-0.054294060000000005, -0.08337908999999999], [-0.06491482, -0.07159860000000001], [-0.07303299, -0.05804796], [-0.07834336, -0.043093440000000004], [-0.08066285000000001, -0.027467490000000004]], 'holes': []}, {'outer': [[0.006195449999999998, 0.10199595], [0.018586329999999998, 0.10425439], [0.018525299999999998, 0.06958432], [0.006195449999999998, 0.06695964]], 'holes': []}], 'simplify_tolerance': 4.1701756e-05, 'sketch_entity_count': 36}
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
