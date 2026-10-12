#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.07328786500000001, -0.46524904499999997, 0.05732515], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.027651214999999993, 'zmax': 0.027651215000000007, 'profiles': [{'outer': [[-0.06552484, -0.006672575000000014], [-0.05607644, -0.001494635000000022], [-0.041023090000000005, 0.0048042949999999585], [-0.030667229999999997, 0.007206424999999961], [-0.02111208, 0.008754474999999984], [-0.013104979999999995, 0.010622784999999968], [-0.005898569999999999, 0.013291814999999985], [0.001521339999999996, 0.017188624999999957], [0.007927039999999996, 0.02108542499999999], [0.012411020000000002, 0.023754464999999947], [0.01694838, 0.027704604999999993], [0.019724159999999998, 0.030213484999999984], [0.02100531, 0.033256184999999994], [0.023300679999999997, 0.03384338499999995], [0.03061384, 0.03432379499999999], [0.03435049, 0.034483954999999955], [0.04219746, 0.03469745499999999], [0.04636115, 0.03475083499999998], [0.05442164, 0.034590705], [0.05794477, 0.03443057499999996], [0.06098747, 0.034217044999999946], [0.06349636, 0.03395013499999999], [0.06525792, 0.03368322499999998], [0.06653907, 0.03309602499999997], [0.0664323, 0.027864734999999974], [0.068354, 0.019964414999999958], [0.07139671, 0.003896814999999998], [0.07273123, -0.003416345000000043], [0.0719839, -0.008487505000000006], [0.07064938, -0.012437685000000032], [0.07022233, -0.02231313500000004], [0.07032909, -0.031708135000000026], [0.06931486, -0.03218855500000001], [0.03600191203659119, -0.03218978889891913], [0.02378111, -0.03245546500000002], [0.021026273535191407, -0.025737528239240658], [0.016244817717908398, -0.02788334670771331], [0.012967198928586915, -0.029686036849962506], [0.007927039999999996, -0.032668995000000034], [0.0070729500000000015, -0.033096035000000024], [-0.000934170000000005, -0.03464408500000005], [-0.0018950200000000042, -0.034750835000000035], [-0.059973240000000004, -0.034750835000000035], [-0.06568498, -0.034590705000000055], [-0.07257109, -0.03384335500000002], [-0.07273123000000001, -0.016761525000000055], [-0.07054262, -0.011263325000000046]], 'holes': []}], 'simplify_tolerance': 2.9092492000000005e-05, 'sketch_entity_count': 50}
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
