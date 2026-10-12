#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.114291555, -0.06717559, -0.008533844999999998], 'basis': [[0.0, 0.9760924469025979, 0.21735578000066927], [-0.9219668297363998, 0.08417512371533177, -0.3780102027899791], [-0.3872688534672167, -0.2003948194120994, 0.8999248588004332]], 'axis': [0.21735578000066927, -0.3780102027899791, 0.8999248588004332], 'zmin': -0.06887048400339353, 'zmax': 0.07803469907300103, 'profiles': [{'outer': [[-0.05014752448343003, -0.0011259466800945886], [-0.04666701433800838, 0.015701760765214876], [-0.037150840959297216, 0.030958674126247664], [-0.022652674782166017, 0.04281770598159184], [-0.005063315473201758, 0.04979534627031641], [0.01361185088690125, 0.051121343927668296], [0.031111132211597364, 0.04664599621517314], [0.04526726223256614, 0.036844396730443985], [0.05440611138546455, 0.02293178947180095], [0.05740725124345189, 0.006544629998474666], [0.05397397345871763, -0.01028738973842272], [0.04475742595688455, -0.02501504269341956], [0.04293037756123331, -0.02811272814631324], [0.029836765206693677, -0.0391960857811614], [0.013793607381538304, -0.04556935454989787], [-0.003267938155815956, -0.046524793056084736], [-0.006304882546523708, -0.04570697374262738], [-0.02377710207392468, -0.04116479928588321], [-0.03796032155119349, -0.031377227179696404], [-0.04709916148442359, -0.017464630523729065]], 'holes': []}], 'simplify_tolerance': 2.1510955145376385e-05, 'sketch_entity_count': 20}
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
