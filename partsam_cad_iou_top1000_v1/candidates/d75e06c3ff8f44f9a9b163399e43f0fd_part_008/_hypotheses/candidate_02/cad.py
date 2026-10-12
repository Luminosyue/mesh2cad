#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.226219125, -0.30879009, -0.104760905], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.071815275, 'zmax': 0.07181527500000001, 'profiles': [{'outer': [[-0.04854232000000003, 0.0014305149999999933], [-0.04709041000000003, 0.0022205349999999957], [-0.04551041, 0.0027116150000000006], [-0.019226940000000026, 0.005700814999999998], [-0.017582900000000012, 0.005551345000000013], [-0.016002900000000042, 0.005060265000000008], [-0.014529650000000005, 0.004291614999999999], [-0.013248570000000015, 0.0032240550000000034], [-0.012180990000000003, 0.0019216150000000154], [-0.011412320000000031, 0.0004483849999999956], [-0.010921239999999999, -0.0011529650000000058], [-0.010729110000000042, -0.0028183850000000066], [-0.035368500000000025, -0.005636754999999993], [-0.05223608000000002, -0.005700814999999998], [-0.05208662000000003, -0.004035404999999992], [-0.051616910000000016, -0.0024340649999999853], [-0.05084825000000004, -0.0009394650000000004], [-0.04980207000000003, 0.00036297500000001537]], 'holes': []}, {'outer': [[-0.006352070000000043, 0.0017935149999999955], [-0.005049650000000017, 0.0028610750000000185], [-0.003576400000000035, 0.0036510750000000036], [-0.0019750600000000285, 0.0041421550000000085], [-0.00030964999999999465, 0.004291614999999999], [0.0013771599999999884, 0.0041421550000000085], [0.002978499999999995, 0.0036510750000000036], [0.0044517499999999766, 0.0028610750000000185], [0.005754170000000003, 0.0017935149999999955], [0.00682174999999996, 0.0004910750000000075], [0.007611749999999973, -0.0009821549999999846], [0.008102830000000005, -0.002583525000000003], [0.008252259999999956, -0.00427027499999999], [-0.00887156, -0.00427027499999999], [-0.00870072999999999, -0.002583525000000003], [-0.008209650000000013, -0.0009821549999999846], [-0.00741965, 0.0004910750000000075]], 'holes': []}, {'outer': [[0.01089981000000001, -0.0038859450000000018], [0.011369519999999966, -0.0022845950000000004], [0.01215951999999998, -0.0008113449999999911], [0.013205759999999955, 0.00046972500000000417], [0.014486849999999996, 0.0015373050000000166], [0.015960099999999977, 0.0023059450000000037], [0.017540090000000008, 0.0027970350000000033], [0.043823659999999987, 0.005658095000000002], [0.04546766999999996, 0.005465945], [0.04704769999999997, 0.004974864999999995], [0.04852091999999997, 0.00418484500000002], [0.04978065999999998, 0.003095934999999994], [0.05082687999999996, 0.0017935149999999955], [0.051595539999999995, 0.000320265000000014], [0.05208658999999999, -0.001302424999999996], [0.05223607999999996, -0.0029678449999999967], [0.027596559999999992, -0.005679464999999995], [0.010729009999999983, -0.0055513650000000025]], 'holes': []}], 'simplify_tolerance': 2.0894432e-05, 'sketch_entity_count': 53}
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
