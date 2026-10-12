#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.07420436, 0.034575550000000004, 0.25016395], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.05396708000000003, 'zmax': 0.05396708, 'profiles': [{'outer': [[-0.10282735999999998, 0.006093189999999998], [-0.09812348999999998, 0.015368729999999997], [-0.09133375999999999, 0.02415622], [-0.08263567999999999, 0.03232246], [-0.07225113, 0.03960117], [-0.060357619999999994, 0.04585921999999999], [-0.04735456999999999, 0.05100783], [-0.03346387, 0.05486945], [-0.01908493, 0.057399689999999996], [-0.004484039999999995, 0.05855418], [0.009895010000000003, 0.05819977], [0.023785960000000002, 0.05646954999999999], [0.03683373, 0.05331912999999999], [0.048727700000000006, 0.04888167], [0.05920156, 0.0431571], [0.06790028000000001, 0.036322999999999994], [0.07059151846764866, 0.03326374506975693], [0.07948334000000001, 0.03769927], [0.08742712, 0.042448229999999997], [0.09488268, 0.04795164], [0.10045244508394921, 0.05290297614954007], [0.10118428000000002, 0.05567398], [0.10278200000000001, 0.054564549999999996], [0.10451301000000002, 0.049860379999999996], [0.1053122, 0.04138388], [0.10451355000000001, 0.036990239999999994], [0.10338649337836311, 0.037415491045503825], [0.10300465, 0.03690143], [0.09652549, 0.029889149999999996], [0.08911431, 0.024296979999999996], [0.07974495318946494, 0.018862265246204102], [0.08183662, 0.010538969999999995], [0.08157072000000001, 0.0014854799999999974], [0.08059456000000001, -0.0030856699999999987], [0.0789527, -0.007568100000000008], [0.07682267000000001, -0.012139300000000006], [0.07407129000000001, -0.016399869999999997], [0.06710404, -0.0248323], [0.0648976681755477, -0.02676303786055874], [0.058373430000000004, -0.03286203], [0.048211620000000004, -0.039945140000000004], [0.0366073, -0.04610449], [0.023819800000000002, -0.05114556000000001], [0.010173240000000004, -0.05497110999999999], [-0.00400822, -0.057451450000000015], [-0.018351819999999998, -0.05855418000000001], [-0.0325172, -0.05824683], [-0.04845952, -0.05621369000000001], [-0.06137415999999999, -0.05332954000000001], [-0.07313497, -0.04915835], [-0.08343128999999999, -0.043788820000000006], [-0.09199686999999998, -0.03735414000000001], [-0.09860975999999999, -0.029987380000000008], [-0.10309246, -0.021777320000000003], [-0.10522305999999998, -0.01307897000000001], [-0.1053122, -0.003936750000000003]], 'holes': []}], 'simplify_tolerance': 4.212488e-05, 'sketch_entity_count': 56}
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
