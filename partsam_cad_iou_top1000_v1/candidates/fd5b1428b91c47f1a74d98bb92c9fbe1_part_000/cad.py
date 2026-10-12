#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [3.355000000010433e-06, 0.01514380999999998, -0.19030752], 'basis': [[0.0, 1.0, -3.2140456611263613e-13], [-0.9949401504099087, -3.229131874168316e-14, -0.10046938390528863], [-0.10046938390528863, 3.197783073505376e-13, 0.9949401504099087]], 'axis': [-3.2140456611263613e-13, -0.10046938390528863, 0.9949401504099087], 'zmin': -3.3890582983638024e-05, 'zmax': 1.7838381088609133e-05, 'profiles': [{'outer': [[-0.3746242414180809, -0.272143205], [-0.42300770079520333, -0.18834631500000001], [-0.4529072174324857, -0.09628211500000003], [-0.4630306275421266, -5.00000000469952e-09], [-0.4529072174324857, 0.09628211499999997], [-0.42300770079520333, 0.18834626499999998], [-0.3746242414180809, 0.272143225], [-0.3098445782271913, 0.344073635], [-0.23149990683596317, 0.400988055], [-0.14309363015533405, 0.440355735], [-0.048414225509702896, 0.460489495], [0.048414157873279996, 0.460489495], [0.1430936291506402, 0.440355735], [0.2314999356794738, 0.400988055], [0.30984452254955763, 0.344073635], [0.37462434784741594, 0.272143225], [0.4230077038092848, 0.18834626499999998], [0.4529129872234546, 0.09628211499999999], [0.4630306275421266, -5.000000016166194e-09], [0.4529129872234546, -0.09628211500000002], [0.4230077038092848, -0.18834631500000001], [0.37462434784741594, -0.272143205], [0.30984452254955763, -0.34407358499999996], [0.2314999356794738, -0.40098799500000004], [0.1430936291506402, -0.440355705], [0.048414157873279996, -0.460489495], [-0.048414225509702896, -0.460489495], [-0.14309363015533405, -0.440355705], [-0.23149990683596317, -0.40098799500000004], [-0.3098445782271913, -0.34407358499999996]], 'holes': []}], 'simplify_tolerance': 0.00018521225101685064, 'sketch_entity_count': 30}
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
