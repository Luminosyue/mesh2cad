#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.1287659, -0.07227533, -0.219439035], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.13148133, 'zmax': 0.13148133, 'profiles': [{'outer': [[-0.06980677499999999, 0.00030735999999997876], [-0.06852429500000001, 0.014088679999999992], [-0.06448226499999998, 0.027268239999999985], [-0.057911064999999984, 0.03930877999999999], [-0.049149204999999974, 0.04979330999999999], [-0.038557495, 0.05839739999999999], [-0.026503114999999994, 0.06471803999999999], [-0.013326564999999985, 0.06855225999999999], [0.00016557500000000114, 0.06994239999999999], [0.013675145, 0.06872866999999999], [0.02665347500000001, 0.06484170999999998], [0.03862758499999999, 0.058505319999999986], [0.049152635, 0.049986429999999984], [0.057797915000000005, 0.03956632999999998], [0.064330525, 0.02772796999999999], [0.068397545, 0.014831849999999994], [0.06993701499999999, 0.0013910699999999943], [0.06887464500000001, -0.012281160000000013], [0.065237675, -0.02529281], [0.059145065, -0.037393040000000016], [0.050756455000000006, -0.04811662], [0.04040332500000002, -0.05705376000000001], [0.028438975000000005, -0.06384442000000001], [0.015309665, -0.06814906000000001], [0.010081505000000018, -0.06904025], [0.002435435832303143, -0.06961211925594019], [0.0015480850000000046, -0.06971296000000002], [-0.002352214999999991, -0.06994240000000002], [-0.014887375000000008, -0.06841270000000002], [-0.027038194999999987, -0.06451793], [-0.038381865000000015, -0.058460960000000006], [-0.048508965000000015, -0.05053047000000002], [-0.05701013500000002, -0.041015070000000015], [-0.063567875, -0.030297020000000008], [-0.06794982500000002, -0.018802190000000024], [-0.06993701499999999, -0.007056489999999999]], 'holes': []}], 'simplify_tolerance': 2.797696e-05, 'sketch_entity_count': 36}
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
