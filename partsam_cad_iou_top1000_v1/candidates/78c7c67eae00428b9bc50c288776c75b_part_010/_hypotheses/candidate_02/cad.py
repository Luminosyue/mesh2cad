#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.206314535, -0.0464638, -0.05166733], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.05950349499999999, 'zmax': 0.05950349499999999, 'profiles': [{'outer': [[-0.04236003, -0.10778375000000001], [-0.045462619999999995, -0.10569424999999999], [-0.04698227, -0.10407962000000001], [-0.04764712, -0.09926741], [-0.0465707, -0.08612885], [-0.03997579195251173, -0.07043055079943819], [-0.03732621, -0.06289102], [-0.01848897, -0.03256150000000001], [-0.003762892219859322, -0.007134767107984271], [0.0006648600000000032, 0.02803419], [-0.0011080399999999976, 0.06238444], [-0.0023510815860451543, 0.07621057657091247], [-0.00338749, 0.07764418000000001], [-0.004907129999999996, 0.08685697], [-0.0049387899999999985, 0.08787007], [-0.00379906, 0.0955316], [0.0008548400000000025, 0.10290821], [0.0012347499999999997, 0.10322477], [0.008484720000000001, 0.10797365], [0.01839405000000001, 0.11069639], [0.02827172, 0.11034812], [0.03590158, 0.10597916], [0.0414736, 0.10021718], [0.041856168007558335, 0.09901359386886274], [0.04505109, 0.09132093999999999], [0.04593754, 0.08318455], [0.047393859999999996, 0.07694764], [0.04764712, 0.0184098], [0.0407454, -0.018346539999999995], [0.03985894000000001, -0.02065765], [0.023712739999999996, -0.05108215000000001], [0.019719712395401188, -0.05562147273958569], [0.0031975700000000037, -0.07697939], [-0.011682249999999998, -0.09138434000000001], [-0.017950789999999994, -0.10173683], [-0.01867895, -0.10306655], [-0.020895089999999998, -0.10673903000000001], [-0.02276298, -0.10822697], [-0.030139589999999997, -0.11069639], [-0.033400479999999996, -0.11060141000000001], [-0.03805438, -0.10965164]], 'holes': []}], 'simplify_tolerance': 4.4278556000000006e-05, 'sketch_entity_count': 47}
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
