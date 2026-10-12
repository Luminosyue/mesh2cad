#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.015487004999999984, -0.464525505, -0.006158244999999979], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.035474375, 'zmax': 0.035474375, 'profiles': [{'outer': [[-0.359274195, -0.193475615], [-0.34136943500000005, -0.188678935], [-0.323457525, -0.193475615], [-0.31034778500000004, -0.20658884500000002], [-0.305552735, -0.22449437500000002], [-0.310347755, -0.242404265], [-0.323457495, -0.255517495], [-0.341369405, -0.260314175], [-0.359274195, -0.255517495], [-0.372383935, -0.242404265], [-0.37718610500000005, -0.22449437500000002], [-0.372383935, -0.20658884500000002]], 'holes': []}, {'outer': [[-0.359274255, 0.255517355], [-0.341369465, 0.260314035], [-0.32345755500000006, 0.255517385], [-0.31034781499999997, 0.242404155], [-0.30555276500000006, 0.22449861499999996], [-0.31034778500000004, 0.20658870499999998], [-0.323457525, 0.193475475], [-0.34136943500000005, 0.188678795], [-0.35927422500000006, 0.19347545499999996], [-0.37238396500000004, 0.206588695], [-0.377186135, 0.22449858499999997], [-0.37238396500000004, 0.24240412499999997]], 'holes': []}, {'outer': [[0.31035490499999996, -0.24240414500000002], [0.305552795, -0.22449425500000003], [0.31035490499999996, -0.20658872500000003], [0.32346464499999994, -0.193475495], [0.341369465, -0.18867878500000002], [0.359281375, -0.193475465], [0.372391115, -0.206588695], [0.377186135, -0.224494225], [0.372391115, -0.24240411499999998], [0.359281375, -0.255517375], [0.341369465, -0.260314055], [0.32346464499999994, -0.255517405]], 'holes': []}, {'outer': [[0.32346464499999994, 0.255517505], [0.341369405, 0.260314175], [0.359281375, 0.255517515], [0.372391115, 0.242404285], [0.377186135, 0.224498755], [0.372391115, 0.20658883499999997], [0.359281375, 0.193475605], [0.341369405, 0.188678925], [0.32346464499999994, 0.193475595], [0.31035490499999996, 0.20658882499999998], [0.305552735, 0.224498725], [0.31035490499999996, 0.24240425499999996]], 'holes': []}], 'simplify_tolerance': 0.000150874454, 'sketch_entity_count': 48}
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
