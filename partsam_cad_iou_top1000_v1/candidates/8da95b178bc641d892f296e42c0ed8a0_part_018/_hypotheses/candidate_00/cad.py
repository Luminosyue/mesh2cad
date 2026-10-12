#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.333882275, -0.37038697, -0.32811362], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.10051929999999998, 'zmax': 0.1005193, 'profiles': [{'outer': [[-0.12961284999999997, -0.025770844999999987], [-0.12961284999999997, 0.025770785000000018], [-0.10988572999999996, 0.07344031500000003], [-0.07341416, 0.10985958500000001], [-0.025796989999999964, 0.129586695], [0.025797000000000014, 0.129586695], [0.07341414000000002, 0.10985958500000001], [0.10988574000000001, 0.07344031500000003], [0.12961285, 0.025770785000000018], [0.12961285, -0.025770844999999987], [0.10988574000000001, -0.073387975], [0.07341414000000002, -0.109859645], [0.025797000000000014, -0.12958669499999997], [-0.025796989999999964, -0.12958669499999997], [-0.07341416, -0.109859645], [-0.10988572999999996, -0.073387975]], 'holes': [[[-0.04505311000000001, 0.067422755], [-0.06739652999999995, 0.045027025], [-0.07953632999999999, 0.015828734999999983], [-0.07953632999999999, -0.015828785000000012], [-0.06739652999999995, -0.045027015000000004], [-0.04505311000000001, -0.06742280499999997], [-0.01580256999999996, -0.079510205], [0.015802609999999995, -0.079510205], [0.04505311000000001, -0.06742280499999997], [0.06744890000000003, -0.045027015000000004], [0.07953631, -0.015828785000000012], [0.07953631, 0.015828734999999983], [0.06744890000000003, 0.045027025], [0.04505311000000001, 0.067422755], [0.015802609999999995, 0.079510215], [-0.01580256999999996, 0.079510215]]]}], 'simplify_tolerance': 5.1845140000000006e-05, 'sketch_entity_count': 68}
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
