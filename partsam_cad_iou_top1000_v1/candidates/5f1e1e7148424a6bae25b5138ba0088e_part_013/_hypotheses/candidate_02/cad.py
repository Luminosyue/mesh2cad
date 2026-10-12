#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.07678904, 0.12668487, -0.28055173], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.04595691000000002, 'zmax': 0.04595690999999999, 'profiles': [{'outer': [[-0.020581860000000007, 0.06057267999999999], [-0.015338379999999985, 0.06054156999999999], [-0.03253893999999999, -0.003310859999999999], [-0.032575386298712365, -0.015535681431196395], [-0.023081080000000004, -0.015518520000000001], [-0.022002980000000005, -0.016150710000000006], [-0.021877169572164065, -0.016496151497778725], [-0.009090338808301493, -0.01651008102256393], [-0.008428760000000007, -0.014750740000000005], [-0.006860619999999984, -0.013723150000000003], [0.001029100000000005, -0.013745324479953847], [0.001029100000000005, -0.011991639999999998], [0.01724959000000001, -0.011982699999999999], [0.01842568, -0.012019680000000005], [0.01842568, -0.013758475167919292], [0.02440423, -0.013748900000000008], [0.02646242, -0.014744860000000005], [0.02731183695999865, -0.016492547845348086], [0.03126313714768865, -0.016493591310819775], [0.03141187000000001, -0.01618125], [0.032734990000000005, -0.015517670000000004], [0.03876254, -0.01550812], [0.04013467000000001, -0.016192700000000004], [0.04047769000000001, -0.01684427], [0.04096774, -0.017899030000000003], [0.04096774, -0.02005312], [0.04067372000000001, -0.02074977], [0.04013467000000001, -0.021817970000000006], [0.03876254, -0.022481550000000003], [0.032734990000000005, -0.022475720000000005], [0.03141187000000001, -0.021806520000000003], [0.03126569954778513, -0.021498970223809186], [0.027314302721378976, -0.021497921989676122], [0.02646242, -0.02326794], [0.02440423, -0.024240050000000006], [0.01842568, -0.02424958819815898], [0.01842568, -0.026013090000000003], [0.001029100000000005, -0.025985060000000004], [0.001029100000000005, -0.024240558660250756], [-0.006860619999999984, -0.024245380000000004], [-0.008428760000000007, -0.023227320000000003], [-0.00908516346672736, -0.021475352498431678], [-0.021885105263060096, -0.02149809502993635], [-0.022002980000000005, -0.021822480000000005], [-0.023081080000000004, -0.022491940000000002], [-0.032596012123303174, -0.022453997732217477], [-0.03268594999999999, -0.05262097], [-0.03572423999999999, -0.060572680000000004], [-0.04096774, -0.06054132], [-0.04096774, -0.013989479999999999], [-0.021316929999999984, 0.06047766999999998]], 'holes': []}], 'simplify_tolerance': 2.4229071999999998e-05, 'sketch_entity_count': 51}
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
