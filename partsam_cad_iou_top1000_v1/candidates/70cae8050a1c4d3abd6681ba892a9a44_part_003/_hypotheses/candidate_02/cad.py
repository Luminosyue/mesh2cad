#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.043493089999999984, -0.289686985, -0.04448031999999999], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.33033663, 'zmax': 0.33033663, 'profiles': [{'outer': [[-0.107390245, -0.04836617999999998], [-0.099325845, 0.003910610000000016], [-0.08733054500000001, 0.04933874000000002], [-0.07201222500000001, 0.08937711000000001], [-0.050412605, 0.13375160000000003], [-0.04497942122525681, 0.1465469747668364], [-0.04287507500000001, 0.15822849000000003], [-0.030596115000000035, 0.19668634000000002], [-0.01009062500000002, 0.23336119000000002], [0.003375513763880044, 0.2579488701248729], [0.015237294999999984, 0.29706595], [0.031001384999999992, 0.32397428000000006], [0.06423156499999999, 0.33195767], [0.09640812500000001, 0.32405534999999996], [0.10714717499999998, 0.30042947], [0.10714726499999999, 0.16315311866517246], [0.107390245, 0.05874046000000002], [0.10714720499999997, -0.30038896000000004], [0.099569075, -0.31963816], [0.09871806499999997, -0.32117810999999996], [0.07351174500000002, -0.33195767], [0.04502289500000001, -0.33074194], [0.035378034999999974, -0.32810783], [0.004174074999999999, -0.30950701], [-0.005876074999999981, -0.3011184], [-0.03691793500000001, -0.26914446999999997], [-0.061556895, -0.23230754999999997], [-0.08104925500000001, -0.19052662999999997], [-0.096651245, -0.14363963999999999], [-0.10645817500000002, -0.10319603999999999]], 'holes': []}], 'simplify_tolerance': 0.000132783068, 'sketch_entity_count': 30}
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
