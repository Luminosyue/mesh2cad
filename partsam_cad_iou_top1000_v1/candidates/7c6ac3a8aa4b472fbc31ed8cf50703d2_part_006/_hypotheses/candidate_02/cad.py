#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.00265352499999999, -0.176063255, -0.3687053], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.136269255, 'zmax': 0.136269255, 'profiles': [{'outer': [[-0.13050109, -0.164469225], [-0.13050109, -0.128761485], [-0.13025694999999998, -0.10117189500000001], [-0.12885302999999998, -0.07455895500000001], [-0.12885302999999998, -0.04178108500000001], [-0.13050109, -0.00662268500000001], [-0.13050109, 0.03329671499999999], [-0.12885302999999998, 0.068882375], [-0.12885302999999998, 0.218183445], [-0.13050109, 0.25126653499999996], [-0.13129458, 0.281541815], [-0.12494656999999998, 0.282518435], [-0.10663488999999998, 0.283434015], [-0.07806870999999999, 0.284166505], [-0.04199474999999997, 0.28465478499999997], [0.0004272399999999954, 0.284776885], [0.044131100000000034, 0.285509365], [0.08038815999999999, 0.286852165], [0.10571930000000002, 0.286058675], [0.12390887, 0.283495055], [0.12708290000000003, 0.281541815], [0.12995171000000003, 0.251632765], [0.13129458000000002, 0.21787828499999998], [0.12909718, 0.162454975], [0.12708290000000003, 0.11807973499999999], [0.12708290000000003, -0.10117189500000001], [0.12665564, -0.13034848500000001], [0.12793743000000002, -0.16758219500000002], [0.12793743000000002, -0.21391068500000002], [0.12574005000000002, -0.255783335], [0.12647252, -0.282274235], [0.10061320889844148, -0.28254436523887844], [0.07446739000000002, -0.284837825], [0.03784409, -0.28666900500000003], [-0.0020753199999999916, -0.286852165], [-0.04199474999999997, -0.28666900500000003], [-0.07806870999999999, -0.286241755], [-0.10663488999999998, -0.285509275], [-0.12494656999999998, -0.284593685], [-0.13129458, -0.283617065], [-0.13129458, -0.213300335]], 'holes': []}], 'simplify_tolerance': 0.000114740866, 'sketch_entity_count': 41}
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
