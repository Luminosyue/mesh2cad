#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.001621850000000001, 0.22167293500000002, -0.356170205], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.113892675, 'zmax': 0.11389267500000003, 'profiles': [{'outer': [[-0.278326915, -0.028184360000000002], [-0.278326915, 0.0243449], [-0.13681049499999998, 0.0243449], [-0.13681049499999998, 0.028456179999999998], [-0.061244505000000005, 0.028456179999999998], [-0.061244505000000005, 0.03219371], [-0.0012401549999999928, 0.03544085875717613], [-0.0012401549999999928, 0.04904657], [0.023631365000000015, 0.04904657], [0.023631365000000015, 0.053769449999999996], [0.02872800500000003, 0.053769449999999996], [0.02872800500000003, 0.06450634], [0.06749634500000001, 0.06450634], [0.06749634500000001, 0.053769449999999996], [0.07252503500000002, 0.053769449999999996], [0.07252503500000002, 0.04904657], [0.09736261500000001, 0.04904657], [0.09736261500000001, 0.04077676960463342], [0.10388629500000002, 0.0411298], [0.11227874500000001, 0.0411298], [0.11227874500000001, 0.04575074], [0.11808889500000001, 0.04575074], [0.11808889500000001, 0.04765349], [0.23130202500000002, 0.057676859999999996], [0.23130202500000002, 0.04575074], [0.237112175, 0.04575074], [0.237112175, 0.04062014], [0.278326915, 0.015578699999999997], [0.278326915, -0.01941816], [0.237112175, -0.0444596], [0.237112175, -0.04955623], [0.231064175, -0.04955623], [0.231064175, -0.06151632], [0.11832673500000002, -0.05149295], [0.11832673500000002, -0.04955623], [0.11227874500000001, -0.04955623], [0.11227874500000001, -0.04493529], [0.10388629500000002, -0.04493529], [0.09736261500000001, -0.04458225960463342], [0.09736261500000001, -0.049522250000000004], [0.07252503500000002, -0.049522250000000004], [0.07252503500000002, -0.05424513], [0.06749634500000001, -0.05424513], [0.06749634500000001, -0.06450634], [0.02872800500000003, -0.06450634], [0.02872800500000003, -0.05424513], [0.023631365000000015, -0.05424513], [0.023631365000000015, -0.049522250000000004], [-0.0012401549999999928, -0.049522250000000004], [-0.0012401549999999928, -0.03924634875717613], [-0.061244505000000005, -0.0359992], [-0.061244505000000005, -0.03229564], [-0.13681049499999998, -0.03229564], [-0.13681049499999998, -0.028184360000000002]], 'holes': []}], 'simplify_tolerance': 0.00011133076600000001, 'sketch_entity_count': 54}
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
