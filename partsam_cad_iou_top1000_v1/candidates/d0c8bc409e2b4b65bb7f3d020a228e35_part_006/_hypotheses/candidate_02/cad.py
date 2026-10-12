#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.051125665, 0.381224095, -0.088552515], 'basis': [[0.0, 0.6149777597274124, 0.7885444534334466], [0.9999999999992794, 9.466555488106374e-07, -7.382869870001889e-07], [-1.2005100596279008e-06, 0.7885444534328784, -0.6149777597269693]], 'axis': [0.7885444534334466, -7.382869870001889e-07, -0.6149777597269693], 'zmin': -0.19765845157479622, 'zmax': 0.19765857859636066, 'profiles': [{'outer': [[-0.08390259411646572, -0.19484722414832192], [-0.08390271588341333, 0.19484707144427169], [-0.08367362849126946, 0.19765843681831538], [-0.0820318480856063, 0.19722871087082602], [-0.05702330611845988, 0.1843362816420494], [-0.042819959106230814, 0.17677653093158363], [-0.024225808616871625, 0.16547819775057743], [-0.0027680542447047884, 0.14999671200259987], [0.018804192851215224, 0.131583192285159], [0.037818331366956316, 0.11164333796397663], [0.053663470867898244, 0.09062592640354476], [0.06607228091938457, 0.06902422184195013], [0.0747775601015842, 0.04836458254311615], [0.07920655470555776, 0.032626915719638466], [0.08000835670491067, 0.028270761119454667], [0.08390283498562347, 2.0754125755795565e-06], [0.08000838329529819, -0.028270804096389483], [0.07920658529464021, -0.032626958478963186], [0.07477758989860817, -0.04836462580246172], [0.06607234908080836, -0.06902426754783894], [0.053663519132276585, -0.09062596579707898], [0.03781841863319329, -0.11164338811502944], [0.018804257148961775, -0.1315832722861354], [-0.002767985755135176, -0.1499967951549914], [-0.024225711382985383, -0.1654783022869233], [-0.04281984089364743, -0.17677663298086535], [-0.05702317388144594, -0.18433638519067186], [-0.08203172191429942, -0.19722883811207068], [-0.08367353150860989, -0.1976585829388778]], 'holes': []}], 'simplify_tolerance': 7.906340395143864e-05, 'sketch_entity_count': 32}
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
