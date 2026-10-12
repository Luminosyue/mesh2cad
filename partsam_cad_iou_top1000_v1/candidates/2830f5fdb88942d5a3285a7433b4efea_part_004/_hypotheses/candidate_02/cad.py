#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.006980130000000001, 0.13839517499999998, -0.22391895], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.06263718499999998, 'zmax': 0.06263718500000001, 'profiles': [{'outer': [[-0.11803328000000002, 0.02098748], [-0.10228105999999998, 0.03226341], [-0.08496448000000001, 0.03934185], [-0.07089328988229557, 0.04205469001102498], [-0.06984728000000001, 0.04233121], [-0.056103881838434407, 0.043408619529071484], [-0.04868458568486447, 0.044594775629406086], [-0.04687720000000001, 0.050431909999999996], [-0.04627313999999999, 0.05994212], [-0.04497048876159992, 0.0650299493071159], [-0.043407699999999994, 0.07372726], [-0.03965448082091162, 0.08226009185992811], [-0.03728957999999999, 0.08899931], [-0.028383429999999987, 0.10194805], [-0.026555739999999994, 0.10389966], [-0.014149119999999987, 0.11371964], [0.003182980000000002, 0.11655411], [0.003554720000000011, 0.11646117], [0.020793880000000015, 0.10935177], [0.03301463000000002, 0.09547369], [0.03424185269976704, 0.09284123143301784], [0.041425110000000015, 0.07869919], [0.04546772000000002, 0.06367495], [0.046459009999999995, 0.0538085], [0.04668771392798749, 0.04638344792458245], [0.05109395996777825, 0.04332498908184472], [0.061219949999999995, 0.04319859], [0.07537681000000002, 0.04144835], [0.0916092, 0.0370495], [0.10795001, 0.029413460000000002], [0.12122401000000001, 0.0169139], [0.12687745, 0.00040270999999999883], [0.12638181, -0.002555680000000001], [0.12058896000000001, -0.01708428], [0.11873029, -0.01906686], [0.10711361000000001, -0.02945992], [0.10561118, -0.030513170000000003], [0.09249206000000001, -0.037576120000000005], [0.0915937, -0.03799432], [0.07839715, -0.04211437], [0.06560331999999999, -0.043539350000000004], [0.054915960000000014, -0.04329153], [0.047378496096771944, -0.04582412254319492], [0.045173430000000014, -0.06664882], [0.0431556722468829, -0.07279666585826804], [0.04137865000000002, -0.08010869], [0.033123050000000015, -0.09593837], [0.02054605000000001, -0.10915041], [0.0018819200000000091, -0.11655411], [-0.016395009999999988, -0.11204684], [-0.02397423700278776, -0.10521942836522077], [-0.02881714000000002, -0.10152986], [-0.03840475999999998, -0.08760533], [-0.04390335000000001, -0.07332455], [-0.04602529999999999, -0.06260621], [-0.04684623999999998, -0.05252293], [-0.04813564866171045, -0.044998741644403484], [-0.048564230832717874, -0.044790545603442894], [-0.05576786, -0.0438956], [-0.06682693, -0.043539350000000004], [-0.08095285000000002, -0.041200520000000004], [-0.08164982999999998, -0.04103015], [-0.09641074999999999, -0.03601174], [-0.10276696795526288, -0.03174362812119802], [-0.11092384999999999, -0.027198550000000002], [-0.11467578728166367, -0.022299273090313213], [-0.12316011999999998, -0.01363025], [-0.12384266103120879, -0.008344523839987024], [-0.12687745, 0.005002919999999999]], 'holes': []}], 'simplify_tolerance': 5.075098e-05, 'sketch_entity_count': 69}
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
