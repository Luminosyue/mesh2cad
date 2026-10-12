#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.21283099, 0.06508805000000001, 0.19388581], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.02333078000000001, 'zmax': 0.023330779999999995, 'profiles': [{'outer': [[-0.01650317005649182, -0.017444792273787382], [-0.00908835999999999, -0.000216380000000016], [-0.006098279999999984, 0.006511359999999994], [-0.004406469999999996, 0.010170309999999988], [-0.0036983099999999824, 0.011429319999999993], [0.0002754100000000037, 0.013160439999999995], [0.001310962381810965, 0.01234662239394962], [0.0023999700000000013, 0.015009579999999995], [0.0047999400000000025, 0.027560200000000007], [-0.0007081699999999802, 0.04656318000000001], [-0.0006688199999999866, 0.04675989999999999], [-0.0001179899999999845, 0.04679923999999999], [0.0009442199999999956, 0.04668121], [0.004327830000000005, 0.04593369], [0.006531040000000016, 0.04538286999999999], [0.011567030000000006, 0.04392715], [0.016799740000000007, 0.04227473000000001], [0.019239000000000006, 0.0414485], [0.02140292000000002, 0.040661630000000004], [0.02325208000000001, 0.03995345], [0.02466848000000002, 0.039363289999999995], [0.025652040000000015, 0.038851830000000004], [0.026124160000000007, 0.03853707000000001], [0.02608480000000002, 0.038340369999999985], [0.02045871000000002, 0.02783561000000001], [0.016917740000000014, 0.023743879999999995], [0.011291629999999997, 0.012176859999999984], [0.009040018719530887, 0.003739793818798262], [0.010032650000000004, 0.0019081699999999868], [0.011685040000000008, -0.002931099999999992], [0.01085887000000002, -0.006275310000000006], [0.005114649999999998, -0.027835620000000005], [0.0035016000000000214, -0.033776520000000004], [0.0026360200000000167, -0.03680596], [0.0022425600000000045, -0.03802561999999998], [-0.0017310899999999907, -0.04184195000000002], [-0.011606389999999994, -0.04679924000000002], [-0.02482582, -0.04498943999999999], [-0.02612415999999998, -0.04058296], [-0.025730749999999997, -0.03932395999999999], [-0.02415700999999998, -0.03542893999999999]], 'holes': []}], 'simplify_tolerance': 1.8719696000000002e-05, 'sketch_entity_count': 47}
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
