#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0, -0.063747, -5.100000000091143e-07], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.29611599, 'zmax': 0.29611599, 'profiles': [{'outer': [[-0.29575551, 0.03050904], [-0.29468552000000003, 0.045019039999999996], [-0.29298452, 0.04878704], [-0.29064650000000003, 0.05056704], [-0.28726450000000003, 0.05184304], [-0.2793895, 0.052450039999999996], [-0.19465751, 0.05362803], [-0.13582751, 0.05420602], [-5.100000000091143e-07, 0.054714], [0.11553248999999999, 0.05432698], [0.19465649, 0.05362797], [0.27938848, 0.05244996], [0.28726348, 0.05184296], [0.29064548, 0.050566959999999994], [0.2929835, 0.04878696], [0.2946845, 0.04501896], [0.29575449, 0.030508959999999995], [0.2961165, -2.0400000000087015e-06], [0.29575449, -0.030513040000000005], [0.2946845, -0.04502304], [0.29298346999999997, -0.04879003], [0.29070946, -0.05061604], [0.28777045, -0.05221304], [0.27698245, -0.05348403], [0.23516247999999998, -0.054171029999999995], [-5.300000000091143e-07, -0.054714], [-0.20727653000000001, -0.05429997], [-0.23516353, -0.05417097], [-0.27698353000000003, -0.05348396], [-0.28777153, -0.05221296], [-0.29071054, -0.05061596], [-0.29298455, -0.04878996000000001], [-0.29468552000000003, -0.04502296], [-0.29575551, -0.030512960000000006], [-0.2961165, -1.959999999995299e-06]], 'holes': []}], 'simplify_tolerance': 0.00011844660000000001, 'sketch_entity_count': 35}
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
