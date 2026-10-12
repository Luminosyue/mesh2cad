#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-7.974999999993404e-06, -0.19221159999999998, 4.500000000406956e-08], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.16884747, 'zmax': 0.16884746999999997, 'profiles': [{'outer': [[-0.475623805, -0.084394725], [-0.475623805, 0.08468503499999999], [-0.47504319500000003, 0.089620415], [-0.473417415, 0.093278375], [-0.468540115, 0.099549195], [-0.465869235, 0.101116895], [-0.437708635, 0.104542635], [-0.407051315, 0.104542635], [-0.401303065, 0.09753399225444478], [-0.401303065, 0.12724529499999998], [-0.420463905, 0.142980385], [-0.420463905, 0.288893005], [-0.410999585, 0.320014825], [-0.404206235, 0.326053365], [-0.353459105, 0.341265905], [0.28093825499999997, 0.342136815], [0.306137605, 0.341440095], [0.376335875, 0.336156325], [0.441308455, 0.317111625], [0.456462965, 0.314382695], [0.475159275, 0.291796105], [0.475623805, 0.148670585], [0.468307805, 0.139148255], [0.446882565, 0.129277505], [0.387600135, 0.108432855], [0.387600135, -0.108432845], [0.446882565, -0.12927749500000002], [0.468307805, -0.13914821500000002], [0.475623805, -0.148612515], [0.475159275, -0.291796135], [0.456462965, -0.314382655], [0.441308455, -0.317053565], [0.376335875, -0.33615632500000003], [0.306137605, -0.341440065], [0.28093825499999997, -0.342136815], [-0.353459105, -0.341265865], [-0.404206235, -0.32599527500000003], [-0.410999585, -0.320014785], [-0.420463905, -0.288892965], [-0.420463905, -0.142980375], [-0.401303065, -0.12718721500000002], [-0.401303065, -0.10425229500000001], [-0.455824305, -0.10425229500000001], [-0.464649875, -0.101581395], [-0.468540115, -0.09925887500000001], [-0.473417415, -0.092988045], [-0.47504319500000003, -0.08933007500000001]], 'holes': []}], 'simplify_tolerance': 0.000190249522, 'sketch_entity_count': 50}
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
