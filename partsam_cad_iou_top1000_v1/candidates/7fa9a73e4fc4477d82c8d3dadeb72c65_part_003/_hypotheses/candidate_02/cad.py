#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.07422544499999999, 0.034580244999999996, 0.25016395], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.05396708000000003, 'zmax': 0.05396708, 'profiles': [{'outer': [[-0.105225745, 0.013036735000000008], [-0.10309588500000001, 0.021735245000000014], [-0.098613875, 0.02994571500000001], [-0.092001605, 0.03731300500000001], [-0.08343658500000001, 0.043748435000000016], [-0.07314071500000001, 0.04911881500000001], [-0.06138025500000001, 0.05329101500000001], [-0.04846586500000001, 0.05617627500000001], [-0.032523705, 0.058234985], [-0.018358365, 0.058543525], [-0.004014675000000002, 0.057442035000000016], [0.010166994999999995, 0.05494668500000001], [0.023813884999999993, 0.051138485000000025], [0.036601814999999996, 0.04609849500000002], [0.048206654999999994, 0.03994014500000001], [0.058369065, 0.03284169500000002], [0.06502872944131387, 0.02661715011823085], [0.067100355, 0.02480463500000002], [0.07406832499999999, 0.016372815000000013], [0.076820055, 0.012112475000000011], [0.07895047499999999, 0.007541425000000018], [0.08059270499999999, 0.003103545000000013], [0.081569255, -0.0015118949999999853], [0.081835925, -0.010565384999999983], [0.07973567509968582, -0.018883846451952922], [0.089114775, -0.02432276499999999], [0.096526435, -0.029914294999999987], [0.103006195, -0.03692603499999999], [0.10338808815217054, -0.03744007318413103], [0.104515095, -0.03701474499999999], [0.105314125, -0.04140827499999999], [0.10451564499999999, -0.04988487499999999], [0.102785035, -0.054589154999999986], [0.101187395, -0.05565436499999998], [0.1004826466516163, -0.052986836675168694], [0.094885145, -0.04797691499999999], [0.087429125, -0.04247416499999999], [0.079484945, -0.03772585499999999], [0.07059276081948683, -0.0332910914091645], [0.067901765, -0.03635056499999999], [0.059203624999999996, -0.04318543499999999], [0.04873024499999999, -0.04891089499999998], [0.036836665, -0.05334935499999999], [0.023789154999999996, -0.05650087499999999], [0.009898354999999994, -0.05823226499999999], [-0.004480675000000003, -0.058543524999999985], [-0.019081655000000003, -0.05743465499999999], [-0.033460815000000005, -0.05490561499999999], [-0.04735183500000001, -0.051045184999999986], [-0.060355325, -0.04589765499999999], [-0.07224936500000001, -0.03964059499999999], [-0.08263453500000001, -0.03231840499999999], [-0.09133331500000001, -0.024197284999999985], [-0.09812377500000001, -0.015410384999999985], [-0.10282842500000001, -0.006090834999999989], [-0.105314125, 0.003894515000000015]], 'holes': []}], 'simplify_tolerance': 4.212565e-05, 'sketch_entity_count': 65}
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
