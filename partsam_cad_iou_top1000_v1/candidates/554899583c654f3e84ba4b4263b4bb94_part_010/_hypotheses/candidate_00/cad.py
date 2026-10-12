#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.07296532, -0.197613645, 0.042042235], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.024751449999999994, 'zmax': 0.02475145, 'profiles': [{'outer': [[-0.029872835, -0.024773985], [-0.028724744999999996, -0.014463685000000004], [-0.027081395000000008, -0.0058867549999999935], [-0.021588575, 0.016872395000000012], [-0.020192865000000004, 0.022095074999999992], [-0.020057795000000003, 0.025831985000000002], [-0.022151365000000006, 0.028263225000000003], [-0.024447545, 0.031212254999999994], [-0.024965315000000002, 0.03636740499999999], [-0.024560105, 0.042490534999999996], [-0.024087355000000005, 0.04825349500000001], [-0.023659645000000007, 0.052890875000000004], [-0.023254435000000004, 0.056740345], [-0.022196385, 0.059959504999999996], [-0.019742625, 0.062278185000000014], [-0.014632515000000006, 0.063133635], [-0.007541375000000003, 0.063538825], [0.0006303149999999993, 0.065272215], [0.009229724999999994, 0.066420325], [0.017671564999999997, 0.065137155], [0.024717674999999998, 0.062908505], [0.029017374999999998, 0.061175115], [0.032123975, 0.05887893499999999], [0.032078945, 0.056740345], [0.031831324999999994, 0.055254584999999995], [0.030930854999999997, 0.051450155], [0.030187984999999997, 0.046542635], [0.029512634999999995, 0.04131995499999999], [0.028837295, 0.03661503500000002], [0.028454595, 0.03105466500000001], [0.028724725, 0.023265675000000013], [0.029580165, 0.015949414999999995], [0.030953374999999998, 0.011852315000000002], [0.031178485, 0.010569145000000002], [0.030795794999999997, 0.008925824999999998], [0.027981844999999998, 0.005571605000000007], [0.024064834999999996, 0.0012268750000000161], [0.020372944999999996, -0.0034330149999999837], [0.016523474999999996, -0.008768255000000003], [0.012111204999999996, -0.015161544999999998], [0.007766474999999995, -0.022500304999999998], [0.004104809643360302, -0.03050747333199252], [0.001148085, -0.03870860500000001], [-0.0011255850000000053, -0.046835285000000004], [-0.003354235000000004, -0.05385888500000002], [-0.006348255000000004, -0.05905906500000002], [-0.009792525000000003, -0.06266091499999998], [-0.010490385000000005, -0.06315616499999999], [-0.014159765000000005, -0.065474845], [-0.017874165000000004, -0.066420325], [-0.021633595000000005, -0.06590257500000002], [-0.025167915, -0.06482199500000002], [-0.028297025000000003, -0.064101615], [-0.029062415000000008, -0.063786485], [-0.03126854500000001, -0.06243578500000002], [-0.032123975, -0.05946425500000002], [-0.032056445, -0.05406148500000002], [-0.031561185000000005, -0.04568718499999999], [-0.030773295000000006, -0.03530935499999999]], 'holes': []}], 'simplify_tolerance': 2.6568130000000003e-05, 'sketch_entity_count': 59}
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
