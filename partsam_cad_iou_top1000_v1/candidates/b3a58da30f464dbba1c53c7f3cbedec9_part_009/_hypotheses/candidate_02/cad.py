#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.04428899, -0.43273970500000003, -0.206454835], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.01533, 'zmax': 0.015329999999999996, 'profiles': [{'outer': [[-0.023104395, 0.015060815000000005], [-0.023777505000000004, 0.015229015000000012], [-0.046292845, 0.05423554500000005], [-0.023743824999999996, 0.06726011500000001], [-0.0012284250000000052, 0.02825364500000005], [-0.0013967250000000153, 0.027580525000000022], [-0.0024083461863267193, 0.027000540021579398], [-0.0025746450000000143, 0.02633532500000002], [-0.0008245649999999993, 0.023306285000000038], [-0.00015146499999998952, 0.023104395000000055], [0.000858195000000006, 0.02367654500000005], [0.0015313150000000053, 0.023508285000000018], [0.005771854999999992, 0.016137745000000037], [0.005603604999999984, 0.015464635000000004], [0.004591988905160297, 0.014884662131498173], [0.004425634999999983, 0.014219375000000034], [0.006243045000000003, 0.011055795000000035], [0.0069069174834430185, 0.010856623392056945], [0.007925805000000008, 0.011459615000000034], [0.008598914999999985, 0.011257735000000046], [0.01236831499999999, 0.004728585000000007], [0.012200025000000003, 0.004055475000000031], [0.01117454736148549, 0.003448584409345015], [0.010853804999999994, 0.0027429150000000124], [0.011829845000000005, -0.0021370949999999778], [0.012502944999999988, -0.003315004999999982], [0.025729475, -0.01532998499999999], [0.028724785000000003, -0.01899841499999999], [0.033604775, -0.027479494999999965], [0.035152934999999996, -0.03192201499999997], [0.03757613500000001, -0.04911985499999999], [0.038350174999999986, -0.05012950499999996], [0.042186874999999985, -0.05177870499999998], [0.04301156463847965, -0.051746964419682726], [0.04407159500000002, -0.051139204999999965], [0.044744704999999996, -0.05134114499999998], [0.04629284499999997, -0.054033604999999985], [0.046124584999999996, -0.054706724999999956], [0.037441485, -0.059754934999999954], [0.02441690499999999, -0.06726011499999995], [0.023743755000000005, -0.067058175], [0.022161965000000006, -0.06436577499999996], [0.022330264999999988, -0.06369259499999996], [0.02336900570499077, -0.06307785773053777], [0.023844724999999983, -0.062380044999999995], [0.024315934999999983, -0.05824050499999994], [0.02381108500000001, -0.05706253499999997], [0.010147054999999988, -0.04632648499999997], [0.007084435, -0.042792704999999986], [0.002170735000000007, -0.03431156499999999], [0.0004543149999999829, -0.029902724999999963], [-0.0032814250000000045, -0.012435584999999971], [-0.003988185000000005, -0.011257674999999967], [-0.007723905000000003, -0.007993134999999985], [-0.008493116592103493, -0.00789698236062553], [-0.009541305, -0.008497924999999962], [-0.01021440500000001, -0.008296044999999974], [-0.013983775000000004, -0.0017668949999999906], [-0.01378185500000001, -0.0010937749999999635], [-0.012767940342510603, -0.0005046035883940481], [-0.012603945000000005, 0.00015148500000000675], [-0.014454965000000014, 0.003315065000000006], [-0.015120230554522177, 0.0035146545499631864], [-0.01613772499999999, 0.002944855000000024], [-0.016777175000000005, 0.00311312500000005], [-0.02105141499999999, 0.010483655000000036], [-0.020849455000000017, 0.011156765000000013], [-0.019873465000000007, 0.011728855000000038], [-0.019671555000000007, 0.012401965000000015], [-0.02145524500000001, 0.015464635000000004], [-0.022094735000000004, 0.015632895000000036]], 'holes': []}], 'simplify_tolerance': 2.6904045999999994e-05, 'sketch_entity_count': 89}
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
