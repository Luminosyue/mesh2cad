#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.35181253999999995, 3.8187114, 0.030253019999999964], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.94401795, 'zmax': 0.94401795, 'profiles': [{'outer': [[-0.59524712, 0.0909234299999997], [-0.52420089, 0.2687405300000001], [-0.5114651600000001, 0.29431187999999997], [-0.40179590000000004, 0.45127856999999993], [-0.28242117000000005, 0.5639904699999998], [-0.17099136000000004, 0.6185072699999998], [-0.04791452000000003, 0.63406312], [0.11374440999999996, 0.6053284399999996], [0.29157980999999994, 0.5342701699999997], [0.44856893999999997, 0.42459523999999993], [0.4597874665846719, 0.41271516262587027], [0.5212891099999999, 0.36253917000000024], [0.53291735, 0.33698212999999955], [0.5378111351140797, 0.33009047816781617], [0.56129893, 0.3052176200000001], [0.61583093, 0.19379079], [0.63139972, 0.07072126999999995], [0.60267779, -0.09092343000000014], [0.5316322099999999, -0.2687388700000004], [0.5188964599999999, -0.29431021000000035], [0.40922695, -0.45127833000000006], [0.28985189999999994, -0.5639897600000001], [0.17842223999999995, -0.6185065500000002], [0.05534555999999996, -0.63406312], [-0.10631310000000005, -0.6053279600000003], [-0.28414876000000006, -0.5342704100000004], [-0.44113767000000004, -0.4245940400000001], [-0.55386797, -0.30521715000000027], [-0.63139972, -0.20356381000000034], [-0.6239685700000001, -0.0707198400000002]], 'holes': []}], 'simplify_tolerance': 0.000253625248, 'sketch_entity_count': 36}
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
