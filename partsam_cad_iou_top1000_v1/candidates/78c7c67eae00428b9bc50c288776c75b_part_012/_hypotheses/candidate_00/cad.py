#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.22426531500000002, -0.18144281, -0.007360250000000002], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.04175848999999998, 'zmax': 0.04175849000000001, 'profiles': [{'outer': [[-0.05063888, -0.008722105000000008], [-0.050209057567679134, -0.0035437351363044826], [-0.05003736, -0.0009339350000000246], [-0.04709305999999999, 0.00891204499999998], [-0.04190094999999999, 0.019992804999999975], [-0.04034965, 0.023443664999999975], [-0.03924158, 0.02651458499999998], [-0.03734203, 0.030598634999999985], [-0.035759070000000004, 0.033352994999999996], [-0.03306803, 0.037342034999999996], [-0.032371540000000004, 0.03788026499999997], [-0.02857243, 0.040476285], [-0.02243054, 0.04015972499999998], [-0.013154389999999998, 0.03664552499999996], [-0.0010922499999999977, 0.030123734999999985], [0.011254850000000002, 0.021100854999999974], [0.018124890000000005, 0.01350266499999997], [0.019232970000000002, 0.013059424999999986], [0.020730098757145366, 0.008711126273006279], [0.024678340000000003, 0.003973234999999992], [0.03214992, -0.004638095000000009], [0.04319898, -0.01711181500000003], [0.047662930000000006, -0.022810455000000007], [0.05063888, -0.026989485000000007], [0.05060723, -0.028255855000000024], [0.050132350000000006, -0.03120016500000003], [0.047916200000000006, -0.03531586500000003], [0.047441300000000006, -0.035917365000000034], [0.04389548, -0.039304915000000024], [0.04041296, -0.04047628500000003], [0.03525252, -0.03807019500000003], [0.022430540000000002, -0.027274395000000007], [0.011011444559764072, -0.01685990544937152], [0.0055562000000000025, -0.024520065000000008], [-0.0035299999999999984, -0.03240320500000002], [-0.01188802, -0.03617066500000002], [-0.02011942, -0.03639227500000003], [-0.027717619999999995, -0.034207755000000034], [-0.03598068, -0.029110635000000024], [-0.04335728, -0.022588845000000024], [-0.04801118, -0.016003725000000024]], 'holes': []}], 'simplify_tolerance': 2.0255552e-05, 'sketch_entity_count': 41}
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
