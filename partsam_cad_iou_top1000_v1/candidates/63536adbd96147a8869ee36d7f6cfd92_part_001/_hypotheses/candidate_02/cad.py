#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.032940885, 0.42313218, 0.095154615], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.07389203, 'zmax': 0.07389203, 'profiles': [{'outer': [[-0.032870825, -0.065865935], [-0.032415164999999996, -0.06435391500000001], [-0.032187325, -0.061164195000000005], [-0.029266845, -0.053127725], [-0.02814834499999999, -0.048798795000000006], [-0.024337244999999993, -0.039395295000000004], [-0.021209654999999994, -0.030323185000000002], [-0.017212135000000003, -0.020608995000000005], [-0.012241114999999997, -0.007974335000000003], [-0.008347145, 0.0008077849999999984], [-0.0021540949999999948, 0.015492994999999996], [0.001077065000000002, 0.022307434999999994], [0.0077257950000000075, 0.037261895], [0.010359286653878533, 0.042286546280024075], [0.016135104999999997, 0.054411895], [0.01897731700599546, 0.05918269143493422], [0.02220385500000001, 0.065389565], [0.023923004999999997, 0.067481535], [0.024712865679968065, 0.06798929577024863], [0.025145045000000005, 0.068682855], [0.025911148958656875, 0.06819035922058134], [0.028169075000000002, 0.068475725], [0.029163275000000002, 0.068413595], [0.029993028633846293, 0.06781931528400885], [0.030903125000000004, 0.067667945], [0.031890237499543825, 0.06681964228692426], [0.03235301500000001, 0.066528745], [0.03287082499999999, 0.06574166499999999], [0.03278794500000001, 0.063587565], [0.031390179371024576, 0.05939425091964435], [0.03117239499999999, 0.058264445], [0.02995034499999999, 0.053645545], [0.02597739160895924, 0.04313377281921424], [0.023943695, 0.037013345], [0.017895625, 0.022079585], [0.015575815000000007, 0.015700114999999994], [0.005716645000000006, -0.007684355000000004], [-0.0003107249999999978, -0.020816125000000005], [-0.004453235, -0.030323185000000002], [-0.009237835, -0.040099525000000004], [-0.013546025000000003, -0.049523735], [-0.016570075000000004, -0.054764005000000004], [-0.020567594999999994, -0.062966175], [-0.021727495, -0.06439534499999999], [-0.02276379623477614, -0.06559109791774716], [-0.023840164999999996, -0.067688635], [-0.024420104999999998, -0.06857929500000001], [-0.025600725000000005, -0.068537865], [-0.025935714608008104, -0.06832849270433813], [-0.026304935, -0.068310025], [-0.02775483499999999, -0.068682855], [-0.028148364999999995, -0.068682855], [-0.02849012775003017, -0.06845501500000001], [-0.029598244999999995, -0.068434305], [-0.030431420155692286, -0.06769168969980792], [-0.031420955, -0.067626515], [-0.032228745, -0.066715155]], 'holes': []}], 'simplify_tolerance': 2.7473142e-05, 'sketch_entity_count': 72}
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
