#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.03079722, -0.039124095, -0.11919316499999999], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.198720395, 'zmax': 0.198720395, 'profiles': [{'outer': [[-0.180117835, -0.025334660000000002], [-0.17733065080806143, -0.006015918156974534], [-0.18154668499999999, 0.003297350000000001], [-0.184541755, 0.01143081], [-0.17967819499999999, 0.028082450000000002], [-0.184789085, 0.0458332], [-0.182398495, 0.07919140999999999], [-0.17868273995152545, 0.08320977634205297], [-0.173825405, 0.11614923], [-0.112604585, 0.15568996000000002], [0.087050085, 0.19163112], [0.160361205, 0.14406681999999998], [0.16368149048581346, 0.12917993541962217], [0.165307235, 0.12815709], [0.1734609721178358, 0.08533249671777386], [0.181326875, 0.05006481], [0.18069994648390247, 0.04731236821385779], [0.181326875, 0.04401965], [0.17970221618330348, 0.03774807958600807], [0.17973570110569556, 0.03732799712200597], [0.181326875, 0.03267126], [0.18034508635052304, 0.029683002393447847], [0.181326875, 0.01736605], [0.17893289301306364, 0.010021415308784806], [0.184789085, 0.00030225000000000043], [0.179927059283433, -0.01309216685033784], [0.181326875, -0.01739354], [0.18048228669286312, -0.019131912123251143], [0.184789085, -0.032368999999999995], [0.176518235, -0.09260064], [0.1709370831606882, -0.09666225821405038], [0.160361205, -0.1440943], [0.087050085, -0.19163112], [-0.113923515, -0.14200596], [-0.171022615, -0.09446912], [-0.1754434187115812, -0.059310589811430364], [-0.177150215, -0.05800592]], 'holes': []}], 'simplify_tolerance': 7.6652448e-05, 'sketch_entity_count': 37}
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
