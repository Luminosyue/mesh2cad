#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.06597268, -0.46588063, -0.013473035000000001], 'basis': [[0.0, 0.9999235915937674, -0.012361673601130286], [-0.13250652286233844, 0.012252670011287454, 0.9911063986659189], [0.9911821333130115, 0.0016380023856449359, 0.1324963982501111]], 'axis': [-0.012361673601130286, 0.9911063986659189, 0.1324963982501111], 'zmin': -0.03752466166234621, 'zmax': 0.031012495941282477, 'profiles': [{'outer': [[-0.06893824909447507, 0.01871131077380901], [-0.04512222575254601, 0.03930482927296437], [0.0017950374277299417, 0.05230155467021322], [0.03520373304076484, 0.05550563460907137], [0.06019961375581092, 0.05627058931867959], [0.07613593158890483, 0.05059203250442339], [0.07670774394708657, 0.05016181136963051], [0.0820016188960885, 0.03890701459778919], [0.0772438413200396, 0.027234670149372288], [0.06310926057255245, 0.020786270954617842], [0.054225463491878866, 0.017427598409301574], [0.06310926057255245, 0.014501101231116474], [0.07695751238584218, 0.00904091413477461], [0.0772438413200396, 0.008830946456022098], [0.0820016188960885, -0.001145694804664698], [0.0772438413200396, -0.011215951675394143], [0.06310926057255245, -0.01676055993265065], [0.05413679687820817, -0.019555994762027528], [0.06310926057255245, -0.02230630615864026], [0.0772438413200396, -0.02814078837677715], [0.0820016188960885, -0.03914440116221032], [0.07671318598998052, -0.050196413088036046], [0.07613593158890483, -0.050505092235125726], [0.06021594253462324, -0.05653580067810937], [0.03531261100047036, -0.05628230174339694], [0.0021434341781614323, -0.05342874419077949], [-0.04462684349149901, -0.040599935584558065], [-0.06811824742477778, -0.028441240620024028], [-0.07587757463511607, -0.015447769260967997], [-0.07817991440402289, -0.004802191951553245], [-0.07598644861962592, 0.00588265896607317]], 'holes': []}], 'simplify_tolerance': 3.2036306660022276e-05, 'sketch_entity_count': 31}
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
