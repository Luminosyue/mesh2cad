#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.16500814, -0.067604345, -0.20293985000000003], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.13148133499999998, 'zmax': 0.13148133499999998, 'profiles': [{'outer': [[-0.06951544999999998, 0.005444339999999992], [-0.06835662621120636, 0.013023213768003387], [-0.06825567999999999, 0.013911010000000001], [-0.06760383999999997, 0.017763290000000015], [-0.06329966999999997, 0.029635280000000014], [-0.056777019999999956, 0.04060190999999999], [-0.04832850999999999, 0.05029665], [-0.03832731999999997, 0.05838539000000001], [-0.027146629999999977, 0.06453394000000001], [-0.01523016999999996, 0.06851869], [-0.0030450999999999673, 0.07020884], [0.00884695000000002, 0.06950902], [0.015993680000000038, 0.06772928], [0.029135520000000026, 0.06338631], [0.04107159000000002, 0.05648928], [0.05133001000000004, 0.04738323999999999], [0.05958046000000003, 0.03649171000000001], [0.06558771000000002, 0.024239050000000012], [0.06904149000000004, 0.01107356000000001], [0.06982042000000002, -0.0026273900000000072], [0.06814678000000005, -0.016087290000000004], [0.06393180000000004, -0.02897975], [0.05723104000000004, -0.04075452], [0.048368730000000026, -0.05100093], [0.03770487000000003, -0.05934538], [0.025610210000000022, -0.06543129], [0.012607650000000026, -0.06914013], [-0.0008722699999999806, -0.07020884], [-0.014315649999999958, -0.06869225999999999], [-0.02740059999999997, -0.06458828], [-0.039263949999999964, -0.058123659999999994], [-0.04968796999999997, -0.0494706], [-0.058255119999999994, -0.03888912], [-0.06464047999999994, -0.026794209999999985], [-0.06857247999999999, -0.01361097], [-0.06982042, 0.00014952000000001409]], 'holes': []}], 'simplify_tolerance': 2.8083535999999998e-05, 'sketch_entity_count': 54}
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
