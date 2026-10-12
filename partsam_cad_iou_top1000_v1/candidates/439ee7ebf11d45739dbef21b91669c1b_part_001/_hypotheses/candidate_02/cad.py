#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.11430557999999999, -0.06717563, -0.008533884999999998], 'basis': [[0.05286075472729112, 0.4085427130614125, 0.9112072169457843], [0.0, 0.9124829658103931, -0.4091146992053318], [-0.9986018929531734, 0.02162611177002253, 0.04823453824853436]], 'axis': [0.9112072169457843, -0.4091146992053318, 0.04823453824853436], 'zmin': -0.048300528151749365, 'zmax': 0.04748532291972318, 'profiles': [{'outer': [[-0.05203622450746286, -0.07183755985477783], [-0.055734700088772855, -0.06514520558403193], [-0.06079931359339848, -0.05473881615828036], [-0.066642750180057, -0.04195237790268815], [-0.07263933959813547, -0.028270946987786014], [-0.0780551803129881, -0.01537876189007391], [-0.08211800856626525, -0.004877441398208397], [-0.08448882544347273, 0.002091064819063141], [-0.08484007315434515, 0.004576875087778071], [-0.016061722445690065, 0.04237740402644254], [0.04039841989002648, 0.0735754995236525], [0.04252410746606472, 0.07067049609256568], [0.047086378615165146, 0.06205500334287455], [0.05339658788676624, 0.048774683677107106], [0.06087038793819403, 0.03251288712597139], [0.06846872429543603, 0.01513507150221606], [0.07539364000020952, -0.001207919664342959], [0.08067472902474587, -0.014587833651846967], [0.08377780875493684, -0.02332699989685169], [0.08432264459948197, -0.026434919839148762], [0.023855287249475, -0.04869478742293441], [-0.050325467847886, -0.07412114253689976]], 'holes': []}], 'simplify_tolerance': 3.383254355076543e-05, 'sketch_entity_count': 22}
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
