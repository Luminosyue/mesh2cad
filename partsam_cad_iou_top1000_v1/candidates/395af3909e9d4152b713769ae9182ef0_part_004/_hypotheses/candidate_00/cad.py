#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.18470715, -0.067604345, -0.05565933], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.13148133499999998, 'zmax': 0.13148133499999998, 'profiles': [{'outer': [[-0.06951731, 0.0077087400000000195], [-0.06673351999999999, 0.020929220000000026], [-0.06144003, 0.03339978000000002], [-0.053765959999999995, 0.04464577], [-0.044015439999999996, 0.05423675], [-0.03251763, 0.061790500000000026], [-0.019695780000000003, 0.06693919000000004], [-0.014536570000000006, 0.06816823999999999], [-0.006944341266901944, 0.06923562917566466], [-0.006064899999999998, 0.06939401], [-0.002187750000000002, 0.06987639000000001], [0.010420310000000002, 0.06916444], [0.02279854, 0.06606744000000003], [0.03451179, 0.060760390000000025], [0.045132820000000004, 0.05350471000000001], [0.05423433, 0.04456180000000001], [0.06147464, 0.034292530000000015], [0.06659427, 0.023106740000000014], [0.06934049, 0.011514980000000008], [0.06968901, 0.004158230000000013], [0.06930473, -0.009677309999999995], [0.06612764, -0.023091659999999986], [0.06035272, -0.03553373999999998], [0.05229067, -0.046565439999999986], [0.04228043, -0.05583958], [0.03066222, -0.06293015999999998], [0.01776266, -0.06761247999999999], [0.004389369999999997, -0.06987638999999998], [-0.00917051, -0.06954305999999999], [-0.022373990000000003, -0.06650762999999998], [-0.034734530000000007, -0.06096270999999999], [-0.045790870000000004, -0.05314571999999998], [-0.05509497, -0.04330940999999999], [-0.06238303, -0.03192054999999999], [-0.06727943, -0.019315969999999988], [-0.06968901, -0.006003629999999982]], 'holes': []}], 'simplify_tolerance': 2.7950556e-05, 'sketch_entity_count': 48}
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
