#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.321908505, -0.23151454999999999, -0.11216108000000001], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.06530925500000001, 'zmax': 0.06530925500000001, 'profiles': [{'outer': [[-0.15056627, 0.05297792999999998], [-0.15041586, 0.06630006999999999], [-0.14767993000000001, 0.07937111999999999], [-0.14245762, 0.09166753999999999], [-0.13497531000000001, 0.10273501999999998], [-0.12549126000000002, 0.11213661999999999], [-0.11438233, 0.11952047999999998], [-0.1020964, 0.12459397999999998], [-0.08906983000000002, 0.12716135], [-0.07582447, 0.12713515999999997], [-0.06286343000000001, 0.12450031999999998], [-0.05068569000000001, 0.11936315999999998], [-0.045213876356522444, 0.11570723571951497], [0.15056627, 0.00924760999999999], [0.09937562999999998, -0.08489236], [0.09913690628281514, -0.08476254887995742], [0.07608163999999999, -0.12716135], [0.01714666999999999, -0.09511418999999999], [0.04020192424532006, -0.05271539362368775], [-0.05369931323054271, -0.0016545901397689042], [-0.06393760000000001, -0.005882520000000002], [-0.07696416, -0.008449890000000015], [-0.09020953000000001, -0.008423710000000001], [-0.10317057000000002, -0.005788860000000007], [-0.11580986000000001, -0.00040072000000002106], [-0.12674137000000002, 0.007028269999999975], [-0.13599834, 0.016474939999999993], [-0.14322026000000002, 0.027578269999999988], [-0.14814633000000002, 0.03990779]], 'holes': []}], 'simplify_tolerance': 6.0226508000000005e-05, 'sketch_entity_count': 29}
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
