#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.088597415, 0.314251455, 0.21454826], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.028610299999999977, 'zmax': 0.028610300000000005, 'profiles': [{'outer': [[-0.073393015, -0.007538514999999996], [-0.069778585, -0.002740864999999995], [-0.06515654500000001, 0.002472785000000005], [-0.06012782499999997, 0.007251944999999996], [-0.05357381499999997, 0.012336164999999996], [-0.04493060500000001, 0.018030505000000002], [-0.034734455, 0.023558424999999994], [-0.023743294999999998, 0.027977074999999997], [-0.012437845000000003, 0.030805744999999995], [-0.011929424999999994, 0.030898185], [-0.0006054950000000114, 0.031674685], [0.010431915000000014, 0.030620875], [0.021136464999999993, 0.028032534999999997], [0.03148979499999999, 0.025370265000000003], [0.04149183500000003, 0.024076095000000006], [0.05118635666389908, 0.024503397097342814], [0.060534535, 0.026803084999999997], [0.06882643500000002, 0.028919975], [0.070555065, 0.029141834999999998], [0.074197235, 0.028106495000000002], [0.07472414500000002, 0.027579584999999997], [0.07559305500000002, 0.024991255000000004], [0.075722485, 0.022171814999999997], [0.072856845, 0.019130545], [0.05450743499999999, 0.011670594999999992], [0.045402055, 0.005911575000000002], [0.036906785, -0.0011323849999999996], [0.028522435000000013, -0.009165464999999998], [0.01975912499999999, -0.016995165000000007], [0.010136095000000012, -0.023475234999999997], [-0.000439075000000011, -0.028208184999999997], [-0.012021864999999965, -0.030833485000000008], [-0.01260420499999998, -0.030935174999999995], [-0.024492055000000013, -0.03167468500000001], [-0.036019354999999975, -0.030805755000000004], [-0.046150835, -0.029012415], [-0.05383261499999997, -0.026978715], [-0.06018325499999999, -0.024547534999999995], [-0.06631210500000001, -0.021589445], [-0.07135006499999996, -0.018612865000000006], [-0.07443758499999997, -0.016153945000000003], [-0.075722485, -0.013778244999999995], [-0.07537123499999998, -0.011060495000000004]], 'holes': []}], 'simplify_tolerance': 3.0288994000000005e-05, 'sketch_entity_count': 43}
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
