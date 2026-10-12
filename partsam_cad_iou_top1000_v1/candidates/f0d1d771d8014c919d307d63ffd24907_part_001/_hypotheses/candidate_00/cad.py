#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.02247926, 0.032931515, 0.18566934000000002], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.10516354000000001, 'zmax': 0.10516354, 'profiles': [{'outer': [[-0.03268978499999999, 0.03333334], [-0.025695934999999996, 0.03919705], [-0.017717755, 0.04358162], [-0.009014294999999999, 0.04627576], [5.000000004307115e-09, 0.04717381], [0.009014305, 0.04627576], [0.017717755, 0.04358162], [0.025695935000000003, 0.03919705], [0.032689785, 0.03333334], [0.038492085, 0.0262018], [0.042740205, 0.018066560000000002], [0.045382335, 0.00919176], [0.046263035, 0.0], [0.045382335, -0.00919176], [0.042740205, -0.018066569999999997], [0.038492085, -0.02620181], [0.032689785, -0.033333339999999996], [0.025695935000000003, -0.03924988], [0.017717755, -0.043581629999999996], [0.009014305, -0.046275769999999994], [5.000000004307115e-09, -0.04717381], [-0.009014294999999999, -0.046275769999999994], [-0.017717755, -0.043581629999999996], [-0.025695934999999996, -0.03924988], [-0.03268978499999999, -0.033333339999999996], [-0.038440275, -0.02620181], [-0.042740204999999996, -0.018066569999999997], [-0.045382324999999994, -0.00919176], [-0.046263035, 0.0], [-0.045382324999999994, 0.00919176], [-0.042740204999999996, 0.018066560000000002], [-0.038440275, 0.0262018]], 'holes': []}], 'simplify_tolerance': 1.8869524e-05, 'sketch_entity_count': 35}
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
