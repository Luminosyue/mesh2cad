#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.15031907, -0.12194826, -0.11127366], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.018830490000000005, 'zmax': 0.018830490000000005, 'profiles': [{'outer': [[-0.036820120892506344, 0.019579505616416987], [-0.03463954999999999, 0.021424639999999995], [-0.03177072, 0.023744139999999997], [-0.029756439999999995, 0.02545322], [-0.026887610000000006, 0.02783373], [-0.024324000000000012, 0.029909059999999987], [-0.014271709539940815, 0.017766704359321307], [0.000396759999999996, 0.029909059999999987], [0.01272659999999999, 0.015015560000000011], [0.03811877999999999, -0.015748010000000007], [0.039217459999999996, -0.018189590000000005], [0.03903437, -0.021241519999999986], [0.0375694, -0.02435451999999999], [0.03500578, -0.027101260000000002], [0.03183177999999999, -0.029054479999999994], [0.028474609999999997, -0.02990906], [0.02548373999999999, -0.029542810000000003], [0.02322528, -0.028016849999999996], [0.013755289125651073, -0.016541942112938954], [0.01449673, -0.018189590000000005], [0.014252559999999997, -0.021241519999999986], [0.012787640000000003, -0.02435451999999999], [0.010285059999999999, -0.027101260000000002], [0.007111010000000001, -0.029054479999999994], [0.003753880000000001, -0.02990906], [0.0007629700000000017, -0.029542810000000003], [-0.0014954500000000093, -0.028016849999999996], [-0.026887610000000006, 0.0027467499999999923], [-0.03921746000000001, 0.01757918], [-0.03866813999999999, 0.01806751000000001]], 'holes': []}], 'simplify_tolerance': 1.5686984e-05, 'sketch_entity_count': 30}
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
