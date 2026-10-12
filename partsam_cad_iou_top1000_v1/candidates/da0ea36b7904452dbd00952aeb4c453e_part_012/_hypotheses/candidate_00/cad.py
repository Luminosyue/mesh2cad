#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.29880582, -0.276871835, 0.20236552], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.004128379999999987, 'zmax': 0.004128379999999987, 'profiles': [{'outer': [[-0.07482385, -0.033807955], [-0.07593965, -0.02198072499999998], [-0.07120874000000002, -0.018499514999999966], [-0.06768466601125547, -0.018795429563730346], [-0.06491577000000001, -0.018588804999999986], [-0.05989330674543172, -0.0212932049615235], [-0.060988249999999994, -0.017606905000000006], [-0.06737046999999999, -0.014705894999999969], [-0.07665372000000001, -0.014393474999999989], [-0.07741245, -0.006315254999999964], [-0.07138725999999998, 0.018544205000000036], [-0.04487645000000001, 0.020135382338752887], [-0.04487645000000001, 0.063755385], [-0.04001167, 0.063755385], [-0.04001168771543811, 0.020427365099959148], [-0.027515010000000006, 0.021177415000000033], [0.021400559999999985, 0.021177384999999993], [0.03514691143420384, 0.021855291971036986], [0.03514692, 0.06375535500000001], [0.040011710000000006, 0.06375535500000001], [0.040011684449747724, 0.022095200251829518], [0.07027148999999999, 0.023587475000000024], [0.07741245, -0.006315314999999988], [0.06978052999999998, -0.033807984999999985], [0.07366344999999999, -0.059649344999999965], [0.025506589999999996, -0.063755385], [-0.02751502, -0.06299662499999997], [-0.06955743, -0.05875667499999998]], 'holes': []}], 'simplify_tolerance': 3.096498e-05, 'sketch_entity_count': 28}
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
