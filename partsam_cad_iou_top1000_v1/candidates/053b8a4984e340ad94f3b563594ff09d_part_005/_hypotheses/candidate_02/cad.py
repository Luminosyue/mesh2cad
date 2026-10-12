#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.01790022, -0.243081465, 0.17708332999999998], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.021718150000000002, 'zmax': 0.02171815, 'profiles': [{'outer': [[-0.013620290000000007, 0.0039127350000000005], [-0.014313680000000023, 0.004408014999999987], [-0.015056590000000009, 0.003714634999999994], [-0.016344340000000013, -0.03630422500000002], [-0.026646210000000004, -0.036155625000000025], [-0.02697883770352984, -0.025805828790356245], [-0.027091950000000004, -0.025804205000000024], [-0.027963962994578855, 0.003940747855450002], [-0.02867687000000002, 0.004606145000000006], [-0.02867687000000002, 0.042148574999999994], [-0.01248114000000003, 0.04269336499999998], [-0.008370280000000008, 0.04269336499999998], [-0.006240560000000006, 0.042495265000000004], [0.0006442912106351292, 0.04226421194217571], [0.0032499221193793156, 0.04233137239619706], [0.011787729999999996, 0.04269336499999998], [0.014759409999999973, 0.04269336499999998], [0.028676869999999993, 0.042148574999999994], [0.028676869999999993, 0.004606145000000006], [0.027983469999999983, 0.003962264999999993], [0.026695729999999973, -0.021396205], [0.01634432999999999, -0.021544795000000005], [0.015056579999999986, 0.0037641549999999913], [0.014363199999999993, 0.004408014999999987], [0.013620259999999995, 0.0038136849999999833], [0.01233254999999997, -0.03645278499999999], [0.0020306599999999897, -0.036601404999999976], [0.000742929999999975, 0.0036155750000000098], [-1.0000000022492017e-08, 0.004209904999999986], [-0.0006933900000000159, 0.003714634999999994], [-0.00198114000000002, -0.04269336499999998], [-0.012332540000000003, -0.042544764999999984]], 'holes': []}], 'simplify_tolerance': 1.7077345999999996e-05, 'sketch_entity_count': 32}
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
