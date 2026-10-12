#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.031156475, 0.21750401, 0.0033961750000000013], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.030436995, 'zmax': 0.030436995, 'profiles': [{'outer': [[-0.10733361999999999, 0.018289885000000002], [-0.10778178000000002, 0.018487605], [-0.10797948999999998, 0.018790795000000002], [-0.10792674, 0.019186245], [-0.10761042000000001, 0.019594894999999998], [-0.10697766, 0.019963985], [-0.10588355000000002, 0.020280355000000003], [-0.10413039999999998, 0.020530814999999997], [-0.10152037, 0.020688985000000003], [-0.09363760000000002, 0.020833985000000003], [-0.08889211999999999, 0.020992175], [-0.08402802000000001, 0.021348085], [-0.07925613000000001, 0.021967635000000003], [-0.07448429999999998, 0.022811265], [-0.06421561, 0.024933555], [-0.0583892, 0.026054024999999998], [-0.05199601000000001, 0.027016305], [-0.045035909999999985, 0.027596304999999998], [-0.03748269000000001, 0.027609485], [-0.02934951999999999, 0.026897664999999998], [-0.020662619999999993, 0.025566284999999998], [-0.011659400000000014, 0.023852645000000002], [-0.002036590000000005, 0.021914915000000004], [0.007928889999999994, 0.019805805], [0.01811855000000001, 0.017433065], [0.02838716999999999, 0.014625315000000003], [0.03855042, 0.011211204999999998], [0.04846321000000001, 0.007137994999999998], [0.057914629999999995, 0.0027616050000000038], [0.06672014000000001, -0.0014302349999999985], [0.07464249, -0.004962985], [0.08154977999999999, -0.007493904999999999], [0.08746842999999999, -0.009141645], [0.09247758, -0.010143474999999999], [0.09665622, -0.010723475], [0.10493444, -0.011606664999999999], [0.10639764, -0.011843935], [0.10725449, -0.012160305], [0.10764994, -0.012608485], [0.1079004, -0.013373034999999998], [0.10797949, -0.013992584999999998], [0.10792674, -0.015600774999999999], [0.10734676, -0.021308535], [0.10712265, -0.021809445], [0.10643719, -0.022508084999999997], [0.10531671, -0.023035365], [0.10426218999999999, -0.023364905], [0.10162579, -0.023931735], [0.09856759, -0.024459015], [0.0943494, -0.025052195], [0.08891846, -0.025684924999999997], [0.0824066, -0.026304475], [0.07501153999999999, -0.026858115], [0.06691791, -0.027279934999999998], [0.058151919999999996, -0.027543575], [0.049227789999999993, -0.027609485], [0.04010591999999999, -0.027438115], [0.03124766000000001, -0.027003115], [0.02270578000000001, -0.026238565], [0.014388010000000007, -0.025078555], [0.0063866200000000095, -0.023496734999999998], [-0.0015093800000000046, -0.021374445], [-0.009194389999999997, -0.018777605], [-0.01722303232361851, -0.015483070964694208], [-0.03858997, -0.008113454999999999], [-0.04858190999999998, -0.0047652549999999995], [-0.0532483, -0.0030647850000000004], [-0.05799378000000002, -0.001087504999999999], [-0.06277879, 0.0011402249999999982], [-0.06740559999999998, 0.0034470650000000026], [-0.07907326812964613, 0.009556110892064098], [-0.08189102533804653, 0.01092905386574809], [-0.08412029000000001, 0.011870305000000001], [-0.08603163, 0.012437115000000002], [-0.08749485999999998, 0.012713934999999999], [-0.08923484000000001, 0.012845755000000004], [-0.09010483, 0.013043494999999999], [-0.09301806999999998, 0.014322125000000002], [-0.09595759000000001, 0.015442595], [-0.09921349999999998, 0.016589415], [-0.1008745, 0.017090335], [-0.10415681000000002, 0.017841705000000003]], 'holes': []}], 'simplify_tolerance': 4.3191796e-05, 'sketch_entity_count': 91}
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
