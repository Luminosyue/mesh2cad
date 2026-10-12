#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.233418285, -0.1686378, -0.07462521999999999], 'basis': [[0.0, 0.999998112187251, 0.0019430959663255735], [-0.7237399145468426, -0.001340877768186758, 0.690071545666491], [0.690072848394812, -0.001406296108624785, 0.7237385482614049]], 'axis': [0.0019430959663255735, 0.690071545666491, 0.7237385482614049], 'zmin': -0.11487984725900868, 'zmax': 0.11486165736510157, 'profiles': [{'outer': [[-0.10901454933666366, -0.02153290011526148], [-0.10901454933666366, -0.018326987543048432], [-0.11484456834811532, -0.018262086488189944], [-0.11484456834811532, 0.008915162206156622], [-0.10901454933666366, 0.008965720441857217], [-0.10901454933666366, 0.012198356206322591], [-0.07525105946036609, 0.01234664708147953], [-0.020090300736927705, 0.012397443382736927], [-0.020090300736927705, 0.03020975681374661], [-0.04002155369828138, 0.030196836101050978], [-0.04002155369828138, 0.03371669945619555], [-0.020090300736927705, 0.03374296044575541], [-0.020090300736927705, 0.0338520106772399], [-0.015027726896114696, 0.04335613849881972], [-0.00795141745933168, 0.04793496241351601], [0.00795143126078863, 0.04793422657493909], [0.015027719322044882, 0.0433547477660741], [0.020090300063586357, 0.033850151458570364], [0.020090300063586357, 0.033729899361447206], [0.033100922805288105, 0.033725670135473826], [0.033100922805288105, 0.03020580678032925], [0.020090300063586357, 0.0301966800337145], [0.020090300063586357, 0.012397521046909792], [0.07892195508425631, 0.012339513252684174], [0.10901455590072147, 0.012188267714676173], [0.10901455590072147, 0.008969435332574308], [0.11484456868478596, 0.008904534181001615], [0.11484456868478596, -0.01827271451334495], [0.10901455590072147, -0.01832327269504131], [0.10901455590072147, -0.021542988606907898], [0.07525104498556777, -0.021691279467347693], [0.020090300063586357, -0.021742075780327594], [0.020090300063586357, -0.047935524145097046], [-0.020090300736927705, -0.04793366492642751], [-0.020090300736927705, -0.02174215346380131], [-0.07891278502611314, -0.021684164383825283]], 'holes': []}], 'simplify_tolerance': 4.593782740658026e-05, 'sketch_entity_count': 36}
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
