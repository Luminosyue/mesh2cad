#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.41291919, -0.16139067499999998, 0.016738425], 'basis': [[-0.0, 0.9988116398480261, -0.04873713270286912], [0.6856167605245388, 0.03547881354424509, 0.7270975941903053], [0.7279626760266197, -0.03341499504099569, -0.684802000886806]], 'axis': [-0.04873713270286912, 0.7270975941903053, -0.684802000886806], 'zmin': -0.05169425289884774, 'zmax': 0.05169427428881961, 'profiles': [{'outer': [[-0.014393072029665136, -0.004322556109255128], [-0.014397342761955432, 0.004280522255884837], [-0.014233867965533284, 0.004416729370048224], [-0.013503758186477503, 0.004550319779180187], [-0.012202801014756168, 0.004674417171607648], [-0.010504184605638947, 0.004783606674823449], [-0.008369538275166288, 0.004872778153769116], [-0.005905718965506529, 0.004943497764818189], [-0.0032132847253646683, 0.004987014754594013], [-0.00043334506334650336, 0.0050031213800692895], [0.002361342268374817, 0.004995154025307934], [0.00510239639485956, 0.004959569899818528], [0.007682895704216845, 0.004897936789447997], [0.009889010604179007, 0.004813379597668945], [0.011752920466628151, 0.004711114220473691], [0.013169722448347125, 0.004589262919874512], [0.014062614322826706, 0.004458041395018968], [0.01439308531854118, 0.004322557507769429], [0.014397363753917375, -0.004280521880458572], [0.014233867118614945, -0.00441672799217211], [0.01350377875498029, -0.004550318714815838], [0.012239140911543399, -0.004676085248160151], [0.010504211606850193, -0.004783604566732878], [0.008405891884288738, -0.004874445520745348], [0.00590571896550651, -0.004943497764818245], [0.0032132633099435067, -0.004987014441082305], [0.00043337291147606776, -0.005003120649854889], [-0.0023613362591255534, -0.004995152292643683], [-0.0051023685467300175, -0.00495956916960413], [-0.00768288241534082, -0.004897935390933697], [-0.009889017460346629, -0.004813379952457137], [-0.011752892618498609, -0.004711113490259292], [-0.013169701879844339, -0.004589261855510163], [-0.014062586474697157, -0.00445804066480457]], 'holes': []}], 'simplify_tolerance': 5.758941303174561e-06, 'sketch_entity_count': 34}
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
