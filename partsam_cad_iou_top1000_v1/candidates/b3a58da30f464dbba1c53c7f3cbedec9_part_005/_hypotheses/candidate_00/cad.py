#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.04428899, -0.432739585, 0.206462095], 'basis': [[-0.0, 0.9999999999951323, 3.1201502770724376e-06], [0.500007182587707, -2.7021164645915813e-06, 0.8660212568715632], [0.8660212568757787, 1.560097549289243e-06, -0.5000071825852732]], 'axis': [3.1201502770724376e-06, 0.8660212568715632, -0.5000071825852732], 'zmin': -0.07046583102436198, 'zmax': 0.07012418468935108, 'profiles': [{'outer': [[-0.008640543288223968, 0.013007896606010583], [-0.0030176458308325536, 0.015330126671279847], [0.0030896585657722913, 0.015330126638984075], [0.008714689512404165, 0.013007866030409094], [0.0130415993060915, 0.008666366621405212], [0.015362551569848342, 0.003045936679628804], [0.015362551569848342, -0.0030456733203415485], [0.0130415993060915, -0.008666113378510415], [0.008714689512404165, -0.012974033969464437], [0.0030896585657722913, -0.01532987336086668], [-0.0030176458308325536, -0.015329873328570907], [-0.008640543288223968, -0.012974003393862947], [-0.012952797669891561, -0.008666113401659471], [-0.01529053017469604, -0.0030456733692000317], [-0.01529053017469604, 0.003045936630770321], [-0.012952797669891561, 0.008666366598256156]], 'holes': []}], 'simplify_tolerance': 6.132006122971916e-06, 'sketch_entity_count': 16}
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
