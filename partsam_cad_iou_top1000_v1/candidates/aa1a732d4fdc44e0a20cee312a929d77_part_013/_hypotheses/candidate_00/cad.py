#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.15847789, -0.10524182, -0.27662488], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.033328370000000024, 'zmax': 0.033328369999999996, 'profiles': [{'outer': [[-0.07872116000000001, 0.019594970000000003], [-0.07337647000000003, 0.034573000000000007], [-0.06522307000000002, 0.0482241], [-0.054571230000000026, 0.06002657], [-0.04180261000000002, 0.06951974], [-0.027439880000000028, 0.07634305], [-0.012021210000000004, 0.0802191], [0.0038591699999999673, 0.08102164], [0.019594979999999984, 0.07872117000000001], [0.034572999999999965, 0.07337648], [0.04822409999999999, 0.06522309], [0.06002656000000001, 0.05457125], [0.06951974, 0.041802610000000004], [0.07634303999999997, 0.027439900000000003], [0.08021909999999999, 0.012021210000000004], [0.08102164, -0.003859169999999995], [0.07872117000000001, -0.01959495], [0.07337647999999997, -0.03457299000000001], [0.06522307999999999, -0.04822409000000001], [0.05457124999999996, -0.06002655999999999], [0.041811089999999995, -0.06951462000000001], [0.02743989999999996, -0.07634303999999999], [0.012021219999999999, -0.08021911], [-0.0038591800000000176, -0.08102163999999999], [-0.019594959999999995, -0.07872115], [-0.03457300000000002, -0.07337645999999999], [-0.04822410000000002, -0.06522308], [-0.06002655000000001, -0.05457123000000001], [-0.06951462000000003, -0.04181107999999999], [-0.07634305000000002, -0.02743989000000001], [-0.08021911000000001, -0.012021190000000001], [-0.08102164, 0.0038591800000000037]], 'holes': [[[-0.007758189999999998, 0.05174396], [-0.0012260600000000288, 0.008177970000000007], [0.00038898999999997796, 0.008259439999999993], [0.001997570000000004, 0.008025009999999999], [0.003528309999999979, 0.007478009999999993], [0.004916709999999991, 0.006648940000000006], [0.031109759999999986, 0.04206910999999999], [0.022303589999999984, 0.04733518], [0.012639889999999987, 0.05077974], [0.002489069999999982, 0.05226733]], [[-0.0019975500000000146, -0.008025000000000004], [-0.003528320000000029, -0.0074779999999999985], [-0.004916720000000041, -0.006648929999999997], [-0.031109760000000014, -0.04206908999999999], [-0.022303569999999995, -0.04733516], [-0.012639900000000037, -0.05077973000000001], [-0.0024890800000000324, -0.05226731], [0.007758180000000003, -0.05174394], [0.0012260499999999785, -0.008177959999999998], [-0.000388970000000044, -0.008259429999999998]], [[-0.05077972000000003, 0.01263989], [-0.052267320000000006, 0.0024890899999999994], [-0.05174395000000001, -0.007758169999999995], [-0.00817796000000004, -0.0012260500000000063], [-0.008259440000000007, 0.0003889900000000057], [-0.008025009999999999, 0.0019975599999999955], [-0.00747798999999999, 0.0035283200000000015], [-0.006648920000000003, 0.004916710000000005], [-0.042069100000000026, 0.03110976], [-0.04733517000000001, 0.022303580000000003]], [[0.008025000000000004, -0.0019975500000000007], [0.007478009999999979, -0.0035283100000000067], [0.006648939999999992, -0.004916710000000005], [0.04206911999999996, -0.031109750000000005], [0.04733518999999997, -0.02230357000000001], [0.05077973999999996, -0.01263989], [0.052267320000000006, -0.0024890800000000046], [0.05174395999999998, 0.007758189999999998], [0.008177969999999979, 0.001226060000000001], [0.008259419999999962, -0.0003889799999999971]]]}], 'simplify_tolerance': 3.240865600000001e-05, 'sketch_entity_count': 72}
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
