#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.033998835000000005, -0.45354258999999997, 0.18499146], 'basis': [[0.0, 0.9147725081515604, -0.40396937796088395], [-0.9999999985231188, -2.1955140723733846e-05, -4.9716538535787704e-05], [-5.434852719420665e-05, 0.4039693773642692, 0.9147725068005501]], 'axis': [-0.40396937796088395, -4.9716538535787704e-05, 0.9147725068005501], 'zmin': -0.046227325314029656, 'zmax': 0.04637155531351356, 'profiles': [{'outer': [[-0.02457645621361816, 0.07437674629415564], [-0.009567410347399236, 0.08275836808518165], [0.006450201096667735, 0.08542391059303704], [0.02083287278264249, 0.08489834521199759], [0.03137757533609673, 0.08294316576412228], [0.03829975068321105, 0.07814776369332377], [0.04243169671630897, 0.06831117181338743], [0.044732932384604907, 0.05120666642885733], [0.04602584003825969, 0.025799351402186498], [0.0464572587944912, -0.004201726615000668], [0.04602715063505797, -0.03389166985835896], [0.044735338603689105, -0.05839141281713547], [0.0424348218207539, -0.0740187932103125], [0.03830326795684548, -0.08204528624415183], [0.03138126182006618, -0.08495617527998384], [0.02083660981780754, -0.08531130076931528], [0.00645393866444835, -0.08481657030446349], [-0.009563801018772933, -0.0816297997348153], [-0.024573219364796926, -0.07305598776255616], [-0.036557513844735, -0.05645569279252766], [-0.04396968266395307, -0.030553456728950518], [-0.046457188022926005, 0.0006753142739730752], [-0.04397105392131649, 0.03189919371121238], [-0.03656002276133967, 0.05781070276369874]], 'holes': []}], 'simplify_tolerance': 3.414704227247047e-05, 'sketch_entity_count': 33}
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
