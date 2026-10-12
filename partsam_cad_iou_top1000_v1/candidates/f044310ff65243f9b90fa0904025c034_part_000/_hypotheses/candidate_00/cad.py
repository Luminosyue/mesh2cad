#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.012836725, -0.23453790000000002, -0.0012984099999999998], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.10024940999999998, 'zmax': 0.10024941000000001, 'profiles': [{'outer': [[-0.05016448, 0.049784765], [-0.04027239495018669, 0.054861098290213114], [-0.01821047, 0.067603625], [-0.01439215, 0.068142095], [-0.00424305, 0.068142095], [-0.00424305, 0.068203785], [-0.00832057, 0.06839793499999999], [-0.00832057, 0.073326115], [-0.00587036, 0.07573934500000001], [0.0058721699999999995, 0.07573934500000001], [0.008322389999999999, 0.073326115], [0.008322389999999999, 0.06839793499999999], [0.00424486, 0.068203785], [0.00424486, 0.068142095], [0.01439215, 0.068142095], [0.01822271, 0.067603625], [0.04038227691301674, 0.054804706301583746], [0.05016447, 0.049784765], [0.0685218, 0.017977615000000002], [0.0685218, -0.018737055000000002], [0.05016447, -0.050544205], [0.04051651442322891, -0.055495259456298254], [0.01822271, -0.068363055], [0.01439215, -0.06890153499999999], [0.008322389999999999, -0.06890153499999999], [0.008322389999999999, -0.07332612499999999], [0.0058721699999999995, -0.07573934500000001], [-0.00587036, -0.07573934500000001], [-0.00832057, -0.07332612499999999], [-0.00832057, -0.06890153499999999], [-0.01439215, -0.06890153499999999], [-0.01821047, -0.068363055], [-0.04040603964083281, -0.055551955682120804], [-0.05016448, -0.050544205], [-0.0685218, -0.018737055000000002], [-0.0685218, 0.017977615000000002]], 'holes': []}], 'simplify_tolerance': 3.0295738000000006e-05, 'sketch_entity_count': 45}
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
