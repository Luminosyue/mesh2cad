#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.05534724, -0.474151745, 0.05600899], 'basis': [[-0.574562445531112, -0.013768614864439553, 0.8183449281507296], [0.0, 0.9998584905231802, 0.016822572000370354], [-0.8184607481029912, 0.009665618108656002, -0.5744811395000446]], 'axis': [0.8183449281507296, 0.016822572000370354, -0.5744811395000446], 'zmin': -0.01476741240609362, 'zmax': 0.015424729157132838, 'profiles': [{'outer': [[-0.04116625358361449, -0.014659996252340312], [-0.03566630016228839, -0.010954730393733817], [-0.028104408502377495, -0.006478259604036771], [-0.019048062469550306, -0.0013591758400175419], [-0.00947775612087828, 0.004123958241942188], [-0.0010993677178410212, 0.009456557203367457], [0.004664553904418168, 0.014167763809194597], [0.00827707159297294, 0.0182466521579194], [0.010632788728834565, 0.021822081142642533], [0.012391236724164803, 0.02511902188523394], [0.0211985176564179, 0.02522388652640259], [0.022512937520315923, 0.025335698134122862], [0.026334186806511728, 0.025850389777911795], [0.030126461467319437, 0.025861137782405896], [0.034603540646338866, 0.02545908284121428], [0.03957204900437417, 0.02528268134592072], [0.04054614384027875, 0.025276941696250676], [0.04100454818168453, 0.019621828210456625], [0.04150509002287375, 0.013945690660957563], [0.042107393195516984, 0.008227327447144958], [0.042856231904040636, 0.002434674761597272], [0.04375512300759337, -0.0033782462523697706], [0.04472335503441882, -0.008933582397463263], [0.046373105779861694, -0.017902492159646892], [0.046771283580893934, -0.020738892131490633], [0.04650994146101333, -0.022547840204602754], [0.04523560947909583, -0.02359695527538084], [0.04258611013931592, -0.0241965567336543], [0.03821674252180316, -0.024582231170676715], [0.031756568294085935, -0.024860793713465123], [0.022869644066298486, -0.025086040118790943], [0.0114638886858592, -0.02531143584508863], [-0.0021782713939069494, -0.02555825208175948], [-0.016343141134915144, -0.025772931368477407], [-0.029132829587829003, -0.02585910603329857], [-0.0391335733079738, -0.02574186944778649], [-0.04544201469097498, -0.025356647429489683], [-0.048554576877828534, -0.024639447806126407], [-0.04934125387234525, -0.023547383378243907], [-0.048669421945883085, -0.02203770985835932], [-0.04723104999166625, -0.020099677124001628], [-0.044865635440058865, -0.01766899037722511]], 'holes': []}], 'simplify_tolerance': 1.922250749064784e-05, 'sketch_entity_count': 45}
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
