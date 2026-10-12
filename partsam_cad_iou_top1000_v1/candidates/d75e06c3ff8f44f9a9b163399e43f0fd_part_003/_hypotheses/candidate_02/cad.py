#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.226219125, -0.30878996999999997, 0.10140775], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.07181528000000001, 'zmax': 0.07181528, 'profiles': [{'outer': [[-0.04854228999999999, 0.0014305149999999933], [-0.04709040999999997, 0.0022205349999999957], [-0.045510409999999946, 0.0027116150000000006], [-0.019226849999999962, 0.005700814999999998], [-0.017582779999999965, 0.005551345000000013], [-0.016002779999999994, 0.005060265000000008], [-0.014529529999999957, 0.004291614999999999], [-0.013248469999999957, 0.0032240550000000034], [-0.012180899999999995, 0.0019216150000000154], [-0.011412259999999952, 0.0004483849999999956], [-0.010921179999999975, -0.0011529650000000058], [-0.010729019999999978, -0.0028183850000000066], [-0.03536849999999997, -0.005636754999999993], [-0.05223607999999996, -0.005700814999999998], [-0.05208661999999997, -0.004035404999999992], [-0.05161690999999996, -0.0024340649999999853], [-0.050848249999999984, -0.0009394650000000004], [-0.04980203999999999, 0.00036297500000001537]], 'holes': []}, {'outer': [[-0.0063520099999999635, 0.0017935149999999955], [-0.005049589999999993, 0.0028610750000000185], [-0.0035763399999999557, 0.0036510750000000036], [-0.001974999999999949, 0.0041421550000000085], [-0.0003095899999999707, 0.004291614999999999], [0.0013771900000000281, 0.0041421550000000085], [0.002978560000000019, 0.0036510750000000036], [0.004451810000000056, 0.0028610750000000185], [0.005754230000000027, 0.0017935149999999955], [0.006821810000000039, 0.0004910750000000075], [0.007611810000000052, -0.0009821549999999846], [0.00810289000000003, -0.002583525000000003], [0.008252320000000035, -0.00427027499999999], [-0.008871499999999977, -0.00427027499999999], [-0.008700669999999966, -0.002583525000000003], [-0.008209589999999989, -0.0009821549999999846], [-0.007419589999999976, 0.0004910750000000075]], 'holes': []}, {'outer': [[0.010899900000000018, -0.0038859450000000018], [0.011369640000000014, -0.0022845950000000004], [0.012159640000000027, -0.0008113449999999911], [0.013205850000000019, 0.00046972500000000417], [0.01448691000000002, 0.0015373050000000166], [0.015960160000000057, 0.0023059450000000037], [0.017540160000000027, 0.0027970350000000033], [0.04382366000000004, 0.005658095000000002], [0.045467700000000055, 0.005465945], [0.04704773000000001, 0.004974864999999995], [0.04852095000000001, 0.00418484500000002], [0.04978067000000003, 0.003095934999999994], [0.05082691000000006, 0.0017935149999999955], [0.051595570000000035, 0.000320265000000014], [0.05208662000000003, -0.001302424999999996], [0.05223608000000002, -0.0029678449999999967], [0.027596650000000056, -0.005679464999999995], [0.010729070000000007, -0.0055513650000000025]], 'holes': []}], 'simplify_tolerance': 2.0894432e-05, 'sketch_entity_count': 56}
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
