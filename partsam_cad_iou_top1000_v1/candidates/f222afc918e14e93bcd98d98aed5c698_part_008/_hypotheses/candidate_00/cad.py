#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.03846147499999997, 0.038454485000000004, -6.974999999992404e-06], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.038454645, 'zmax': 0.038454645, 'profiles': [{'outer': [[-0.461545415, -0.499999985], [-0.461545415, 0.499999985], [0.461545415, 0.499999985], [0.461545415, -0.499999985]], 'holes': [[[-0.153848485, 0.19230298500000004], [-0.153848485, 0.11539400500000002], [-0.230757455, 0.11539400500000002], [-0.230757455, 0.038485025000000034], [-0.30766642499999997, 0.038485025000000034], [-0.30766642499999997, -0.038485024999999964], [-0.07693951500000001, -0.038485024999999964], [-0.07693951500000001, -0.11539400499999997], [-0.230757455, -0.11539400499999997], [-0.230757455, -0.19230298499999995], [-0.30766642499999997, -0.19230298499999995], [-0.30766642499999997, -0.2692119949999999], [-0.38463646500000004, -0.2692119949999999], [-0.38463646500000004, -0.34618202499999995], [-0.07693954500000001, -0.34618202499999995], [-0.07693951500000001, -0.19230298499999995], [3.052499999999241e-05, -0.19230298499999995], [3.052499999999241e-05, -0.2692119949999999], [0.076939495, -0.2692119949999999], [0.076939495, -0.19230298499999995], [0.153848465, -0.19230298499999995], [0.153848465, -0.038485024999999964], [0.307727455, -0.038485024999999964], [0.307727455, 0.11539400500000002], [0.230757465, 0.11539400500000002], [0.230757465, 0.19230298500000004], [0.153848465, 0.19230298500000004], [0.153848465, 0.26921196500000005], [3.052499999999241e-05, 0.26921196500000005], [3.052499999999241e-05, 0.19230298500000004]], [[0.307727455, 0.19230298500000004], [0.307727455, 0.26921196500000005], [0.230757465, 0.26921196500000005], [0.230757465, 0.19230298500000004]], [[-0.153848485, 0.26921196500000005], [-0.07693954500000001, 0.26921196500000005], [-0.07693954500000001, 0.34618202500000006], [-0.153848485, 0.34618202500000006]], [[-0.230757455, 0.26921196500000005], [-0.30766642499999997, 0.26921196500000005], [-0.30766642499999997, 0.19230298500000004], [-0.230757455, 0.19230298500000004]], [[0.230757465, -0.11539400499999997], [0.230757465, -0.2692119949999999], [0.307727455, -0.2692119949999999], [0.307727455, -0.11539400499999997]]]}, {'outer': [[-0.153848485, 0.11539400500000002], [-0.07693951500000001, 0.11539400500000002], [-0.07693951500000001, 0.038485025000000034], [-0.153848485, 0.038485025000000034]], 'holes': []}, {'outer': [[0.076939495, 0.11539400500000002], [3.052499999999241e-05, 0.11539400500000002], [3.052499999999241e-05, 0.19230298500000004], [0.153848465, 0.19230298500000004], [0.153848465, 0.038485025000000034], [0.076939495, 0.038485025000000034]], 'holes': []}], 'simplify_tolerance': 0.000199999994, 'sketch_entity_count': 60}
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
