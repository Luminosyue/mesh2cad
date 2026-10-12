#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.21196648, -0.163685425, 0.08160827999999999], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.045952009999999995, 'zmax': 0.04595201, 'profiles': [{'outer': [[-0.051191165, -0.009878129999999985], [-0.051191165, 0.011240660000000013], [-0.04304857499999999, 0.03076986000000001], [-0.02799616499999999, 0.045692500000000025], [-0.008304754999999997, 0.05377019000000002], [0.012976215000000013, 0.05377019000000002], [0.032667625000000006, 0.045692500000000025], [0.05119116500000001, 0.023568060000000002], [0.027347375000000007, 0.023730240000000014], [0.021540505000000015, 0.029050490000000012], [0.009083344999999993, 0.03427343000000002], [-0.0044119149999999885, 0.03427343000000002], [-0.016836624999999994, 0.029180280000000003], [-0.026374144999999988, 0.01970765000000002], [-0.03153218499999999, 0.007380230000000015], [-0.03153218499999999, -0.005985279999999982], [-0.026374144999999988, -0.018345109999999998], [-0.016836624999999994, -0.028174599999999994], [-0.0044119149999999885, -0.034078779999999975], [0.009245565000000011, -0.03420853999999998], [0.013497755816377553, -0.03183019297167622], [0.014987544999999991, -0.030932039999999994], [0.03827984500000001, -0.03628472999999999], [0.012976215000000013, -0.053770189999999995], [-0.008304754999999997, -0.05357551999999999], [-0.02799616499999999, -0.04468683000000001], [-0.04304857499999999, -0.02937489999999998]], 'holes': []}], 'simplify_tolerance': 2.1508076000000006e-05, 'sketch_entity_count': 27}
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
