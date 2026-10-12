#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.04759861, -0.37994416, 0.09259237000000001], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.02434186, 'zmax': 0.024341860000000007, 'profiles': [{'outer': [[-0.004687209999999997, -0.10541906000000001], [-0.0010352199999999895, -0.09541203000000004], [-0.001782869999999992, -0.08508866000000004], [-0.002156689999999989, -0.0674613], [-0.006930179999999994, -0.02323474000000003], [-0.011128529999999998, 0.06815142999999996], [-0.012250009999999992, 0.08258689999999996], [-0.012307519999999988, 0.08577879], [-0.010352119999999992, 0.10826588999999998], [-0.010697189999999995, 0.10863972999999999], [-0.010380879999999995, 0.10912857999999998], [-0.010754709999999987, 0.12005580999999999], [0.032896730000000006, 0.12005580999999999], [0.03252290000000001, 0.11085392], [0.03283922000000001, 0.11048007999999998], [0.032494150000000006, 0.11013502999999997], [0.03295424000000001, 0.09118489999999996], [0.032896730000000006, 0.0760593], [0.033270560000000005, 0.06815142999999996], [0.02907219000000001, -0.02323474000000003], [0.024327480000000012, -0.0674613], [0.023924890000000004, -0.08508866000000004], [0.02320599000000001, -0.09308280000000002], [0.02317724, -0.09541203000000004], [0.023637340000000007, -0.09880520000000004], [0.02662795000000001, -0.1048152], [0.026857990000000012, -0.10541906000000001], [0.02907219000000001, -0.11556991], [0.02907219000000001, -0.11925064000000002], [0.02800823000000001, -0.12005581000000004], [-0.03220659999999999, -0.12005581000000004], [-0.033270560000000005, -0.11925064000000002], [-0.033270560000000005, -0.11556991]], 'holes': []}], 'simplify_tolerance': 4.802232400000001e-05, 'sketch_entity_count': 33}
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
