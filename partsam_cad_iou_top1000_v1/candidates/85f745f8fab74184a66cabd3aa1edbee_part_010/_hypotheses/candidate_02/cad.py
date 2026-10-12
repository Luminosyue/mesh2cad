#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.109253235, -0.331677915, -0.003773565000000003], 'basis': [[0.0, 0.9970115641201617, -0.07725244986839558], [-0.9960521694707101, -0.006857683784893604, -0.0885045076015819], [-0.08876979042834371, 0.07694747028834269, 0.9930755314292729]], 'axis': [-0.07725244986839558, -0.0885045076015819, 0.9930755314292729], 'zmin': -0.06638458675888227, 'zmax': 0.067588164409309, 'profiles': [{'outer': [[-0.05884204902585859, 0.008144822016619275], [-0.0472275888883291, 0.014905864566833828], [-0.014740884593126452, 0.031039041803510286], [0.013740869480697904, 0.035219823622698286], [0.023309877595467172, 0.036986737415234], [0.03213050803702475, 0.03791920324441856], [0.06005183344725834, 0.024870964696965897], [0.07193222038979015, 0.01517636179965567], [0.07435411326657808, 0.013077015509899361], [0.08400667466383031, -0.007319212423683098], [0.07078892381534818, -0.0206217554348343], [0.06836703093856025, -0.018522409145077988], [0.068082217540429, -0.01808157648886538], [0.0620157345422152, -0.02419566504130018], [0.0588126693362227, -0.020719641868563933], [0.05785529556425468, -0.0192955081299047], [0.05665345789415225, -0.020508505521911365], [0.04914199080084621, -0.013314441132943703], [0.04203667404394113, -0.0017015123179965482], [0.03162158191558406, -0.00039567434509623115], [0.014375340249729461, -0.005499447568570125], [0.014745394325528651, -0.0070719027143585364], [0.005070920309206873, -0.02621938485143717], [-0.018256576944348242, -0.015672964712377998], [-0.04037785863210146, -0.023130744428320738], [-0.05364595677622188, -0.020843022392368432], [-0.06878490100533553, -0.04016619217453953], [-0.07247767301383833, -0.026782617891266527], [-0.07930464446495562, 0.011931796123579294], [-0.07974596706479768, 0.021241313723277453]], 'holes': []}], 'simplify_tolerance': 3.27505283457256e-05, 'sketch_entity_count': 30}
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
