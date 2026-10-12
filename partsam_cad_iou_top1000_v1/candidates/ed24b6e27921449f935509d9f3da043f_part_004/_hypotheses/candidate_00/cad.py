#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.22182827, 0.030340074999999994, -8.023499999999795e-05], 'basis': [[0.014020254548250278, 0.13288473037719495, 0.9910323309029744], [0.0, 0.991129747657421, -0.13289779271506746], [-0.9999017114008767, 0.0018632608827658474, 0.013895891352500108]], 'axis': [0.9910323309029744, -0.13289779271506746, 0.013895891352500108], 'zmin': -0.05174621658547575, 'zmax': 0.05143622742605521, 'profiles': [{'outer': [[-0.06282837382732459, 0.0331980121169525], [-0.05939100718615183, 0.06421214806841197], [-0.037203215475471826, 0.07601369147569137], [-0.012762885464032899, 0.09974731471015325], [0.014920438106902651, 0.1391214993642708], [0.033994518364494894, 0.0949362325675761], [0.05317888012173059, 0.06659563041886943], [0.07241527180383449, 0.0505126427722824], [0.0694454238884209, 0.01944044657714027], [0.07800884158903808, -0.006701836614983301], [0.06300227984152751, -0.03177526612438231], [0.05998837867141684, -0.05869784744541859], [0.034237367770426255, -0.07945455480534104], [0.010453568318224882, -0.10301394727332831], [-0.01307107280671599, -0.13012334913754955], [-0.030305025182924494, -0.09874266262900433], [-0.048746185090659, -0.07084311493791472], [-0.06961927112203224, -0.04517648069318524], [-0.06700530063943058, -0.018253173946288642], [-0.076592469768544, 0.009456109491445513]], 'holes': []}], 'simplify_tolerance': 5.384896970036407e-05, 'sketch_entity_count': 20}
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
