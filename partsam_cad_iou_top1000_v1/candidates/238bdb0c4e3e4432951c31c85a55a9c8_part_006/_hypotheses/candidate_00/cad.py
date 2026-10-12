#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.39459926, -0.16139067499999998, 0.016738425], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.004193190000000013, 'zmax': 0.004193190000000013, 'profiles': [{'outer': [[-0.028204374999999997, -0.041108475000000005], [-0.030949915, -0.04030974500000001], [-0.033445885, -0.038961935], [-0.035592395, -0.037164855000000024], [-0.037389504999999996, -0.03501831500000002], [-0.038737315, -0.032522365000000025], [-0.039585934999999996, -0.029776825000000007], [-0.039835535, -0.026981315000000006], [-0.039585934999999996, -0.024185855000000006], [-0.038737315, -0.021440315000000015], [-0.037389504999999996, -0.01894434500000003], [-0.035592395, -0.016797795000000004], [-0.033445885, -0.015000715000000026], [-0.030949915, -0.01365290500000002], [-0.028204374999999997, -0.012804255000000014], [-0.025408885, -0.012554695000000005], [-0.022613395, -0.012804255000000014], [-0.019867854999999997, -0.01365290500000002], [-0.017371884999999997, -0.015000715000000026], [-0.015225375, -0.016797795000000004], [-0.013428264999999998, -0.01894434500000003], [-0.012080455, -0.021440315000000015], [-0.011281745, -0.024185855000000006], [-0.010982235, -0.026981315000000006], [-0.011281745, -0.029776825000000007], [-0.012080455, -0.032522365000000025], [-0.013428264999999998, -0.03501831500000002], [-0.015225375, -0.037164855000000024], [-0.017371884999999997, -0.038961935], [-0.019867854999999997, -0.04030974500000001], [-0.022613395, -0.041108475000000005], [-0.025408885, -0.04140798500000001]], 'holes': []}, {'outer': [[0.025408885, 0.012554684999999982], [0.022613405000000003, 0.01280428499999997], [0.019867845000000002, 0.013652934999999977], [0.017371905, 0.015000744999999982], [0.015225365000000001, 0.01679782499999999], [0.013428285000000002, 0.01894433499999998], [0.012080455, 0.021440314999999988], [0.011231825, 0.024185874999999996], [0.010982245000000002, 0.02698136499999998], [0.011231825, 0.02977682499999998], [0.012080455, 0.03252239499999998], [0.013428285000000002, 0.035018334999999984], [0.015225365000000001, 0.037164874999999986], [0.017371905, 0.03896195499999998], [0.019867845000000002, 0.040309764999999984], [0.022613405000000003, 0.04110850499999999], [0.025408885, 0.04140798499999998], [0.028204365000000002, 0.04110850499999999], [0.030949915, 0.040309764999999984], [0.033445875, 0.03896195499999998], [0.035592405, 0.037164874999999986], [0.037389495, 0.035018334999999984], [0.038737305, 0.03252239499999998], [0.039536025, 0.02977682499999998], [0.039835535000000005, 0.02698136499999998], [0.039536025, 0.024185874999999996], [0.038737305, 0.021440314999999988], [0.037389495, 0.01894433499999998], [0.035592405, 0.01679782499999999], [0.033445875, 0.015000744999999982], [0.030949915, 0.013652934999999977], [0.028204365000000002, 0.01280428499999997]], 'holes': []}], 'simplify_tolerance': 1.6563193999999998e-05, 'sketch_entity_count': 64}
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
