#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.0072272050000000004, 0.41007899999999997, -0.004609265000000001], 'basis': [[-0.0, 0.9999999951804754, -9.817865982333596e-05], [0.6588249606122193, 7.385943914922729e-05, 0.7522962619999458], [0.7522962656256561, -6.46825516910698e-05, -0.6588249574369962]], 'axis': [-9.817865982333596e-05, 0.7522962619999458, -0.6588249574369962], 'zmin': -0.11684137787170175, 'zmax': 0.1181603218721808, 'profiles': [{'outer': [[-0.0431566696898045, 0.012497655696354868], [-0.042175904787442424, 0.013279131754465693], [-0.03926847502971891, 0.015224142434912909], [-0.03485464704431217, 0.017169088065932488], [-0.019968091739329244, 0.02046388333471512], [-0.01782950795341845, 0.020828025295591537], [-0.00013221628810843012, 0.022135651681680656], [0.01708148452688752, 0.02080893410094594], [0.01953192508491425, 0.020393685038629], [0.033626499558567106, 0.017167719049687728], [0.03874179259074995, 0.015215793337725388], [0.04238697339636044, 0.013263938195388516], [0.043696443704809115, 0.012464750556599737], [0.050180496061002874, 0.002222884656805691], [0.043696443704809115, -0.012289159324098187], [0.025335783913935084, -0.020225755035846598], [0.0004156418079123086, -0.022124829825842983], [-0.024604812360903193, -0.020203818968520353], [-0.0431566696898045, -0.012256244184343106], [-0.04970793790970393, 0.002255785981181232]], 'holes': []}], 'simplify_tolerance': 1.9977686794141363e-05, 'sketch_entity_count': 20}
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
