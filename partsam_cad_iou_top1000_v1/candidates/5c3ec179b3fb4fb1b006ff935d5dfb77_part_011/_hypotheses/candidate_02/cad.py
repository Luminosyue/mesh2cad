#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-6.577305315, 102.95923232999999, 12.568751335], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -11.803231714999999, 'zmax': 11.803231714999999, 'profiles': [{'outer': [[-1.5995454749999993, 1.413829800000002], [-1.6049041749999997, 1.694461820000015], [-1.5981340450000001, 1.9242973300000017], [-1.5882549249999993, 2.1048469500000095], [-1.4722194650000002, 2.753231050000011], [-1.443303105, 2.8772621200000117], [-1.1156234749999996, 3.413326260000005], [-0.6054105750000005, 3.7578315700000076], [-0.5771913550000001, 3.773242950000011], [0.0026779149999995866, 3.8833503700000023], [0.5825471849999992, 3.773242950000011], [0.6107664150000005, 3.7578315700000076], [1.1209793050000005, 3.413326260000005], [1.448658945, 2.8772621200000117], [1.4775753050000002, 2.753231050000011], [1.5936117149999998, 2.1048469500000095], [1.6034917849999992, 1.9242973300000017], [1.6049032249999993, 1.6944541900000019], [1.6034927349999997, -0.3186225899999897], [1.5936126749999993, -0.9443550099999953], [1.5620155350000005, -1.6347389199999895], [1.4763307549999993, -2.320377349999987], [1.2992639550000007, -2.9234504699999917], [1.216141705, -3.160724639999998], [0.9428491549999993, -3.555072779999989], [0.5200662650000005, -3.7996787999999952], [0.002679824999999525, -3.883350369999988], [-0.5147056550000002, -3.7996787999999952], [-0.9374885549999998, -3.555072779999989], [-1.2107810949999998, -3.160724639999998], [-1.2939043049999999, -2.9234504699999917], [-1.4709711050000003, -2.320377349999987], [-1.5566558849999996, -1.6347389199999895], [-1.5882530250000002, -0.9443550099999953], [-1.5981330850000006, -0.3186225899999897]], 'holes': []}], 'simplify_tolerance': 0.0015533401479999982, 'sketch_entity_count': 38}
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
