#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.00867702, -0.134814235, 0.32794611], 'basis': [[-0.44512612520624595, 0.049807240708067774, 0.8940816357760192], [0.0, 0.9984519277351878, -0.05562147069151852], [-0.8954678847724654, -0.024758569727188415, -0.44443703779747085]], 'axis': [0.8940816357760192, -0.05562147069151852, -0.44443703779747085], 'zmin': -0.01927311554573931, 'zmax': 0.019263532287393637, 'profiles': [{'outer': [[-0.032371116666956364, -0.11922955651700493], [-0.0058753536879078035, 0.12338075658702254], [-0.0030318370105058326, 0.1422414876748315], [0.0021859379391384695, 0.1532085249898189], [0.005215812831044321, 0.15508647573834575], [0.017312198334295866, 0.15849319909454568], [0.028363478817968232, 0.15259201407687523], [0.03090941519845541, 0.15005173475801994], [0.033611270173102926, 0.1382479583136339], [0.032371058487622055, 0.11922959546764025], [0.0058753268238712734, -0.12338071739170252], [0.0030318056952080507, -0.14224143799691977], [-0.0021859737578538417, -0.15320848604208465], [-0.0052158486497596935, -0.15508643679061143], [-0.017312225198332393, -0.15849319983730276], [-0.028363505682004762, -0.15259199485059374], [-0.030909415198455414, -0.15005171478898138], [-0.03361127017310288, -0.13824790839103754]], 'holes': []}], 'simplify_tolerance': 6.33972797863697e-05, 'sketch_entity_count': 21}
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
