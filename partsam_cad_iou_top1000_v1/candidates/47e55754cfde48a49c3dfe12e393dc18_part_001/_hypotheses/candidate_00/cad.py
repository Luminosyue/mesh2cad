#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [4.415499999999711e-05, 0.37611556, -4.401999999999878e-05], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.07158306000000003, 'zmax': 0.07158305999999998, 'profiles': [{'outer': [[-0.10616144, -0.043904935], [-0.10996217999999999, -0.033288084999999995], [-0.11268302999999999, -0.022348664999999997], [-0.11433795, -0.011198884999999997], [-0.11488492, 7.0150000000028864e-06], [-0.11433795, 0.011198875000000002], [-0.11268302999999999, 0.022348675000000002], [-0.10996217999999999, 0.033288085], [-0.10616144, 0.043904935000000006], [-0.1013509, 0.054101035000000006], [-0.09555863, 0.063778215], [-0.08884070999999999, 0.07283830499999999], [-0.08128126999999999, 0.081197145], [-0.07293646000000001, 0.08877058500000001], [-0.06387636999999999, 0.095488505], [-0.05421324, 0.101294825], [-0.04401714, 0.10611937500000002], [-0.033414320000000004, 0.109920135], [-0.022474900000000003, 0.11266900500000002], [-0.011325110000000001, 0.11432394500000001], [-7.020000000001217e-06, 0.114884935], [0.0113251, 0.11432394500000001], [0.022474889999999997, 0.11266900500000002], [0.033414309999999996, 0.109920135], [0.04401713, 0.10611937500000002], [0.05421323, 0.101294825], [0.06387638000000001, 0.095488505], [0.07293646000000001, 0.08877058500000001], [0.08128128000000001, 0.081197145], [0.0888407, 0.07283830499999999], [0.09555862000000001, 0.063778215], [0.10135090999999999, 0.054101035000000006], [0.10616144, 0.043904935000000006], [0.10996217999999999, 0.033288085], [0.11268302, 0.022348675000000002], [0.11433795, 0.011198875000000002], [0.11488492, 7.0150000000028864e-06], [0.11433795, -0.011198884999999997], [0.11268302, -0.022348664999999997], [0.10996217999999999, -0.033288084999999995], [0.10616144, -0.043904935], [0.10135090999999999, -0.054101035], [0.09555862000000001, -0.063778205], [0.0888407, -0.07283830499999999], [0.08128128000000001, -0.081197135], [0.07293646000000001, -0.08877057499999999], [0.06387638000000001, -0.095488505], [0.05421323, -0.10129480499999999], [0.04401713, -0.10611937499999999], [0.033414309999999996, -0.10992011499999998], [0.022474889999999997, -0.11266900499999999], [0.0113251, -0.11432393499999999], [-7.020000000001217e-06, -0.114884935], [-0.011325110000000001, -0.11432393499999999], [-0.022474900000000003, -0.11266900499999999], [-0.033414320000000004, -0.10992011499999998], [-0.04401714, -0.10611937499999999], [-0.05421324, -0.10129480499999999], [-0.06387636999999999, -0.095488505], [-0.07293646000000001, -0.08877057499999999], [-0.08128126999999999, -0.081197135], [-0.08884070999999999, -0.07283830499999999], [-0.09555863, -0.063778205], [-0.1013509, -0.054101035]], 'holes': []}], 'simplify_tolerance': 4.5953973999999996e-05, 'sketch_entity_count': 64}
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
