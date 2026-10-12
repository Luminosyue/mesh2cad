#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.334511625, -0.16881781, -0.017903895000000003], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.062374995000000044, 'zmax': 0.06237499499999999, 'profiles': [{'outer': [[-0.342981305, -0.013512809999999986], [-0.349737735, -0.010107569999999982], [-0.360061465, -0.0014053499999999997], [-0.3899118720086306, 0.010987775431581102], [-0.402761845, 0.013891140000000024], [-0.417355625, 0.016431520000000005], [-0.42092276343554874, 0.016974739697296206], [-0.438273405, 0.01848549000000002], [-0.431517065, 0.06172635000000001], [-0.419842005, 0.07442837000000001], [-0.404761705, 0.07626610000000002], [-0.391519245, 0.07875245000000002], [-0.360764145, 0.08188743000000001], [-0.343846115, 0.08210363000000001], [-0.317901555, 0.08318465000000001], [-0.282660305, 0.06313168000000001], [-0.24233812500000002, 0.028430890000000014], [-0.217907015, 0.01243175000000002], [-0.201151205, 0.007026620000000011], [-0.173368945, 0.003837620000000014], [-0.135479095, 0.001999890000000004], [-0.117426055, 0.0024322900000000036], [-0.058996785, 0.002972820000000015], [-0.007215825000000004, 0.004270020000000013], [0.044565135, 0.0034052200000000143], [0.088778965, 0.009026530000000005], [0.109588605, 0.009134630000000005], [0.121047455, 0.013512770000000007], [0.15893728499999998, 0.022160950000000013], [0.186719555, 0.03318737000000002], [0.203475395, 0.04226796000000002], [0.227906505, 0.05399705000000002], [0.268228615, 0.08059020000000001], [0.303469955, 0.09756225000000002], [0.328982085, 0.10015669], [0.346116275, 0.09977835000000002], [0.377249715, 0.10085935000000001], [0.405950845, 0.09772440000000002], [0.434003385, 0.09734604000000001], [0.442759665, 0.01799903], [0.442705605, 0.017728750000000015], [0.404653635, 0.01567481000000001], [0.389411185, 0.012972270000000008], [0.37589844499999997, 0.009945400000000021], [0.344764975, -0.0024863699999999878], [0.334279085, -0.011134529999999976], [0.32768068034638126, -0.01413868340672034], [0.32752768490994594, -0.027298999408592345], [0.3481469830121235, -0.04043694663899438], [0.374330935, -0.038160079999999985], [0.416166485, -0.031241559999999974], [0.409788455, -0.08091451999999999], [0.378168585, -0.08388734999999997], [0.350278195, -0.09340037000000001], [0.265309865, -0.09188689], [0.224987745, -0.09410299], [0.201043095, -0.09069777000000001], [0.156667145, -0.09096801999999998], [0.118831365, -0.09015721999999998], [0.107372525, -0.08967079], [0.100778295, -0.09015721999999998], [0.09488672499999999, -0.08707637000000001], [0.086562865, -0.08707637000000001], [0.042294985, -0.09021133999999997], [-0.007215825000000004, -0.08896817000000001], [-0.056672595000000006, -0.09021133999999997], [-0.10099448500000001, -0.08875191999999998], [-0.10931837500000001, -0.08902217000000001], [-0.115155905, -0.09523809999999999], [-0.121804165, -0.09885949999999999], [-0.133262995, -0.10085935000000001], [-0.171098795, -0.09199494999999996], [-0.215474775, -0.09069777000000001], [-0.239365325, -0.09410299], [-0.340440875, -0.09291387000000001], [-0.364709855, -0.09340037000000001], [-0.392600235, -0.09604883999999997], [-0.435246585, -0.09194094999999997], [-0.442759665, -0.05480784], [-0.388762565, -0.050321599999999994], [-0.3650551640941706, -0.040876395223475276], [-0.34250845290632775, -0.026385686482734656]], 'holes': []}], 'simplify_tolerance': 0.00017710386600000002, 'sketch_entity_count': 88}
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
