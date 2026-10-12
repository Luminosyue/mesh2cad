#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0012707299999999977, 0.23024532, -0.172011265], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.057156155000000014, 'zmax': 0.057156155, 'profiles': [{'outer': [[-0.26563086999999996, -0.03196403], [-0.26975295, -0.0014169399999999976], [-0.26603583, 0.029166970000000004], [-0.23225000999999998, 0.0879793], [-0.19853774, 0.11543488], [-0.1628013, 0.14049823], [-0.12110266, 0.16224923], [-0.029424580000000006, 0.18503072], [0.062363890000000005, 0.18499393], [0.10130229000000002, 0.17594021], [0.14031419, 0.15499889], [0.17071411, 0.12415736999999999], [0.19279632, 0.08801612], [0.2070324990582753, 0.052664816765799365], [0.21474160864398073, 0.05271035649743006], [0.21090373, 0.053899050000000004], [0.21083018, 0.07130722], [0.21498897, 0.07263215], [0.26886967, 0.07296338000000001], [0.26894328, 0.05294215], [0.2415250437366914, 0.052773607354522176], [0.2415981, 0.040244880000000004], [0.20854828, 0.040060870000000005], [0.21152946, 0.0014169500000000023], [0.20902989941030434, -0.03721554728189239], [0.21539376142004596, -0.03718234491320773], [0.21491536, 0.03987686], [0.23456859, 0.040060870000000005], [0.23504701, -0.037042939999999996], [0.21883492546943523, -0.037164391224504656], [0.24211335, -0.037042939999999996], [0.24218696, -0.049666619999999995], [0.24081021815274664, -0.04969654598848121], [0.26960572, -0.0495194], [0.26975295, -0.06950383], [0.21583542, -0.06987186], [0.21167663, -0.06862054], [0.21156624000000002, -0.05124918], [0.21568082510948716, -0.04987645928864813], [0.20770183, -0.049850639999999995], [0.19390043, -0.08536624], [0.17222300000000001, -0.12176511], [0.14222798, -0.15301149], [0.10347369000000001, -0.17439445], [0.06468257, -0.18388981], [-0.027105960000000012, -0.18503072], [-0.11904164999999997, -0.16335333], [-0.16103473999999998, -0.14208077], [-0.19710239999999998, -0.11742229], [-0.23114589, -0.09040834]], 'holes': []}], 'simplify_tolerance': 0.00010790118000000001, 'sketch_entity_count': 50}
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
