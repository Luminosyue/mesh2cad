#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.012836725, -0.23453790000000002, -0.0012984099999999998], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.07573934500000001, 'zmax': 0.07573934500000001, 'profiles': [{'outer': [[-0.06407935, -0.014043329999999965], [-0.0658906, -0.01258697999999997], [-0.0658906, -0.008511659999999976], [-0.06445873, -0.007104249999999979], [-0.0685218, 0.03162971000000003], [-0.06081172, 0.031911190000000034], [-0.01628907, 0.031911170000000016], [-0.01506523, 0.10015151000000003], [-0.01074514, 0.10024941000000001], [-3.0225951743833236e-06, 0.100194066956483], [0.01073294, 0.10024941000000001], [0.01506528, 0.10015151000000003], [0.01628907, 0.031911170000000016], [0.06081173, 0.03191114000000003], [0.0685218, 0.03162965000000001], [0.06444646, -0.007104309999999975], [0.0658661, -0.008511719999999973], [0.0658661, -0.012587009999999982], [0.06406708, -0.014043359999999977], [0.05609998, -0.08708106999999998], [0.05737276, -0.08824371999999997], [0.05737276, -0.09179278999999996], [0.05579401, -0.09290646999999996], [0.054741530000000004, -0.10002910999999998], [0.0485857, -0.10024940999999998], [0.03556423, -0.10024940999999998], [-0.04858578, -0.10024934999999996], [-0.05474161, -0.10002907999999999], [-0.05580634, -0.09290641], [-0.0573973, -0.09179275999999997], [-0.0573973, -0.08824366], [-0.05611229, -0.08708100999999996]], 'holes': []}], 'simplify_tolerance': 4.0099764e-05, 'sketch_entity_count': 32}
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
