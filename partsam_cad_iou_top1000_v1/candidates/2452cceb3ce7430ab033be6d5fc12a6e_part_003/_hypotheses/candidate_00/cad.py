#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.12694633, -0.37112958500000004, 0.0035348550000000034], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.05657084499999998, 'zmax': 0.056570845000000036, 'profiles': [{'outer': [[-0.093298605, 0.03866610999999999], [-0.084677795, 0.05501500999999999], [-0.07302183500000001, 0.06917048], [-0.060473215000000004, 0.07817386], [-0.048766255, 0.07985721999999999], [-0.04513128329643466, 0.07847268955758245], [-0.03976296437143419, 0.07659574454046764], [-0.036957275000000005, 0.07569983999999999], [-0.036268625000000006, 0.07534276], [-0.031532476470359456, 0.07263449213657326], [-0.026653115000000005, 0.07013966999999999], [-0.021211579016790393, 0.06630503593027015], [-0.007881165000000002, 0.057463509999999995], [0.007626094999999996, 0.047720479999999996], [0.028591494999999995, 0.034840289999999996], [0.038921185, 0.02838744], [0.050067034999999996, 0.02122041999999999], [0.061927015, 0.013466829999999999], [0.073225905, 0.005458149999999995], [0.08388715499999999, -0.00395332000000001], [0.09099125717510732, -0.013337163301819768], [0.093273105, -0.01624690000000001], [0.096869365, -0.028489440000000005], [0.09485442499999999, -0.042772439999999995], [0.088095515, -0.057233969999999995], [0.078020915, -0.06965505999999999], [0.06608439499999999, -0.07774025000000001], [0.05348474499999999, -0.07985722], [0.047014907657774344, -0.07846358408891439], [0.039227254999999996, -0.07702611000000001], [0.038360055, -0.07682206999999999], [0.0291980490501137, -0.07294656014489075], [0.025224794999999998, -0.07136392999999999], [0.013058734999999995, -0.06470704], [0.0008926949999999963, -0.05746353000000001], [-0.010431685000000003, -0.05055158000000001], [-0.020735865000000003, -0.04409873], [-0.041522725, -0.03091250000000001], [-0.052974625000000004, -0.023745480000000013], [-0.068379875, -0.014385010000000004], [-0.07613349500000001, -0.009487999999999996], [-0.084575775, -0.0025250200000000167], [-0.092507935, 0.008671829999999991], [-0.093910725, 0.010865279999999991], [-0.096869365, 0.02320984999999999]], 'holes': []}], 'simplify_tolerance': 3.8747746e-05, 'sketch_entity_count': 45}
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
