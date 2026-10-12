#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [2.310000000000159e-06, 0.296483515, 0.26585236], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.017402180000000003, 'zmax': 0.017402180000000003, 'profiles': [{'outer': [[-0.06453702, 0.09211629500000001], [-0.059364169999999994, 0.09009212500000002], [-0.05623796999999997, 0.08753937500000003], [-0.05482104999999998, 0.08627993500000003], [-0.05185225999999998, 0.08326620500000004], [-0.04725292999999997, 0.07800328500000003], [-0.03538910000000001, 0.06418276500000003], [-0.028349489999999977, 0.05582744500000003], [-0.02063522000000001, 0.046538835], [-0.012291170000000018, 0.036339285], [-0.0034972699999999968, 0.02539754500000002], [0.0055777100000000135, 0.013893605000000031], [0.015192450000000024, 0.0015124650000000184], [0.02561691000000002, -0.012071964999999962], [0.03601882000000001, -0.025914964999999957], [0.045554890000000015, -0.039049504999999984], [0.053898940000000006, -0.05156558499999997], [0.06072485, -0.06353062499999998], [0.06453702, -0.07438242499999997], [0.06378358, -0.08352488499999997], [0.05937542000000001, -0.08982223499999997], [0.052189630000000015, -0.09211629499999999], [0.04353072000000002, -0.08976602499999997], [0.03468062000000002, -0.08210795499999998], [0.025830550000000008, -0.07105374499999997], [0.01717163000000002, -0.058515244999999966], [0.008456500000000033, -0.044728394999999976], [-0.000584780000000007, -0.029963254999999966], [-0.009378639999999994, -0.01529931499999998], [-0.017374069999999964, -0.0018162149999999544], [-0.02476223999999999, 0.010823605000000014], [-0.031734380000000006, 0.02301353500000003], [-0.044137990000000016, 0.045133115], [-0.04943450999999999, 0.05475920500000003], [-0.05402264000000001, 0.06326073500000001], [-0.05783484, 0.07054770500000002], [-0.06083729999999998, 0.076474015], [-0.06241163999999999, 0.08018493500000001], [-0.06301889, 0.08192795500000005], [-0.06423339, 0.08586388500000003]], 'holes': []}], 'simplify_tolerance': 3.6846518e-05, 'sketch_entity_count': 40}
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
