#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.140255425, -0.124632025, -0.12812602], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.027887925000000008, 'zmax': 0.027887924999999994, 'profiles': [{'outer': [[-0.31003559999999997, 0.002069454999999998], [-0.31676579000000005, 0.018701625], [-0.31425164, 0.03606873499999999], [-0.29943738, 0.05014806499999999], [-0.28334672, 0.054325454999999995], [-0.08553972000000001, 0.05691692499999999], [0.12773904999999997, 0.05691685499999999], [0.27000225, 0.049993184999999996], [0.28617031, 0.04771107499999999], [0.30257041, 0.04047801499999999], [0.31444502, 0.027404334999999988], [0.31676579, 0.009495724999999997], [0.31216294, -0.007291174999999997], [0.30040432, -0.020442205000000005], [0.22679723000000002, -0.052236745000000015], [0.21004898, -0.056375435000000015], [0.11632856999999999, -0.05691692499999999], [-0.21840386, -0.05691682500000002], [-0.23522946, -0.05567907500000001], [-0.2509333, -0.04960638500000002]], 'holes': [[[-0.08553973000000001, 0.045274385], [-0.28145141, 0.04283762499999999], [-0.29545341, 0.039201765], [-0.30326668, 0.032239455], [-0.30535535, 0.021099754999999998], [-0.29986287, 0.008451564999999994], [-0.24524743, -0.039433675000000015], [-0.23232847, -0.044384665000000004], [-0.21840386, -0.045274295000000006], [0.11632856999999999, -0.04527439500000001], [0.20892728, -0.044771585000000017], [0.22242647999999998, -0.041445155], [0.29324859999999997, -0.011236494999999999], [0.30187417, -0.0018373649999999936], [0.3051619, 0.010114604999999999], [0.30415625, 0.021989204999999998], [0.29560811, 0.031117565], [0.28241844, 0.036687424999999996], [0.26930607, 0.03838932499999999], [0.12773904999999997, 0.045274314999999996]]]}], 'simplify_tolerance': 0.00012670631600000001, 'sketch_entity_count': 61}
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
