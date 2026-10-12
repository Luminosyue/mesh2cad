#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.23280376, -0.04166916000000001, 0.023943570000000004], 'basis': [[0.0, 0.9999999998995344, 1.4175027863363373e-05], [-0.9248612032626481, 5.3908313936884785e-06, -0.3803048181005676], [-0.3803048181387752, -1.3109933325991812e-05, 0.9248612031697312]], 'axis': [1.4175027863363373e-05, -0.3803048181005676, 0.9248612031697312], 'zmin': -0.08593375798485922, 'zmax': 0.07191377847561023, 'profiles': [{'outer': [[0.05150743992407932, 0.13770054187146977], [0.05150743992407932, 0.13860644520722246], [0.09848139565821104, 0.1386042334984976], [0.09848139565821104, 0.012129424834091674], [0.2109744827202511, 0.01212869985248301], [0.2109744827202511, -0.009029680145391305], [0.09848139565821104, -0.009030470452096996], [0.09848139565821104, -0.13848737647366421], [0.05458897022243728, -0.13848726885088192], [0.05458897022243728, -0.1386061156595723], [0.05372654619449048, -0.1384866799829825], [0.05150743992407932, -0.13848516476493936], [0.05150743992407932, -0.13817498979445625], [-0.18282177767990426, -0.09747683535888953], [-0.18282177767990426, 0.09455827462181753]], 'holes': []}], 'simplify_tolerance': 7.875925208003108e-05, 'sketch_entity_count': 15}
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
