#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.171523065, 0.156726325, -0.006844564999999997], 'basis': [[0.0, 0.9865404477508946, -0.16351741482626453], [-0.08174640673542563, 0.1629701485008733, 0.9832386565241675], [0.9966531618300553, 0.013366961100713138, 0.08064613670279354]], 'axis': [-0.16351741482626453, 0.9832386565241675, 0.08064613670279354], 'zmin': -0.019725654249565402, 'zmax': 0.039061789490736444, 'profiles': [{'outer': [[-0.05715990280499526, 0.13423929863289125], [-0.0015592772272727217, 0.14607798200473981], [0.05448586210735756, 0.13573667470492667], [0.10243660197606794, 0.10473771411658202], [0.13502305058236555, 0.05784564821060805], [0.14726901331820494, 0.0021667949299089308], [0.1372525334126859, -0.0538519518888379], [0.10655361914747806, -0.10159276189053616], [0.0592047036823305, -0.13451933354684628], [0.002352576899833169, -0.14765952920393913], [-0.05453034488547108, -0.13816532990617236], [-0.10281341152920197, -0.10749529754558795], [-0.13506750509581233, -0.0602742701552285], [-0.14647570122672066, -0.0037483172883296372], [-0.13520428481849017, 0.053523826741648975], [-0.10388711706564503, 0.10197053167818895]], 'holes': []}], 'simplify_tolerance': 5.874894290898512e-05, 'sketch_entity_count': 22}
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
