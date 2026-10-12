#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.018375304999999998, -0.43509921500000004, -0.012750865], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.028252004999999997, 'zmax': 0.028252005, 'profiles': [{'outer': [[-0.05188790879299791, 0.037473752727809326], [-0.051844095, 0.03799951500000004], [-0.051371345, 0.03887745500000006], [-0.051168745, 0.03917008500000002], [-0.047927085, 0.042254185000000055], [-0.042096595, 0.04628375500000004], [-0.036198565, 0.05227184500000004], [-0.030007885, 0.057764655000000054], [-0.022781685, 0.060601085000000054], [-0.017306120635641676, 0.061964461824289385], [-0.014812595, 0.06291976500000002], [-0.012066185, 0.06490078500000002], [-0.009162195, 0.06415790500000002], [-0.0066859250000000005, 0.062311945000000035], [-0.0032416649999999995, 0.05807980500000004], [0.004479794999999998, 0.04729676500000002], [0.008239225, 0.04119613500000002], [0.011863585, 0.033654775000000026], [0.015330364999999999, 0.02753162500000006], [0.018011008021159455, 0.02605264246045807], [0.019720115000000003, 0.026000855000000045], [0.020440485, 0.024334995000000026], [0.020395465, 0.01951751500000004], [0.020215365, 0.013101725000000064], [0.020508025, 0.006730945000000044], [0.021701135000000003, -2.2524999999939954e-05], [0.024222425, -0.007496354999999955], [0.027902180157896736, -0.014982029043652955], [0.031741275, -0.02066561499999997], [0.036491215, -0.02600082499999995], [0.042051565, -0.031381064999999986], [0.047071645, -0.036716314999999944], [0.050673495, -0.04259183499999997], [0.052181775, -0.047319264999999944], [0.052406885, -0.05152892499999995], [0.051416375, -0.05519831499999994], [0.049322795, -0.05832740499999994], [0.046869035, -0.061051304999999945], [0.044842995, -0.06355008499999998], [0.042749425, -0.06490078499999996], [0.038809905, -0.06386524499999996], [0.037459215, -0.06314489499999998], [0.032619234999999996, -0.06033092499999998], [0.025370515000000003, -0.05585113499999994], [0.016838635, -0.050088194999999947], [0.008126664999999998, -0.043402254999999945], [-6.753500000000051e-05, -0.036288584999999984], [-0.007136165, -0.029242484999999985], [-0.020508025, -0.014790084999999953], [-0.026406045, -0.007091134999999971], [-0.030345565, 0.0011030750000000644], [-0.033497175000000004, 0.007428825000000028], [-0.035877960979562744, 0.008832870447626165], [-0.039192605, 0.010197725000000046], [-0.040475755, 0.010873075000000065], [-0.043447285, 0.015082745000000064], [-0.046058625, 0.020575555000000023], [-0.048467365, 0.025775735000000022], [-0.051844095, 0.03351968500000002], [-0.052406885, 0.036063495000000056]], 'holes': []}], 'simplify_tolerance': 2.5960313999999998e-05, 'sketch_entity_count': 60}
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
