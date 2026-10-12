#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [7.085000000003894e-06, -0.002878920000000007, 7.039999999999824e-06], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.16235644500000002, 'zmax': 0.16235644500000002, 'profiles': [{'outer': [[-0.15438116000000002, 0.10854490000000001], [-0.14464791999999999, 0.15944074], [-0.13135585, 0.20643468], [-0.11480504, 0.24836905], [-0.09542433, 0.28417198], [-0.07368533, 0.31294291], [-0.05014547, 0.33403872], [-0.02540503, 0.34690206], [2.1429999999999824e-05, 0.35123269], [0.02540503, 0.34690206], [0.05018834, 0.33403872], [0.0737282, 0.31294291], [0.09542431999999999, 0.28417198], [0.11480504, 0.24836905], [0.13135583, 0.20643468], [0.14464791999999999, 0.15944074], [0.15442403, 0.10854490000000001], [0.16034116999999998, 0.05494778000000001], [0.16235641, 2.1430000000007172e-05], [0.16034116999999998, -0.054947779999999995], [0.15442403, -0.10854491], [0.14464791999999999, -0.15944074], [0.13135583, -0.2064347], [0.11480504, -0.24836908000000002], [0.09542431999999999, -0.28417198], [0.0737282, -0.31294291], [0.05018834, -0.33403872], [0.02540503, -0.34690206], [2.1429999999999824e-05, -0.35123269], [-0.02540503, -0.34690206], [-0.05014547, -0.33403872], [-0.07368533, -0.31294291], [-0.09542433, -0.28417198], [-0.11480504, -0.24836908000000002], [-0.13135585, -0.2064347], [-0.14464791999999999, -0.15944074], [-0.15438116000000002, -0.10854491], [-0.16034116999999998, -0.054947779999999995], [-0.16235641, 2.1430000000007172e-05], [-0.16034116999999998, 0.05494778000000001]], 'holes': []}], 'simplify_tolerance': 0.00014049307600000002, 'sketch_entity_count': 40}
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
