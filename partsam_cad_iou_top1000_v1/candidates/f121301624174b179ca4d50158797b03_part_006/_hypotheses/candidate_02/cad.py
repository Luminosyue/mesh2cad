#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.032486225, 0.117906735, 0.259907365], 'basis': [[-0.4473284692233569, 0.22145231991594463, 0.86651953851378], [0.0, 0.9688605226628353, -0.24760712353544637], [-0.8943697449166582, -0.11076171553990985, -0.43339889449370755]], 'axis': [0.86651953851378, -0.24760712353544637, -0.43339889449370755], 'zmin': -0.05223608473036452, 'zmax': 0.042999019946195524, 'profiles': [{'outer': [[-0.024677732552278946, 0.03505918876812472], [-0.02057435741986176, 0.04113353622593214], [-0.015270385121601364, -0.04550088424412433], [-0.020080947563384487, -0.039971296089411426], [-0.02434206222675517, -0.024286434659771372], [-0.02683626412500865, -0.0027071446767537154], [-0.026954772128537346, 0.01901436349891711]], 'holes': []}, {'outer': [[-0.01991103110027341, 0.033618484960817555], [-0.020415092424109264, 0.042234098131312854], [-0.01908963958142039, 0.04229568460349139], [-0.019190131939151582, 0.04389221240898031], [-0.01921718025254788, 0.04541178519613463], [-0.011570303312943597, 0.04635866741990871], [-0.010983962859420373, 0.044877168240398516], [-0.010452217368450901, 0.03633424013099053], [-0.010975415794964917, 0.044865892487938965], [-0.00013720360421581504, 0.04316189437284561], [0.004582403712027593, 0.03915885856921747], [0.016773000192167667, 0.01972764170593022], [0.03750109704265164, 0.006095173238306722], [0.03793012002040403, -0.0004874213535674381], [0.039235229996713784, -0.022705199729655463], [0.03977901522056536, -0.03114438956736944], [0.020545734084116855, -0.04148982910738831], [0.009660226064238149, -0.04396074522552149], [0.005296564392040175, -0.04560208325979232], [-0.005324123867861839, -0.04713684705294736], [-0.0057556297904258445, -0.04870043567126619], [-0.013478993904747036, -0.048694372814204225], [-0.013681192286776856, -0.045640727875270674], [-0.015059452238799014, -0.04569504461340035], [-0.01527751757880915, -0.04177362229922142], [-0.01643255170134176, -0.02333596238400513]], 'holes': []}], 'simplify_tolerance': 1.9011820618234984e-05, 'sketch_entity_count': 37}
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
