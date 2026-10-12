#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.062925275, -0.349590675, -0.1297448], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.05714783000000001, 'zmax': 0.05714783, 'profiles': [{'outer': [[-0.027553245000000004, -0.019235475000000002], [-0.03514991500000003, -0.013101244999999997], [-0.039009194999999997, -0.006134224999999993], [-0.03480462500000003, 0.0007109149999999995], [-0.027004795000000026, 0.006682645000000001], [-0.02003778500000003, 0.011029415], [-0.012989534999999997, 0.015234005000000002], [-0.007809955000000035, 0.018158935], [-0.0022607927928486545, 0.022197690236402293], [-0.002224165, 0.026080615], [-0.003524145000000034, 0.030366455], [-0.002833534999999998, 0.036358495000000005], [-0.0017773050000000068, 0.037353785], [-0.00029452499999998993, 0.038227205], [0.0017773050000000068, 0.036886615], [0.0031381950000000103, 0.03613506500000001], [0.005453774999999994, 0.033961675000000004], [0.008622454999999973, 0.031605485], [0.014269184999999962, 0.030630505000000002], [0.015751974999999974, 0.034164795], [0.016930055, 0.03960841500000001], [0.01942844499999996, 0.042980215], [0.01985500499999998, 0.04312239500000001], [0.021244549550046742, 0.04339030197911138], [0.027614195000000008, 0.04482860500000001], [0.031624446788910965, 0.04258872631707515], [0.035738985, 0.040400585], [0.03594209500000001, 0.040177155000000006], [0.03856237499999998, 0.026263425], [0.038806094999999985, 0.023968175], [0.038968575000000005, 0.019702655], [0.039009194999999997, -0.027136844999999993], [0.03592179499999998, -0.041558365], [0.02732981499999998, -0.044828604999999994], [0.026761064999999973, -0.044747365], [0.014492614999999986, -0.04251303499999999], [0.009089634999999985, -0.042086475], [0.0061443849999999745, -0.042492724999999995], [0.00039608499999999047, -0.04271615499999999], [-0.0025694549999999983, -0.041030264999999996], [-0.002874155000000045, -0.038044385], [-0.002853825000000032, -0.036988165], [-0.0020194636605462527, -0.035712064947340326], [-0.008134945000000005, -0.031747675], [-0.012787437420788101, -0.028862410584740476], [-0.017803475000000013, -0.026324354999999994], [-0.024140825000000032, -0.02165260499999999]], 'holes': []}], 'simplify_tolerance': 1.7931442e-05, 'sketch_entity_count': 50}
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
