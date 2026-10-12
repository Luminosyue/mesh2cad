#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.262877405, -0.35472033999999997, -0.18048930000000002], 'basis': [[0.0032232335650140844, -0.20608276521850097, 0.978529255896461], [0.0, 0.9785343390210768, 0.2060838357479414], [-0.9999948053692006, -0.0006642563365896141, 0.003154044726051606]], 'axis': [0.978529255896461, 0.2060838357479414, 0.003154044726051606], 'zmin': -0.0016025745552873203, 'zmax': 0.00256089479664863, 'profiles': [{'outer': [[-0.013145447728734735, 0.002933882864880598], [-0.012383450041411694, 0.005446158987300637], [-0.011147074502309269, 0.007762549399341835], [-0.009483722298736428, 0.009794644616572494], [-0.007453828611590342, 0.011460724919535856], [-0.0051391028869520764, 0.012700152973888877], [-0.0026278431427555976, 0.013465499549811851], [-1.3227331428807732e-05, 0.013723981590036037], [0.0026000996998704205, 0.01346897226201185], [0.005112373860134453, 0.012706962617651116], [0.007428754078485637, 0.011470610820746165], [0.00946085929064535, 0.009807228740307155], [0.011126919695215875, 0.007777351300534183], [0.01236634139189157, 0.005462599278490722], [0.013131675770601143, 0.0029513377013438108], [0.013390161405215534, 0.0003366960652432006], [0.013135148450211753, -0.0022766602099521557], [0.012373150762888684, -0.004788926547028808], [0.011136805320327438, -0.007105332906968645], [0.009473443020109515, -0.009137421948358924], [0.007443549332963429, -0.010803502251322287], [0.005128833640505548, -0.012042951930547165], [0.0026175638641287124, -0.012808276881598281], [4.578044334676552e-06, -0.01306675783908464], [-0.002610388978445354, -0.012811749600440844], [-0.005122663106477079, -0.012049761587594531], [-0.00743903335711255, -0.010813388152532596], [-0.00947113866596927, -0.009150029245640788], [-0.011137188973894712, -0.007120128625678039], [-0.012376640573717575, -0.004805373020701847], [-0.013141975049124125, -0.0022941150464153683], [-0.013400439523478337, 0.0003188769728890853]], 'holes': []}], 'simplify_tolerance': 5.3581478858241355e-06, 'sketch_entity_count': 32}
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
