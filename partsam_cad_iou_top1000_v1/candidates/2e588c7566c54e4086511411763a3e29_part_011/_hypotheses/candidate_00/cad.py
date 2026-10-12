#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.111929625, 0.08700364, 0.1290134], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.07729828, 'zmax': 0.07729828, 'profiles': [{'outer': [[-0.035557240000000004, 2.3149999999888538e-06], [-0.035283049999999996, 0.0047237749999999995], [-0.034497700000000006, 0.009231444999999991], [-0.03329409, 0.013367374999999987], [-0.031802380000000005, 0.017024634999999982], [-0.030152659999999998, 0.020175355000000006], [-0.028447180000000002, 0.022838145000000004], [-0.026760279999999997, 0.025068745000000003], [-0.0251431, 0.02691829500000001], [-0.02341438, 0.028647005000000003], [-0.02133248, 0.030454724999999988], [-0.018846280000000007, 0.03228104500000001], [-0.015900029999999996, 0.034046935], [-0.012484410000000001, 0.035640895000000006], [-0.008622669999999999, 0.036928135], [-0.004407759999999997, 0.037773904999999997], [2.329999999994836e-06, 0.038066674999999994], [0.004412429999999995, 0.037773904999999997], [0.008622700000000011, 0.036928135], [0.012484419999999996, 0.035640895000000006], [0.015904680000000004, 0.034046935], [0.018846310000000005, 0.03228104500000001], [0.021337140000000004, 0.030454724999999988], [0.023414390000000007, 0.028647005000000003], [0.025143109999999996, 0.02691829500000001], [0.026760299999999987, 0.025068745000000003], [0.028447200000000006, 0.022838145000000004], [0.030152679999999987, 0.020175355000000006], [0.03180241, 0.017024634999999982], [0.03329412000000001, 0.013367374999999987], [0.03449770999999999, 0.009231444999999991], [0.035283079999999994, 0.0047237749999999995], [0.03555723999999999, 2.3149999999888538e-06], [0.035283079999999994, -0.0047237749999999995], [0.03449770999999999, -0.009231455], [0.03329412000000001, -0.013367365000000006], [0.03180241, -0.01702463500000001], [0.030152679999999987, -0.020175365], [0.028447200000000006, -0.022838155], [0.026760299999999987, -0.025068754999999998], [0.025143109999999996, -0.02691829500000001], [0.023414390000000007, -0.028647025000000007], [0.021337140000000004, -0.03045473500000001], [0.018846310000000005, -0.03228104500000001], [0.015904680000000004, -0.03404694500000001], [0.012484419999999996, -0.035640895000000006], [0.008622700000000011, -0.036928135], [0.004412429999999995, -0.03777390500000001], [2.329999999994836e-06, -0.03806667500000001], [-0.004407759999999997, -0.03777390500000001], [-0.008622669999999999, -0.036928135], [-0.012484410000000001, -0.035640895000000006], [-0.015900029999999996, -0.03404694500000001], [-0.018846280000000007, -0.03228104500000001], [-0.02133248, -0.03045473500000001], [-0.02341438, -0.028647025000000007], [-0.0251431, -0.02691829500000001], [-0.026760279999999997, -0.025068754999999998], [-0.028447180000000002, -0.022838155], [-0.030152659999999998, -0.020175365], [-0.031802380000000005, -0.01702463500000001], [-0.03329409, -0.013367365000000006], [-0.034497700000000006, -0.009231455], [-0.035283049999999996, -0.0047237749999999995]], 'holes': []}], 'simplify_tolerance': 1.522667e-05, 'sketch_entity_count': 67}
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
