#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.175373055, -0.38736844000000004, -0.17692912], 'basis': [[-0.0, 0.9746547521598031, -0.22371435826140618], [0.13364990752526312, 0.22170732909624988, 0.9659107424827078], [0.9910286081735928, -0.02989940329371052, -0.13026251749521595]], 'axis': [-0.22371435826140618, 0.9659107424827078, -0.13026251749521595], 'zmin': -0.04905039576026174, 'zmax': 0.048983736384534196, 'profiles': [{'outer': [[-0.04867021626005364, -0.001274071811331724], [-0.04807539194973008, 0.011160531424869764], [-0.04573848976638242, 0.02561058482854971], [-0.040043579624902154, 0.0429245479992147], [-0.031061254166880527, 0.059387681341503996], [-0.021289713404506052, 0.07209324252822724], [-0.012566406454906061, 0.08034449481662198], [-0.005896319752709842, 0.08487045403764315], [-0.0021649674711040562, 0.0863617899107726], [0.0016368179295211183, 0.0850450557909675], [0.008539114559937626, 0.08084920597525999], [0.017658720394388167, 0.0730264166971544], [0.028035646579550693, 0.060811891820182665], [0.03780977400505103, 0.044797621980034265], [0.04432440571369978, 0.02777836896852402], [0.04736057541462872, 0.013470658697039084], [0.04855337494660529, 0.0010802644315229882], [0.0479585327070012, -0.01135434206157669], [0.04562162061336744, -0.025804404912810122], [0.039935540136004796, -0.04312096184989202], [0.030943013765814358, -0.05958377614296094], [0.021171466320944483, -0.07227931921765092], [0.012458355719223518, -0.08054090083883103], [0.0057794524909864885, -0.08506429746988486], [0.002058278627979227, -0.08655594648184568], [-0.0017550663495817626, -0.08524114440176915], [-0.008647185116192321, -0.08104561139948097], [-0.017765399882019504, -0.07322055774871446], [-0.02814233786875975, -0.061006018971314885], [-0.037928004495831155, -0.04499369758739019], [-0.04444264422347435, -0.027974467624867216], [-0.047477446458935334, -0.013664465179865722]], 'holes': []}], 'simplify_tolerance': 3.458354727852366e-05, 'sketch_entity_count': 32}
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
