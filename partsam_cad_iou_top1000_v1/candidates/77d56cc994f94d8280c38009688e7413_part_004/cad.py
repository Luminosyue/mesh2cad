#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.1004979, 0.03583211, 0.16923803999999998], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.0010177399999999892, 'zmax': 0.001017740000000017, 'profiles': [{'outer': [[-0.25314015, -0.14249319], [-0.25555134, -0.10598141], [-0.25555134, 0.10598129], [-0.25314015, 0.14249307], [-0.246032, 0.17330581], [-0.23441457000000002, 0.19882649], [-0.21844455, 0.21936828], [-0.19787144, 0.23536962], [-0.17235079, 0.24695569], [-0.14156937, 0.2540639], [-0.10502623999999999, 0.25650638000000003], [0.10502625, 0.25650638000000003], [0.14153805, 0.2540639], [0.17235075, 0.24695569], [0.19787145, 0.23536962], [0.21841324, 0.21936828], [0.23441455, 0.19882649], [0.24600065, 0.17330581], [0.25310886, 0.14249307], [0.25555134, 0.10598129], [0.25555134, -0.10598141], [0.25310886, -0.14249319], [0.24600065, -0.17330593000000002], [0.23441455, -0.19882649], [0.21841324, -0.21936828], [0.19787145, -0.23536961999999997], [0.17235075, -0.24695581000000003], [0.14153805, -0.25406390999999995], [0.10502625, -0.25650638000000003], [-0.10502623999999999, -0.25650638000000003], [-0.14156937, -0.25406390999999995], [-0.17235079, -0.24695581000000003], [-0.19787144, -0.23536961999999997], [-0.21844455, -0.21936828], [-0.23441457000000002, -0.19882649], [-0.246032, -0.17330593000000002]], 'holes': []}], 'simplify_tolerance': 0.00010260255200000002, 'sketch_entity_count': 36}
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
