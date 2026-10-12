#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.047981325, -0.473509135, 0.051639569999999996], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.026490864999999975, 'zmax': 0.02649086500000003, 'profiles': [{'outer': [[-0.1132271, -0.010681814999999997], [-0.1058414, 0.014466195000000001], [-0.10376606999999999, 0.017274025000000005], [-0.09857777, 0.021912955000000005], [-0.09302323, 0.02740644500000001], [-0.0882622, 0.031679185000000006], [-0.0827687, 0.034425895000000005], [-0.07495573, 0.035341515], [-0.060062239999999996, 0.035341515], [-0.024598659999999994, 0.034731135], [-0.005554529999999995, 0.034853205000000005], [0.014099979999999998, 0.035280445], [0.03100775, 0.035463564999999996], [0.06677653, 0.035646695], [0.08282976, 0.034792145000000003], [0.09094793000000001, 0.032106434999999996], [0.09815051, 0.02569733500000001], [0.09992063000000001, 0.022950635000000004], [0.09912712000000001, 0.020020735000000005], [0.09906608, 0.017274025000000005], [0.10303361999999999, 0.015137624999999995], [0.10834400999999999, 0.010986995], [0.11212842, 0.002258435000000003], [0.1132271, -0.006348034999999995], [0.1102362, -0.010254534999999995], [0.10724531000000001, -0.011963635], [0.10828296000000001, -0.014038944999999997], [0.10803879999999999, -0.018067515], [0.10114139, -0.025697365], [0.08795700000000001, -0.032899954999999995], [0.06885185, -0.035402535], [0.03100775, -0.035646695], [0.014099979999999998, -0.035585665], [-0.038637599999999994, -0.034792174999999995], [-0.04799579995968566, -0.03474316225218246], [-0.04950250999999999, -0.034853205], [-0.05798692, -0.035036325], [-0.0761765, -0.034731115], [-0.08704142, -0.032289555], [-0.09784530999999999, -0.025453214999999998], [-0.11115178, -0.014344135000000001], [-0.11292189999999999, -0.012390905]], 'holes': []}], 'simplify_tolerance': 4.529084e-05, 'sketch_entity_count': 54}
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
