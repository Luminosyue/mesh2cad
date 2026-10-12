#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.001621850000000001, 0.22167293500000002, -0.356170205], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.06450634, 'zmax': 0.06450634, 'profiles': [{'outer': [[-0.11389267500000003, -0.20357635500000001], [-0.11389267500000003, -0.11747729500000001], [-0.008120624999999992, -0.11747729500000001], [-0.008120624999999992, -0.11227874500000001], [-0.005198565000000044, -0.11227874500000001], [-0.005198565000000044, -0.10388629500000002], [-0.00484553381451072, -0.09736261500000001], [-0.020012765000000043, -0.09736261500000001], [-0.020012765000000043, 0.0012401549999999928], [0.0004903889753304548, 0.0012401549999999928], [0.0037375450000000088, 0.061244505000000005], [0.007475084999999992, 0.061244505000000005], [0.007475084999999992, 0.13681049499999998], [0.011586344999999998, 0.13681049499999998], [0.011586344999999998, 0.278326915], [0.06411561499999996, 0.278326915], [0.06411561499999996, 0.13681049499999998], [0.068226905, 0.13681049499999998], [0.068226905, 0.061244505000000005], [0.07026553499999999, 0.061244505000000005], [0.091637405, 0.07806338499999999], [0.095544815, 0.11611818499999998], [0.10006383499999999, 0.11611818499999998], [0.10397124499999999, 0.07806338499999999], [0.113892675, -0.10388629500000002], [0.113892675, -0.131476045], [0.10312178499999997, -0.131476045], [0.10312178499999997, -0.237112175], [0.07930356499999996, -0.237112175], [0.072949765, -0.278326915], [0.0031938850000000074, -0.278326915], [-0.0031599050000000184, -0.237112175], [-0.008120624999999992, -0.237112175], [-0.008120624999999992, -0.20357635500000001]], 'holes': []}], 'simplify_tolerance': 0.00011133076600000001, 'sketch_entity_count': 34}
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
