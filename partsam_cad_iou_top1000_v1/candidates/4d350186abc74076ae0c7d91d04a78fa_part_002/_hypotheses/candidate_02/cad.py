#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.12738812, 0.285859885, -5.464999999996167e-06], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.134346635, 'zmax': 0.134346635, 'profiles': [{'outer': [[-0.24156137500000002, -0.372612], [-0.241561405, 0.0018006899999999937], [-0.24101205488171948, 0.0018006899999999937], [-0.24101199499999998, 0.37261206], [-0.200787365, 0.36260167], [-0.16062377500000002, 0.37261200000000005], [-0.12039915500000001, 0.36260164], [-0.080174535, 0.37261200000000005], [-0.039949925000000004, 0.36260164], [0.0002747049999999962, 0.37261200000000005], [0.040499345, 0.36260164], [0.080723965, 0.37261200000000005], [0.12088753499999999, 0.36260164], [0.16111215499999998, 0.37261200000000005], [0.20133678500000002, 0.36260164], [0.241561405, 0.37261200000000005], [0.24156134499999998, -0.0018006299999999975], [0.241073025, -0.0018006299999999975], [0.24101200499999997, -0.37261206], [0.200848395, -0.3626627], [0.16062377499999997, -0.37261203], [0.120399155, -0.3626627], [0.08017453499999999, -0.37261203], [0.039949914999999996, -0.3626627], [-0.00027469500000000383, -0.37261203], [-0.040499315, -0.3626627], [-0.08066290500000001, -0.37261203], [-0.12088752500000001, -0.3626627], [-0.16111214499999998, -0.37261203], [-0.20133677500000002, -0.36266266999999996]], 'holes': []}], 'simplify_tolerance': 0.00014904482400000002, 'sketch_entity_count': 30}
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
