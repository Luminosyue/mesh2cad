#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.069538485, 0.396489085, -0.044579444999999995], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.015480564999999995, 'zmax': 0.015480565000000002, 'profiles': [{'outer': [[-0.030669874999999996, -0.06379708500000003], [-0.030085174999999995, 0.021367164999999966], [-0.028379934999999995, 0.071062595], [-0.024238654999999994, 0.09249976499999996], [-0.018976774999999994, 0.098687315], [-0.013958524999999996, 0.102536285], [-0.006552934999999996, 0.10351070499999998], [0.005968355000000002, 0.10102590499999997], [0.018099895000000005, 0.09698209499999999], [0.02443360500000001, 0.09313312499999998], [0.027697895, 0.08840724499999997], [0.030669875, 0.08168372499999998], [0.029841635000000005, 0.06049010499999996], [0.021656485000000003, 0.012256414999999965], [0.005919595000000007, -0.07017949500000004], [0.002606565000000005, -0.084698355], [0.0015446696657240961, -0.08734437340203152], [0.0005516950000000048, -0.093058855], [-0.0026969949999999937, -0.098362595], [-0.0077931749999999925, -0.10200569500000001], [-0.013875384999999997, -0.10351070500000004], [-0.020082144999999996, -0.10243120500000003], [-0.025458564999999996, -0.09916177500000001], [-0.029029004999999997, -0.094086385], [-0.030471704999999995, -0.08809760500000002], [-0.02970200672165813, -0.08365469918952011], [-0.030377534999999997, -0.07880315500000001]], 'holes': []}], 'simplify_tolerance': 4.1404282000000003e-05, 'sketch_entity_count': 30}
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
