#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-5.650000000009814e-07, -0.009516154999999998, -0.00872597], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.07009167499999999, 'zmax': 0.07009167499999999, 'profiles': [{'outer': [[0.10780208091898652, 0.06358286032930464], [0.10879603, 0.06784501500000001], [0.11040303, 0.071721935], [0.11259458, 0.075301625], [0.11532179000000001, 0.078495905], [0.11851614999999999, 0.081223135], [0.12209582, 0.083414715], [0.12597269, 0.085021655], [0.1300554, 0.086001495], [0.13423929, 0.086331385], [0.13842651, 0.086001495], [0.14250916, 0.085021655], [0.14638609, 0.08341470499999999], [0.14996576, 0.081223125], [0.15316004, 0.078495895], [0.15588406, 0.075301615], [0.15807888, 0.071721915], [0.15968579, 0.067845005], [0.16067974324853812, 0.06358284639950773], [0.19787746506853532, 0.06358283551274314], [0.19884008, 0.065021315], [0.20407963, 0.06549126499999999], [0.21344927, 0.065288925], [0.21656701, 0.064249315], [0.21694168740857003, 0.06358282984028961], [0.2302964, 0.06358282586666901], [0.2302964, 0.064878785], [0.26402791999999997, 0.06508212499999999], [0.26401593999999995, 0.06358281583360707], [0.26491419000000005, 0.06358281556633777], [0.26491419000000005, 0.06386434499999999], [0.26845238000000005, 0.06386434499999999], [0.26845238000000005, 0.06358281451356897], [0.30870685, 0.06358280253607487], [0.30870685, 0.065252405], [0.31005713, 0.065252405], [0.31005713, 0.06358280213430656], [0.3259963740493861, 0.06358279739167297], [0.32706514, 0.064187245], [0.328133934187778, 0.06358279675565383], [0.35535655, 0.0635827863233194], [0.35538086, 0.064060305], [0.35577008, 0.064340075], [0.35957244, 0.064343325], [0.35957751000000004, 0.06358278460567184], [0.3959848, 0.063573725], [0.3959848, 0.06039695663890684], [0.40462001999999997, 0.058248095], [0.40462001999999997, -0.08450376500000001], [0.38318255999999995, -0.086331385], [0.16599223, -0.086331315], [0.09007201, -0.048198265000000004], [0.05025956475412243, -0.029279927259094944], [-0.08187237, -0.029279885], [-0.40462001999999997, -0.018956215000000002], [-0.40461999000000004, 0.037996345], [-0.08187234, 0.053753295], [-0.07969896, 0.053753295], [0.04933085854762908, 0.04227739363021855], [0.09007207, 0.06358286499999999]], 'holes': []}], 'simplify_tolerance': 0.000161848008, 'sketch_entity_count': 66}
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
