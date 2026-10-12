#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.17704547, -0.16604930499999998, -0.383434895], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.013141340000000001, 'zmax': 0.013141340000000001, 'profiles': [{'outer': [[-0.08300590499999999, 0.01652361499999999], [-0.07818022499999999, 0.03242248499999997], [-0.07038158500000002, 0.047028764999999986], [-0.05986851500000001, 0.059868504999999975], [-0.04702878500000002, 0.07038158499999998], [-0.03237939499999998, 0.07822331499999997], [-0.016523604999999997, 0.08304898499999998], [2.1545000000011694e-05, 0.08464318499999998], [0.016523624999999986, 0.08304898499999998], [0.032422475000000006, 0.07822331499999997], [0.04702877500000002, 0.07038158499999998], [0.05986851500000001, 0.059868504999999975], [0.07038157500000003, 0.047028764999999986], [0.07822328499999998, 0.03242248499999997], [0.08304899500000001, 0.01652361499999999], [0.08464318500000001, 2.15349999999892e-05], [0.08304899500000001, -0.01652364500000003], [0.07822328499999998, -0.03237943500000001], [0.07038157500000003, -0.04702879500000001], [0.05986851500000001, -0.059868525000000006], [0.04702877500000002, -0.07038160500000001], [0.032422475000000006, -0.07818025500000003], [0.016523624999999986, -0.08300591500000001], [2.1545000000011694e-05, -0.08464318500000001], [-0.016523604999999997, -0.08300591500000001], [-0.03237939499999998, -0.07818025500000003], [-0.04702878500000002, -0.07038160500000001], [-0.05986851500000001, -0.059868525000000006], [-0.07038158500000002, -0.04702879500000001], [-0.07818022499999999, -0.03237943500000001], [-0.08300590499999999, -0.01652364500000003], [-0.08464318500000001, 2.15349999999892e-05]], 'holes': []}], 'simplify_tolerance': 3.385727400000001e-05, 'sketch_entity_count': 32}
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
