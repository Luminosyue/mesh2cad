#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [1.1149999999959803e-06, -0.298681885, 1.080000000000525e-06], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.20131811500000002, 'zmax': 0.20131811499999996, 'profiles': [{'outer': [[-0.19723842000000003, 0.020803975000000002], [-0.19426467000000003, 0.04004735500000001], [-0.18939853, 0.058897525000000006], [-0.18271372000000002, 0.077182415], [-0.17425943, 0.09470542500000001], [-0.16415849999999998, 0.111343685], [-0.15246010999999998, 0.126900605], [-0.13928711, 0.141228675], [-0.12476243, 0.15418046500000002], [-0.10903349, 0.16568227500000002], [-0.09229692, 0.17558658500000002], [-0.07462644, 0.183770535], [-0.05624324, 0.190184995], [-0.03734394, 0.19480540500000001], [-0.01807599, 0.197533375], [0.0013885699999999996, 0.198344395], [0.020803969999999998, 0.197238445], [0.04004735, 0.194264715], [0.05889751, 0.189398555], [0.0771824, 0.182713775], [0.09470542, 0.174259455], [0.11134367, 0.164158525], [0.12690058999999998, 0.152460135], [0.14122865, 0.139262555], [0.15418045000000002, 0.12476245500000001], [0.16568224999999998, 0.109033505], [0.17558654, 0.092272355], [0.18377052, 0.074626445], [0.19018497, 0.056243255000000006], [0.19480535999999998, 0.037343955000000005], [0.19753333, 0.018075995000000004], [0.19834437, -0.001388564999999996], [0.19723840999999998, -0.020803974999999995], [0.19426469000000002, -0.040047345], [0.18939853, -0.058897504999999996], [0.18271374, -0.077182395], [0.17425943, -0.094705425], [0.16415849999999998, -0.11134369499999999], [0.15246010999999998, -0.126900595], [0.13926254, -0.141228675], [0.12476243, -0.154205055], [0.10903349, -0.165682265], [0.09227234, -0.175586575], [0.07462643, -0.183770545], [0.05624324, -0.190209575], [0.03734395, -0.194805385], [0.018076, -0.197533365], [-0.0013885600000000005, -0.198344395], [-0.02080398, -0.197238455], [-0.04004735, -0.194264695], [-0.058897490000000004, -0.189398555], [-0.07718238, -0.182713755], [-0.09470541, -0.174259455], [-0.11134368, -0.164158525], [-0.12690057999999999, -0.152460125], [-0.14122867, -0.139287145], [-0.15420503000000002, -0.124762455], [-0.16568224999999998, -0.109033505], [-0.17558656, -0.092296935], [-0.18377053, -0.074626455], [-0.19020954, -0.056243245], [-0.19480535, -0.037343944999999996], [-0.19753335, -0.018075994999999997], [-0.19834437, 0.001388565000000004]], 'holes': []}], 'simplify_tolerance': 7.933775800000001e-05, 'sketch_entity_count': 73}
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
