#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.046004935000000004, 0.25066173, -0.03050252], 'basis': [[0.0, 0.8792867228977173, -0.47629282897792324], [-0.22447799526740125, 0.46413743500844484, 0.8568465854892056], [0.9744791581356312, 0.10691725940920341, 0.19738052082132254]], 'axis': [-0.47629282897792324, 0.8568465854892056, 0.19738052082132254], 'zmin': -0.011802075428240924, 'zmax': 0.010116969388451328, 'profiles': [{'outer': [[-0.037247498277934186, -0.004402633069184628], [-0.037110388548578704, -0.0024504276964922105], [-0.029431210183514085, 0.0012609601044559215], [-0.026811971969388174, -0.004154098332060197], [0.030684838958411998, 0.02364546033235779], [0.032303344581799356, 0.023088094888819282], [0.03691700514040928, 0.013535616238480467], [0.03635299902769502, 0.01191215638263033], [-0.02113536857852184, -0.015883302375415402], [-0.018536167457890863, -0.021292173413211598], [-0.026215345822955493, -0.025003587592761424], [-0.02780265721926899, -0.023921383548851732], [-0.02815148418974433, -0.023248211471063766], [-0.02844876324220984, -0.022584337967771862], [-0.028976997527780303, -0.021541355336568892], [-0.036680077450637644, -0.005617028537438416]], 'holes': []}], 'simplify_tolerance': 1.4832900683668693e-05, 'sketch_entity_count': 22}
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
