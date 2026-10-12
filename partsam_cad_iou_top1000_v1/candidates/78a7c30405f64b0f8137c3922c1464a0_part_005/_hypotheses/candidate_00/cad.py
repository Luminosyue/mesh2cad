#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.12047342500000001, -0.002307175, -6.752500000000057e-05], 'basis': [[0.0, 0.8825274624229759, 0.47026086172385534], [-2.8233565272292417e-05, -0.4702608615364248, 0.8825274620712295], [0.9999999996014329, -1.3277140734484948e-05, 2.4916896714909683e-05]], 'axis': [0.47026086172385534, 0.8825274620712295, 2.4916896714909683e-05], 'zmin': -0.00226894686181199, 'zmax': 0.005943210918485672, 'profiles': [{'outer': [[-0.019410317075380913, 0.0001316776285242057], [-0.01792813816955744, 0.007575783895087507], [-0.013717474625957108, 0.01385823933400844], [-0.0074185485190563566, 0.018077548213042846], [8.740973824870108e-06, 0.01954665339406128], [0.007435991475023113, 0.018077350987224718], [0.013734805363101319, 0.013857874846223398], [0.017928251816151382, 0.007575307824751246], [0.019410232909146487, 0.0001311622026184656], [0.017928054479905597, -0.007290144298134882], [0.013734330793336878, -0.013588936429904658], [0.007435515017798347, -0.01780181080811798], [8.115193272565383e-06, -0.019277355192566115], [-0.007419034976281119, -0.017801613582167083], [-0.013717939195721552, -0.013588571942252388], [-0.01792833550580323, -0.007289668227798622]], 'holes': []}], 'simplify_tolerance': 7.764801717325479e-06, 'sketch_entity_count': 16}
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
