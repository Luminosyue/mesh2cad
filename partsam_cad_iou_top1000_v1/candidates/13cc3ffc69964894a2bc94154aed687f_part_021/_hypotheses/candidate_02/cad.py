#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.094071795, 0.045477855, 0.10701411], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.02063165, 'zmax': 0.02063165, 'profiles': [{'outer': [[-0.047976955, -0.009672454999999996], [-0.048889825, 3.0849999999998934e-06], [-0.047976955, 0.009672465000000005], [-0.04526200500000001, 0.018971845], [-0.040863575, 0.027543554999999997], [-0.03493576500000001, 0.03505458500000001], [-0.034336834999999996, 0.03572059500000001], [-0.026974495, 0.041998295000000005], [-0.018580725000000006, 0.046666484999999994], [-0.009475605000000005, 0.04954632499999999], [-2.965000000000606e-06, 0.050514495000000006], [0.009475594999999996, 0.04954632499999999], [0.018580714999999998, 0.046666484999999994], [0.026974484999999996, 0.041998295000000005], [0.034336834999999996, 0.03572059500000001], [0.034935764999999994, 0.03505458500000001], [0.040863565, 0.027543554999999997], [0.045262005, 0.018971845], [0.047976935, 0.009672465000000005], [0.048889825, 3.0849999999998934e-06], [0.047976935, -0.009672454999999996], [0.045262005, -0.018971835000000006], [0.040863565, -0.027543545000000003], [0.034935764999999994, -0.035054585], [0.034336834999999996, -0.035720585], [0.026974484999999996, -0.041998284999999996], [0.018580714999999998, -0.046666475], [0.009475594999999996, -0.049546325], [2.965000000000606e-06, -0.050514495], [-0.009475605000000005, -0.049546325], [-0.018580725000000006, -0.046666475], [-0.026974495, -0.041998284999999996], [-0.034336834999999996, -0.035720585], [-0.03493576500000001, -0.035054585], [-0.040863575, -0.027543545000000003], [-0.04526200500000001, -0.018971835000000006]], 'holes': [[[-0.034022445, 0.007298285000000002], [-0.034710065, 3.0849999999998934e-06], [-0.034022445, -0.007298285000000002], [-0.031977345000000004, -0.014309824999999998], [-0.02865184500000001, -0.020778685000000005], [-0.024555884194159477, -0.025972157329385452], [-0.019462071672309445, -0.030316750974021995], [-0.020079275000000008, -0.027617544999999993], [-0.021187775000000006, -3.0849999999998934e-06], [-0.020079275000000008, 0.027617555000000002], [-0.019462073813052372, 0.030316749782071335], [-0.02455586109664645, 0.025972186615870474], [-0.02865184500000001, 0.020778685000000005], [-0.031977345000000004, 0.014309815000000004]], [[0.014446490273844734, 0.03310939058985518], [0.014813204999999996, 0.029849895], [0.016733815, 0.020439515000000005], [0.021932504999999998, 0.014149494999999998], [0.028832474999999996, 0.011479304999999995], [0.03282059676814125, 0.011418751491853445], [0.031977345, 0.014309815000000004], [0.028651834999999997, 0.020778685000000005], [0.02455585941363683, 0.025972187690036928], [0.019469885, 0.030312395000000006]], [[0.016733815, -0.020439515000000005], [0.014813204999999996, -0.029849895], [0.014446489806850793, -0.03310939084987456], [0.019469885, -0.030312395000000006], [0.02455588251089658, -0.025972158403807528], [0.028651834999999997, -0.020778685000000005], [0.031977345, -0.014309824999999998], [0.03282059848985205, -0.011418751465711908], [0.028832474999999996, -0.011479304999999995], [0.021932504999999998, -0.014149485000000003]]]}], 'simplify_tolerance': 2.0205798000000003e-05, 'sketch_entity_count': 70}
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
