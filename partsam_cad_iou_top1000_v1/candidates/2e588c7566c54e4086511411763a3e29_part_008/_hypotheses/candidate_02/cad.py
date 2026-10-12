#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.070702475, -0.41888341500000004, 0.158981725], 'basis': [[0.12241636762866405, 4.032308934486899e-09, 0.9924788324879296], [0.0, 1.0, -4.062866433512515e-09], [-0.9924788324879296, 4.973613509510272e-10, 0.12241636762866405]], 'axis': [0.9924788324879296, -4.062866433512515e-09, 0.12241636762866405], 'zmin': -0.03910298948167622, 'zmax': 0.039095413259589415, 'profiles': [{'outer': [[-0.04626276824010617, 0.011606515000000265], [-0.044193796663094136, 0.014780495000000303], [-0.04190164783368607, 0.01751870500000024], [-0.039531069254827945, 0.019834135000000214], [-0.03718464029770537, 0.021765855000000275], [-0.03494072368657755, 0.023372355000000223], [-0.03254000712527946, 0.024874805000000277], [-0.029644660469264825, 0.026442265000000253], [-0.026188325041720813, 0.028029265000000247], [-0.02209863640388095, 0.029564235000000254], [-0.017351472260047324, 0.030949595000000253], [-0.011983003680651173, 0.03206828500000028], [-0.006131967378551066, 0.03279674500000026], [-3.474920504119375e-06, 0.03305691500000023], [0.006131054298025163, 0.03279674500000023], [0.011982070750548603, 0.032068285000000245], [0.017350538105781105, 0.030949595000000277], [0.022097702249614732, 0.029564235000000272], [0.026187390887454566, 0.02802926500000023], [0.029643726314998578, 0.026442265000000218], [0.03253908289580156, 0.024874805000000253], [0.034939809381887954, 0.02337235500000022], [0.03718370736760281, 0.021765855000000306], [0.03953014502535004, 0.01983413500000027], [0.04190071367941985, 0.017518705000000235], [0.044192863732991576, 0.014780495000000286], [0.04626183408583992, 0.01160651500000024], [0.04793270077758942, 0.008016265000000218], [0.049030528698912584, 0.00410080500000027], [0.0494105369000075, -3.2449999997535687e-06], [0.049030528698912584, -0.004100824999999746], [0.04793270077758942, -0.008016254999999776], [0.04626183408583992, -0.011606514999999783], [0.044192863732991576, -0.01478698499999975], [0.04190071367941985, -0.01751869499999976], [0.03953014502535004, -0.019834154999999725], [0.03718370736760281, -0.021765854999999695], [0.034939809381887954, -0.023372384999999732], [0.03253908289580156, -0.024881304999999767], [0.029643726314998578, -0.026448784999999777], [0.026187390887454566, -0.02802929499999975], [0.022097702249614732, -0.029564224999999722], [0.017350538105781105, -0.030949594999999715], [0.011982070750548603, -0.03206831499999974], [0.006131054298025163, -0.032803264999999755], [-3.474920504119375e-06, -0.033056914999999756], [-0.006131967378551066, -0.03280326499999973], [-0.011983003680651173, -0.03206831499999971], [-0.017351472260047324, -0.03094959499999974], [-0.02209863640388095, -0.02956422499999974], [-0.026188325041720813, -0.028029294999999732], [-0.029644660469264825, -0.026448784999999742], [-0.03254000712527946, -0.024881304999999743], [-0.03494072368657755, -0.02337238499999973], [-0.03718464029770537, -0.021765854999999727], [-0.039531069254827945, -0.01983415499999978], [-0.04190164783368607, -0.017518694999999758], [-0.044193796663094136, -0.014786984999999732], [-0.04626276824010617, -0.011606514999999758], [-0.04793362500706732, -0.008016254999999747], [-0.049031461629015144, -0.004100824999999736], [-0.04941146983011004, -3.244999999749042e-06], [-0.049031461629015144, 0.004100805000000279], [-0.04793362500706732, 0.008016265000000248]], 'holes': []}], 'simplify_tolerance': 1.976440134602351e-05, 'sketch_entity_count': 64}
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
