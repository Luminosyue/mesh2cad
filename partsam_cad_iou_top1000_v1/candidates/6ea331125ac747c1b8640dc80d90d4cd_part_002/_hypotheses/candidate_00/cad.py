#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.069553085, 0.396509855, -0.044579444999999995], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.015470184999999997, 'zmax': 0.015470184999999997, 'profiles': [{'outer': [[-0.030669874999999996, -0.06381785500000003], [-0.030085174999999995, 0.021346394999999962], [-0.028379934999999995, 0.071041825], [-0.024238654999999994, 0.09247899499999995], [-0.018976774999999994, 0.098666545], [-0.013958524999999996, 0.102515515], [-0.006552934999999996, 0.10348993499999998], [0.005968355000000002, 0.10100513499999997], [0.018099895000000005, 0.09696132499999999], [0.02443360500000001, 0.09311235499999998], [0.027697895, 0.08838647499999996], [0.030669875, 0.08166295499999998], [0.029841635000000005, 0.06046933499999996], [0.021656485000000003, 0.012235644999999962], [0.005919595000000007, -0.07020026500000004], [0.002606565000000005, -0.084719125], [0.0013902850208475915, -0.08774983725852435], [0.0007800350000000053, -0.09242570500000002], [-0.002240304999999998, -0.097864385], [-0.007191184999999996, -0.10171508500000004], [-0.013221494999999993, -0.10348993500000003], [-0.019449014999999997, -0.10268038500000004], [-0.024929224999999996, -0.09964960500000003], [-0.028717624999999997, -0.09472989500000001], [-0.030419814999999996, -0.08880334500000003], [-0.029738235751113257, -0.08341527765797326], [-0.030377534999999997, -0.07882392500000002]], 'holes': []}], 'simplify_tolerance': 4.1395974000000004e-05, 'sketch_entity_count': 45}
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
