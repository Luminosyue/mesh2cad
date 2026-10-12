#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.178099465, 0.05844213, 0.035018795], 'basis': [[0.0, 0.6710007802946957, 0.7414566425920734], [-0.9899422624568252, 0.1048953285066259, -0.09492779919154082], [-0.1414719654272975, -0.7339992662812388, 0.664252030555226]], 'axis': [0.7414566425920734, -0.09492779919154082, 0.664252030555226], 'zmin': -0.031661324292421314, 'zmax': 0.027897245897065045, 'profiles': [{'outer': [[-0.16536570876459217, 0.057169078083163266], [-0.1702099465766849, 0.06863905716679126], [-0.15928935494221944, 0.07340399770494789], [-0.1048067630020028, 0.06425592322444676], [-0.0778383612160344, 0.04699790068786307], [-0.05377355829936261, 0.0355227503217686], [-0.037161369143573826, 0.035296147371252244], [-0.013325644735864473, 0.02651468773901899], [0.06899269647054768, -0.01733857841084488], [0.0833348111806483, -0.011531753427346065], [0.11658258201746641, -0.01466007277107828], [0.17338875939217147, -0.044315186636332986], [0.16991370239540254, -0.05485982739544931], [0.1676490755157075, -0.06300592169316387], [0.1638704550206061, -0.07494842490132544], [0.09850682229830188, -0.0637909524829901], [0.07788866610627655, -0.04705448701415181], [0.06059352575767662, -0.03405997519291284], [-0.03297345977684707, -0.01900664073606219], [-0.0549288421085928, -0.0006730986866884594], [-0.06753873545172316, 0.007389561117942878], [-0.11238765064914577, 0.016354141019902204]], 'holes': []}], 'simplify_tolerance': 6.871974119377127e-05, 'sketch_entity_count': 25}
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
