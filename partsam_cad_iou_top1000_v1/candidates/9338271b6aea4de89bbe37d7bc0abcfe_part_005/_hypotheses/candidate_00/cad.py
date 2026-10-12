#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [2.8499999998876646e-07, -0.18508768, -0.126865275], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.07134533000000001, 'zmax': 0.07134533, 'profiles': [{'outer': [[-0.298785675, -0.03494314499999999], [-0.12534665499999997, -0.03494314499999999], [-0.12534665499999997, 0.034943135000000014], [-0.298785735, 0.034943135000000014], [-0.286967805, 0.09436107500000002], [-0.219634765, 0.195141735], [-0.11885409499999999, 0.262474755], [-1.823500000000533e-05, 0.286110625], [0.118854105, 0.262474755], [0.219634765, 0.195141735], [0.28696780499999996, 0.09436107500000002], [0.298785735, 0.034943135000000014], [0.127097465, 0.034943135000000014], [0.127097465, -0.03494314499999999], [0.298785735, -0.03494314499999999], [0.28696780499999996, -0.09436107499999999], [0.219634765, -0.19514173499999998], [0.118854105, -0.262474765], [-1.823500000000533e-05, -0.286110625], [-0.11885409499999999, -0.262474765], [-0.219634765, -0.19514173499999998], [-0.286967805, -0.09436107499999999]], 'holes': [[[-0.040396144999999994, 0.17351200500000002], [-0.05381903499999999, 0.16454917081998893], [-0.05381903499999999, 0.161949425], [-0.04922317500000001, 0.155967505], [-0.03426837499999999, 0.149803175], [0.037295755, 0.149803175], [0.052214065000000004, 0.155967505], [0.056809925, 0.161949425], [0.056809925, 0.16274693123090198], [0.040687984999999996, 0.17351200500000002], [0.0001276849999999885, 0.18157298500000002]], [[0.037295755, -0.149803205], [-0.03426837499999999, -0.149803205], [-0.04922317500000001, -0.15596749499999998], [-0.05381903499999999, -0.16194941499999999], [-0.05381903499999999, -0.16454917691339235], [-0.040396144999999994, -0.173512015], [0.0001276849999999885, -0.18157300499999998], [0.040687984999999996, -0.173512015], [0.056809925, -0.16274693653877004], [0.056809925, -0.16194941499999999], [0.052214065000000004, -0.15596749499999998]]]}], 'simplify_tolerance': 0.000119514294, 'sketch_entity_count': 62}
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
