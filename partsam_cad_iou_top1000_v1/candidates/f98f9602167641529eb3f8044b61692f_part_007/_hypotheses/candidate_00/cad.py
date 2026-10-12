#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.44461138499999997, 0.06233537, -0.133883175], 'basis': [[-0.0, 0.9993136298533611, 0.03704415189067791], [0.5278693896492781, -0.031462545062403154, 0.8487426086449854], [0.8493255603543901, 0.0195544738486073, -0.5275070758588983]], 'axis': [0.03704415189067791, 0.8487426086449854, -0.5275070758588983], 'zmin': -0.04745128926247879, 'zmax': 0.04819554768619426, 'profiles': [{'outer': [[-0.037104906367674245, -0.05285524732230638], [-0.039975815818370744, -0.04952811506237201], [-0.03283161429740573, -0.03232575979742251], [-0.01870362429549504, -0.03509007643503865], [-0.004588861059430299, -0.03228208124966053], [0.007381652798506559, -0.02429890699327705], [0.015365198508598655, -0.01237228611335381], [0.018175108653280817, 0.0016928122179804541], [0.015365198508598655, 0.01574959860707563], [0.008948392314929292, 0.02531549977897836], [-0.0015558988599948802, 0.03226489667834419], [-0.015749951293801863, 0.03504739199526122], [-0.029921049115235583, 0.03222530627051251], [-0.03283162485479352, 0.0355535185218848], [-0.039975815818370744, 0.05274972626408649], [-0.018703613738107246, 0.05699441547789419], [0.002555396699762222, 0.05281602125260833], [0.02059802400196952, 0.04084810173223569], [0.023730473136707148, 0.03751158457299715], [0.0358358540475977, 0.019567436251841718], [0.039090511150531256, 0.0033300061668769224], [0.046060877929613255, 0.0016057508373578998], [0.045655193894656464, -0.0008404915639280761], [0.044576684758174445, -0.0058893291838602105], [0.04296052861554917, -0.012784189605390612], [0.04107982829420706, -0.020487022113508658], [0.03919572190527399, -0.027812955544703852], [0.03761985776878623, -0.03364421809902385], [0.03658241989091285, -0.037106836292210975], [0.036244344352405554, -0.03764992462350855], [0.02731568488474313, -0.035449537876088955], [0.023730473136707148, -0.040774165519172824], [0.005627992365466199, -0.05279524924023444], [-0.015749920535341147, -0.05703704031609594]], 'holes': []}], 'simplify_tolerance': 2.2806291158798028e-05, 'sketch_entity_count': 37}
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
