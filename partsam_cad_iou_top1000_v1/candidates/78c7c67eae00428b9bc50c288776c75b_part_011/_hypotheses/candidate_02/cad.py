#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.11456107, -0.35899375499999997, -0.073824185], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.058188955, 'zmax': 0.058188955, 'profiles': [{'outer': [[-0.13160149499999996, 0.02312526999999999], [-0.10914184499999996, 0.025616029999999998], [-0.099545712638043, 0.02580092704186844], [-0.02754847499999996, 0.028622099999999998], [0.005818915000000036, 0.028622099999999998], [0.03347475500000002, 0.027934990000000007], [0.08182956500000005, 0.025573090000000007], [0.08321431937557389, 0.02491266807185354], [0.08384792500000005, 0.027376720000000007], [0.08960242500000004, 0.03914336], [0.09389679500000003, 0.04210647999999999], [0.097332315, 0.04472605], [0.10214201500000003, 0.04738858], [0.10862655500000001, 0.04932107000000001], [0.11717237500000005, 0.05112468999999999], [0.12434400500000004, 0.051811800000000005], [0.13005553500000006, 0.05078113999999999], [0.13288982500000002, 0.04962165], [0.13417335854581594, 0.048707627318181075], [0.13611061500000005, 0.04773213], [0.139159635, 0.043910130000000006], [0.13933141500000001, 0.042535909999999996], [0.14001850500000002, 0.03532134999999999], [0.140920325, 0.021106909999999993], [0.1401337452021907, 0.01019741270162941], [0.13929729288836384, -0.0036247243687424764], [0.13920286843549776, -0.008723507402895712], [0.13924555500000002, -0.026861400000000007], [0.13684068500000002, -0.029609819999999995], [0.12799425500000006, -0.033345929999999996], [0.122669205, -0.034462469999999995], [0.11167557500000003, -0.03467719], [0.10184143500000004, -0.03356065], [0.09578634500000005, -0.03201466], [0.08938769500000004, -0.02939509], [0.08831409500000004, -0.028321490000000005], [0.08590258714335355, -0.024192428324972853], [0.08522213500000003, -0.025873690000000005], [0.08444915500000005, -0.027290830000000002], [0.08131424500000001, -0.028836830000000008], [0.07116783626361713, -0.0325865882616086], [0.05945582500000002, -0.038198590000000004], [0.031714065000000013, -0.04094699], [0.00448764500000004, -0.043094190000000004], [0.001390752491933178, -0.04411434271211477], [-0.02016215499999996, -0.051811800000000005], [-0.050523444999999945, -0.05159709], [-0.08045534499999996, -0.05090998000000001], [-0.10566337499999995, -0.05056642], [-0.13048495499999996, -0.04889162], [-0.13718418499999996, -0.045069609999999996], [-0.13860131499999997, -0.030339859999999996], [-0.13988967499999996, -0.011745160000000004], [-0.14092032499999996, 0.006505999999999998], [-0.14023320499999997, 0.01853028999999999]], 'holes': []}], 'simplify_tolerance': 5.6368129999999995e-05, 'sketch_entity_count': 64}
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
