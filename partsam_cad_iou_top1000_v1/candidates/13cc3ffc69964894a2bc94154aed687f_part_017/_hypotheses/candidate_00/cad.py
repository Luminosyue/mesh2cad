#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.21282769499999998, 0.06508805000000001, 0.19388581], 'basis': [[0.0, 0.9375975973112473, 0.3477222246509076], [-0.9990275027238859, -0.01533154884159206, 0.04133996143435532], [0.0440913687843336, -0.34738406573459024, 0.936685786201771]], 'axis': [0.3477222246509076, 0.04133996143435532, 0.936685786201771], 'zmin': -0.017379728737109162, 'zmax': 0.01541891121016846, 'profiles': [{'outer': [[-0.02329210913444827, 0.0175275012506994], [-0.02065120627410432, 0.02854100027921167], [-0.01298383665073482, 0.044494237248663755], [-0.007677080033267133, 0.04924966434556419], [-0.0002691778914179173, 0.050855651674215206], [0.0051590176686979105, 0.04867840697989341], [0.010958902282129847, 0.04328831512233428], [0.013427708054899833, 0.03264836694064077], [0.013596733421156759, -0.006211867892768428], [0.012103720775904698, -0.007231842898499961], [0.012821174267905144, -0.014595888989788417], [0.015508451851817534, -0.027124437895758982], [0.018788132137630854, -0.03126877181664552], [0.023800748875507958, -0.04290227063902985], [0.023720436365753658, -0.043046367874509224], [0.02316674797660174, -0.043257766246262624], [0.02209685379737632, -0.0434729251290573], [0.020661108522366172, -0.04374538084183691], [0.01881841033237786, -0.044025193032795805], [0.014293121389465297, -0.04457896349687051], [0.00932737156073181, -0.04508192979476604], [0.004546540030059711, -0.045423267438532984], [0.002518822092505207, -0.04551474391405786], [-0.0005273970174840217, -0.0455664336849294], [-0.0014210620910482562, -0.0455058089807246], [-0.0018482617367501539, -0.04539692425358859], [0.0025001551718600353, -0.03391288657322132], [0.0038850611471395583, -0.028216379848376102], [0.004251465949984368, -0.015397549176596179], [0.003644189300650475, -0.012313566838557055], [-0.0038790689192326378, -0.012457696574374559], [-0.013270191819955543, -0.010986257359722498], [-0.019838846091164784, -0.006593337826694064], [-0.023563094193191948, 0.0015591789111153629]], 'holes': []}], 'simplify_tolerance': 1.9284417071828924e-05, 'sketch_entity_count': 34}
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
