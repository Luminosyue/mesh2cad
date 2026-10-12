#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.271810445, -0.09506701, -0.019491790000000002], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.04714255, 'zmax': 0.047142550000000005, 'profiles': [{'outer': [[-0.03268138999999999, -0.01692613500000001], [-0.04422564999999999, -0.006080264999999974], [-0.045334889999999996, 0.010640475000000038], [-0.04435247369471553, 0.011084267830195184], [-0.04299316999999999, 0.012858935000000016], [-0.03251702999999999, 0.017624534999999997], [-0.028819579999999997, 0.019144594999999986], [-0.024842313002335085, 0.018912346554379896], [-0.021794449999999993, 0.020253834999999998], [-0.018014799999999997, 0.019966275000000033], [-0.012838379999999996, 0.01922679500000002], [-0.011267374674522402, 0.017561975907838288], [-0.008976589999999993, 0.016268795000000003], [-0.008487701707939999, 0.014483313553387531], [-0.0012940899999999977, 0.011667554999999996], [0.008501012033427303, 0.006630775934047327], [0.00827818000000001, 0.007559244999999992], [0.006224050000000009, 0.011174534999999985], [0.0058132300000000026, 0.015529304999999993], [0.005977560000000007, 0.017213705000000024], [0.006881370000000012, 0.020253834999999998], [0.008894430000000009, 0.02181498500000001], [0.012057800000000007, 0.022595555000000017], [0.01550876000000001, 0.021732835000000006], [0.01692881415624401, 0.021272634486752626], [0.017727240000000005, 0.022965315000000014], [0.021540761801318475, 0.023684254516383528], [0.02286263000000001, 0.027073595000000006], [0.027710330000000005, 0.02847039500000001], [0.03370844000000002, 0.02777201500000001], [0.03913139, 0.024896205000000005], [0.04311640000000001, 0.019596515000000037], [0.04533489, 0.011914015], [0.04525272000000001, 0.0029579750000000016], [0.04254125000000002, -0.006039165000000013], [0.037159399999999995, -0.014748714999999968], [0.028901770000000007, -0.02259555499999999], [0.02399733193298358, -0.023385260685512343], [0.02335559000000001, -0.02403345499999998], [0.007703020000000005, -0.02847039499999998], [0.00640063426223063, -0.028156223483620204], [-0.0031838899999999948, -0.028347165000000007], [-0.02483455999999999, -0.02128091500000001], [-0.028819579999999997, -0.01852836499999999]], 'holes': []}], 'simplify_tolerance': 1.8133956000000003e-05, 'sketch_entity_count': 50}
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
