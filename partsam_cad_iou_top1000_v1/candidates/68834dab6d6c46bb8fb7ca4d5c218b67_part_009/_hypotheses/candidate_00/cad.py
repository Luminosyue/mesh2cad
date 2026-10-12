#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.317654685, -0.260287355, -0.07366484000000001], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.009545634999999997, 'zmax': 0.009545634999999997, 'profiles': [{'outer': [[-0.07540812000000001, -0.010935654999999989], [-0.07394279000000001, -0.008108245000000014], [-0.07166309000000001, -0.005865145000000016], [-0.06878863, -0.004425964999999976], [-0.06560306, -0.003929245000000026], [-0.062417490000000006, -0.004425964999999976], [-0.05954303000000001, -0.005865145000000016], [-0.057262030000000005, -0.008108245000000014], [-0.055798000000000014, -0.010935654999999989], [-0.055293430000000005, -0.014067635000000023], [-0.05527644000000001, -0.015189194999999989], [-0.05578231000000001, -0.018327705000000027], [-0.05724895000000001, -0.02115773500000001], [-0.05953257000000001, -0.023404705000000026], [-0.062412270000000006, -0.024847854999999974], [-0.06560306, -0.025344564999999986], [-0.06879386000000001, -0.024847854999999974], [-0.07167224000000001, -0.023404705000000026], [-0.07395717, -0.02115773500000001], [-0.07542381000000001, -0.018327705000000027], [-0.07592968000000001, -0.015189194999999989], [-0.07591269, -0.014067635000000023]], 'holes': []}, {'outer': [[0.05527628999999998, 0.014284994999999995], [0.05529318999999999, 0.015132244999999989], [0.055798669999999995, 0.018287315], [0.05726313999999999, 0.021134385000000006], [0.05954366999999999, 0.02339408500000001], [0.06241805, 0.024844265000000004], [0.06560297999999998, 0.025344564999999986], [0.06878922999999998, 0.024844265000000004], [0.07166229999999998, 0.02339408500000001], [0.07394413999999999, 0.021134385000000006], [0.07540859999999999, 0.018287315], [0.07591277999999999, 0.015132244999999989], [0.07592968, 0.014284994999999995], [0.0754242, 0.011124754999999986], [0.07395712999999998, 0.008272475000000001], [0.07167269999999998, 0.006008815000000001], [0.06879442, 0.004556074999999993], [0.06560297999999998, 0.0040557449999999995], [0.06241154999999998, 0.004556074999999993], [0.05953327, 0.006008815000000001], [0.05724884999999999, 0.008272475000000001], [0.05578176999999998, 0.011124754999999986]], 'holes': []}], 'simplify_tolerance': 3.0371872e-05, 'sketch_entity_count': 53}
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
