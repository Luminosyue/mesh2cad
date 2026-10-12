#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.164523475, 0.14638748499999998, 0.0043422750000000065], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.16660011500000002, 'zmax': 0.166600115, 'profiles': [{'outer': [[-0.230453115, -0.09980398499999998], [-0.18502265499999998, -0.07840579499999999], [-0.167949655, -0.051804454999999985], [-0.161510685, -0.021593324999999983], [-0.155364425, 0.011186845000000029], [-0.15360833499999998, 0.013235635000000023], [-0.065934355, 0.04357677500000001], [-0.05679621499999999, 0.050991355000000016], [-0.013056774999999993, 0.12575489500000003], [-0.010715334999999994, 0.127120795], [0.010715355000000006, 0.127120795], [0.013056795000000006, 0.12575489500000003], [0.056796225000000006, 0.050991355000000016], [0.065934345, 0.04357677500000001], [0.153608335, 0.013235635000000023], [0.155364415, 0.011186845000000029], [0.161510695, -0.021593324999999983], [0.167949665, -0.051804454999999985], [0.18502268500000002, -0.07840579499999999], [0.230453155, -0.09980398499999998], [0.265217055, -0.11086079499999998], [0.266387775, -0.11349493499999999], [0.260241495, -0.12581997499999997], [0.257282155, -0.12712079499999998], [0.222355665, -0.11599895499999999], [0.173445555, -0.09154388499999999], [0.151592095, -0.05882876499999998], [0.143624685, -0.02357706499999998], [0.143624685, 0.0023089050000000277], [0.141998695, 0.004455215000000012], [0.05783687500000001, 0.027804615000000005], [0.04307278500000001, 0.03973943500000002], [0.004991835000000007, 0.11245423500000001], [0.0026829150000000066, 0.11385256500000002], [-0.0026829049999999932, 0.11385256500000002], [-0.004991804999999993, 0.11245423500000001], [-0.04307276499999999, 0.03973943500000002], [-0.05783684499999999, 0.027804615000000005], [-0.141998675, 0.004455215000000012], [-0.14362466499999998, 0.0023089050000000277], [-0.14362466499999998, -0.02357706499999998], [-0.151592055, -0.05882876499999998], [-0.173445555, -0.09154388499999999], [-0.222355645, -0.11599895499999999], [-0.257282155, -0.12712079499999998], [-0.260241495, -0.12581997499999997], [-0.266387775, -0.11349493499999999], [-0.265217015, -0.11086079499999998]], 'holes': []}], 'simplify_tolerance': 0.00010655511, 'sketch_entity_count': 51}
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
