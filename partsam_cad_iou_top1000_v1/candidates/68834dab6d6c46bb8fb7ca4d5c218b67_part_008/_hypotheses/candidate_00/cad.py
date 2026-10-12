#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.316963645, -0.26028737, -0.07366479000000001], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.010237245000000006, 'zmax': 0.010237245000000006, 'profiles': [{'outer': [[-0.07592974000000001, -0.015189199999999958], [-0.07591275, -0.014067620000000003], [-0.07540818, -0.010935639999999969], [-0.07394284000000001, -0.008108229999999994], [-0.07166312000000001, -0.0058650999999999565], [-0.06878865, -0.004425919999999972], [-0.06560307000000001, -0.003929169999999982], [-0.062417490000000006, -0.004425919999999972], [-0.05954301000000001, -0.0058650999999999565], [-0.05726199000000001, -0.008108229999999994], [-0.05579796000000001, -0.010935639999999969], [-0.05529339000000001, -0.014067620000000003], [-0.0552764, -0.015189199999999958], [-0.05578227000000001, -0.018327690000000008], [-0.05724892000000001, -0.021157749999999975], [-0.059532550000000004, -0.023404749999999974], [-0.06241226000000001, -0.02484789999999998], [-0.06560307000000001, -0.02534460999999999], [-0.06879388, -0.02484789999999998], [-0.07167228, -0.023404749999999974], [-0.07395722, -0.021157749999999975], [-0.07542386000000001, -0.018327690000000008]], 'holes': []}, {'outer': [[0.05527642999999999, 0.01428507000000001], [0.05529333, 0.015132320000000005], [0.05579878999999999, 0.018288640000000023], [0.05726328, 0.02113443000000001], [0.05954379999999998, 0.023394130000000013], [0.062416849999999996, 0.02484431000000001], [0.06560309, 0.025344610000000017], [0.06878932999999998, 0.02484431000000001], [0.07166238, 0.023394130000000013], [0.07394420999999998, 0.02113443000000001], [0.07540865999999999, 0.018288640000000023], [0.07591283999999998, 0.015132320000000005], [0.07592974, 0.01428507000000001], [0.07542425999999999, 0.01112353000000002], [0.0739572, 0.008272550000000045], [0.07167277999999999, 0.006008950000000013], [0.06879451, 0.004556140000000042], [0.06560309, 0.004055880000000012], [0.06241165999999998, 0.004556140000000042], [0.059533399999999986, 0.006008950000000013], [0.05724899, 0.008272550000000045], [0.05578190999999999, 0.01112353000000002]], 'holes': []}], 'simplify_tolerance': 3.0371896e-05, 'sketch_entity_count': 65}
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
