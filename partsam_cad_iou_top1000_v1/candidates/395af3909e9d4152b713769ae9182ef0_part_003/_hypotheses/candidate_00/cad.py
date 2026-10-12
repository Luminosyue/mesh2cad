#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.15606303, -0.07285750999999999, -0.05582924], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.13148134, 'zmax': 0.13148134, 'profiles': [{'outer': [[-0.06698147, 0.020608669999999996], [-0.06193767, 0.03320000999999999], [-0.05448594999999999, 0.04451448999999999], [-0.044976569999999993, 0.05416338], [-0.03379301999999999, 0.06179726999999999], [-0.021328470000000002, 0.06708441999999999], [-0.008112380000000002, 0.06994052999999999], [0.005408490000000002, 0.07013108], [0.01872492, 0.06774417999999999], [0.03151554, 0.06279860999999999], [0.04293376, 0.05557678999999999], [0.052773480000000005, 0.046264669999999994], [0.06063496, 0.035148869999999985], [0.06622092, 0.02266459999999998], [0.06928798, 0.009253719999999993], [0.06963916, -0.004558790000000007], [0.06899076, -0.009822579999999997], [0.06734184560558677, -0.017310523442285126], [0.06718349, -0.01818951000000002], [0.06628272, -0.02199130000000002], [0.0612162, -0.03355854], [0.05399474, -0.04407815000000001], [0.044934140000000004, -0.05320344000000002], [0.0344285, -0.06062522000000001], [0.02287189, -0.06603425000000002], [0.0107217, -0.06923627000000002], [-0.0015474399999999972, -0.07013108000000001], [-0.013368900000000003, -0.06866001000000002], [-0.02038487, -0.06641965], [-0.03321675, -0.061231900000000006], [-0.04467942999999999, -0.05357384000000001], [-0.054324479999999994, -0.043820479999999995], [-0.061849760000000004, -0.03241584], [-0.06704816, -0.019798750000000004], [-0.06963916, -0.006436650000000016], [-0.06952617, 0.00728595999999998]], 'holes': []}], 'simplify_tolerance': 2.8052432000000007e-05, 'sketch_entity_count': 42}
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
