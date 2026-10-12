#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.00035132499999999955, -0.195476525, -0.159686355], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.025292275000000003, 'zmax': 0.025292275000000003, 'profiles': [{'outer': [[-0.03205042500000002, -0.13224762499999998], [-0.029202515000000012, -0.124427135], [-0.02988059500000001, -0.103542355], [-0.03295453500000001, -0.035418225], [-0.035169595000000026, -2.2604999999999544e-05], [-0.03295453500000001, 0.035327815], [-0.02988059500000001, 0.103497165], [-0.029202515000000012, 0.124291525], [-0.03205042500000002, 0.13220240500000002], [-0.043532525000000016, 0.14345847499999997], [-0.04240239500000001, 0.159506325], [-0.035169595000000026, 0.167869235], [-0.03205042500000002, 0.175915775], [0.02906689499999998, 0.175915775], [0.032140845, 0.167869235], [0.03928325499999999, 0.159506325], [0.04353252499999999, 0.160093995], [0.043306504999999995, 0.141062615], [0.016319055, 0.128314765], [0.013832764999999997, 0.125692855], [0.019212194999999987, 0.123749065], [0.017810824999999975, 0.108695735], [0.014962884999999981, 0.106299875], [0.008091724999999994, 0.103497165], [0.010939634999999975, 0.035327815], [0.01301909499999998, -2.2604999999999544e-05], [0.010939634999999975, -0.035418225], [0.008091724999999994, -0.103542355], [0.014962884999999981, -0.106390285], [0.017810824999999975, -0.108786155], [0.019212194999999987, -0.123749055], [0.013832764999999997, -0.125828485], [0.016319055, -0.128314775], [0.043306504999999995, -0.141198235], [0.04353252499999999, -0.160093975], [0.03928325499999999, -0.15950630500000001], [0.032140845, -0.168004875], [0.02906689499999998, -0.175915775], [-0.03205042500000002, -0.175915775], [-0.035169595000000026, -0.168004875], [-0.04240239500000001, -0.15950630500000001], [-0.043532525000000016, -0.14359410499999997]], 'holes': []}], 'simplify_tolerance': 7.036631e-05, 'sketch_entity_count': 45}
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
