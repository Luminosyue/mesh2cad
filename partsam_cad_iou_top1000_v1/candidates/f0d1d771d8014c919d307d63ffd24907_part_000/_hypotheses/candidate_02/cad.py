#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.01878988, -0.07630456, 1.720000000003663e-06], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.10409635, 'zmax': 0.10409635, 'profiles': [{'outer': [[-0.1384243, 0.05875062], [-0.12701905, 0.06490345], [-0.10592866999999999, 0.06859786], [-0.07986484999999999, 0.07094761], [-0.051669549999999995, 0.07223794], [-0.022576799999999994, 0.0721157], [0.005169770000000004, 0.06895099], [0.008812341801702109, 0.06678642729368535], [0.011271488251512475, 0.06574372083940325], [0.03190667000000001, 0.06187458], [0.053333610000000004, 0.05721580999999999], [0.07109589, 0.05387454], [0.08693237000000001, 0.05179644], [0.10493773, 0.049664], [0.12701906000000002, 0.045589279999999996], [0.14468784, 0.03659774], [0.15209192000000002, 0.02002723], [0.15315765, -0.0021935600000000006], [0.15209192000000002, -0.02440077], [0.14468784, -0.04098486], [0.12701906000000002, -0.04997641], [0.10493773, -0.05403754000000001], [0.08693237000000001, -0.05616998000000001], [0.07109589, -0.05824809], [0.03190667000000001, -0.06551465000000001], [0.007489183021737164, -0.06976410121933548], [0.005169770000000004, -0.0709612], [-0.022576799999999994, -0.07223794], [-0.051669549999999995, -0.07092045000000001], [-0.07986484999999999, -0.06884234], [-0.10592866999999999, -0.06649259], [-0.12634594999999998, -0.06387119000000001], [-0.1378634, -0.05993230000000001], [-0.14713716, -0.04962327000000001], [-0.15240975, -0.02899162], [-0.15315764999999998, -0.0021935600000000006], [-0.15240975, 0.0247539], [-0.14713716, 0.04630914999999999]], 'holes': []}], 'simplify_tolerance': 6.126305999999999e-05, 'sketch_entity_count': 44}
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
