#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.12170084, -0.0076137500000000025, -0.0012000050000000005], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.4590362, 'zmax': 0.4590362, 'profiles': [{'outer': [[-0.031549455000000004, -0.23670502], [-0.025049035, -0.23236168971827312], [-0.025049035, 0.2319694089111031], [-0.031549455000000004, 0.23631275999999998], [-0.041188014999999994, 0.25077057999999997], [-0.044606335, 0.26786221], [-0.041188014999999994, 0.28495384999999995], [-0.031549455000000004, 0.29941167], [-0.025049035, 0.30377046912264843], [-0.025049035, 0.37831335], [0.025105065, 0.37831335], [0.025105065, 0.3037440508895572], [0.031549455000000004, 0.29941167], [0.041244055, 0.28495384999999995], [0.044606335, 0.26786221], [0.041244055, 0.25077057999999997], [0.031549455000000004, 0.23631275999999998], [0.025105065, 0.23198037517606548], [0.025105065, -0.23237266866888404], [0.031549455000000004, -0.23670502], [0.041244055, -0.2512189], [0.044606335, -0.26825448], [0.041244055, -0.28534611], [0.031549455000000004, -0.29980394], [0.025105065, -0.3041367618741495], [0.025105065, -0.37831335], [-0.025049035, -0.37831335], [-0.025049035, -0.3041734671061254], [-0.031549455000000004, -0.29980394], [-0.041188014999999994, -0.28534611], [-0.044606335, -0.26825448], [-0.041188014999999994, -0.2512189]], 'holes': []}], 'simplify_tolerance': 0.00015132534, 'sketch_entity_count': 35}
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
