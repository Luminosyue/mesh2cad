#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.111929625, 0.08700364, 0.1290134], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.035557240000000004, 'zmax': 0.03555723999999999, 'profiles': [{'outer': [[-0.07729828, 2.3149999999888538e-06], [-0.07702410000000001, 0.0047237749999999995], [-0.07623873, 0.009231444999999991], [-0.07503513, 0.013367374999999987], [-0.07354344000000002, 0.017024634999999982], [-0.0718937, 0.020175355000000006], [-0.07018823000000002, 0.022838145000000004], [-0.06850133, 0.025068745000000003], [-0.06688414000000001, 0.02691829500000001], [-0.06515543000000001, 0.028647005000000003], [-0.06307817000000002, 0.030454724999999988], [-0.060587329999999995, 0.03228104500000001], [-0.05764572000000001, 0.034046935], [-0.05422545000000001, 0.035640895000000006], [-0.050363729999999995, 0.036928135], [-0.04615345000000001, 0.037773904999999997], [-0.04174335000000001, 0.038066674999999994], [-0.03733327, 0.037773904999999997], [-0.033118350000000005, 0.036928135], [-0.02925662000000001, 0.035640895000000006], [-0.02584101000000001, 0.034046935], [-0.022894750000000005, 0.03228104500000001], [-0.02040855000000001, 0.030454724999999988], [-0.01832665, 0.028647005000000003], [-0.01659793000000001, 0.02691829500000001], [-0.014980740000000006, 0.025068745000000003], [-0.013293860000000005, 0.022838145000000004], [-0.011588360000000006, 0.020175355000000006], [-0.009933486250307615, 0.017011974999999985], [0.07729828, 0.017011974999999985], [0.07729828, -0.01804683500000001], [-0.010473869952836336, -0.01804683500000001], [-0.011588360000000006, -0.020175365], [-0.013293860000000005, -0.022838155], [-0.014980740000000006, -0.025068754999999998], [-0.01659793000000001, -0.02691829500000001], [-0.01832665, -0.028647025000000007], [-0.02040855000000001, -0.03045473500000001], [-0.022894750000000005, -0.03228104500000001], [-0.02584101000000001, -0.03404694500000001], [-0.02925662000000001, -0.035640895000000006], [-0.033118350000000005, -0.036928135], [-0.03733327, -0.03777390500000001], [-0.04174335000000001, -0.03806667500000001], [-0.04615345000000001, -0.03777390500000001], [-0.050363729999999995, -0.036928135], [-0.05422545000000001, -0.035640895000000006], [-0.05764572000000001, -0.03404694500000001], [-0.060587329999999995, -0.03228104500000001], [-0.06307817000000002, -0.03045473500000001], [-0.06515543000000001, -0.028647025000000007], [-0.06688414000000001, -0.02691829500000001], [-0.06850133, -0.025068754999999998], [-0.07018823000000002, -0.022838155], [-0.0718937, -0.020175365], [-0.07354344000000002, -0.01702463500000001], [-0.07503513, -0.013367365000000006], [-0.07623873, -0.009231455], [-0.07702410000000001, -0.0047237749999999995]], 'holes': []}], 'simplify_tolerance': 3.0919312e-05, 'sketch_entity_count': 59}
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
