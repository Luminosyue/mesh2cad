#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.34926744, -0.200518395, -0.16948142500000002], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.01934503000000004, 'zmax': 0.019345029999999985, 'profiles': [{'outer': [[-0.131877965, 0.091635315], [-0.144472865, 0.10962271499999998], [-0.038889405000000016, 0.183552955], [-0.02629449500000003, 0.16556555499999998], [-0.026554614134833118, 0.16538341560580308], [-0.016243335000000025, 0.150657355], [-0.014645725000000026, 0.11605397499999999], [0.11241695499999999, -0.115192035], [0.12936523499999997, -0.12708971500000002], [0.143864695, -0.156654745], [0.144472865, -0.170213555], [0.14437887499999996, -0.170547755], [0.138253185, -0.18091986499999999], [0.125635145, -0.183552955], [0.12528896499999997, -0.18352702500000004], [0.11284592499999996, -0.178404125], [0.08998900499999996, -0.154661215], [0.08460551499999996, -0.134665795], [-0.08921640500000001, 0.06383908499999999], [-0.12118651500000002, 0.07717544499999998], [-0.13149780500000002, 0.09190149499999999]], 'holes': [[[-0.10124535500000002, 0.11308446499999998], [-0.10008253500000001, 0.11142378499999998], [-0.08828633500000002, 0.10999269499999999], [-0.07026601500000001, 0.11611030499999998], [-0.05835401500000002, 0.13095149499999997], [-0.055664255000000024, 0.14252575499999998], [-0.05682708011126126, 0.14418644142106032]]]}], 'simplify_tolerance': 7.3421182e-05, 'sketch_entity_count': 37}
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
