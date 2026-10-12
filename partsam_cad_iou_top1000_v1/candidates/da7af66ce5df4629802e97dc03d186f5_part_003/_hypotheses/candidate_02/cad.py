#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.080233345, -0.178752345, 0.007974555000000001], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.12442119500000001, 'zmax': 0.12442119500000001, 'profiles': [{'outer': [[-0.076457215, 0.013520044999999994], [-0.074249865, 0.022423035], [-0.07095723500000001, 0.030921354999999998], [-0.066652885, 0.038904625], [-0.061392025, 0.046244065], [-0.055266625, 0.05281095499999999], [-0.048368645, 0.058476494999999996], [-0.040826845, 0.063148725], [-0.032770015, 0.066735675], [-0.024345275, 0.069163765], [-0.015773385, 0.070396205], [-0.007201495000000001, 0.070451385], [-0.006723235000000001, 0.070414595], [0.0015727449999999987, 0.069310915], [0.009519214999999998, 0.067177145], [0.016950635, 0.064123635], [0.023811825000000002, 0.060242365], [0.030010814999999996, 0.055698895], [0.035400435, 0.050456434999999994], [0.037731016057802776, 0.04860291813650705], [0.040845244999999995, 0.046391215], [0.047504094999999996, 0.044036715], [0.053905415, 0.040431365], [0.05455441361753621, 0.03952158088041474], [0.05843049499999999, 0.034545095], [0.061943864999999994, 0.028787574999999996], [0.06639536500000001, 0.023692264999999997], [0.071067605, 0.018523374999999995], [0.07509602500000001, 0.012857834999999998], [0.07743213499999999, 0.006769214999999995], [0.077524115, 0.006438114999999994], [0.07756089499999999, 0.00011036500000000116], [0.077468925, -0.0002943150000000033], [0.075482305, -0.006272554999999999], [0.07209769499999999, -0.012250814999999998], [0.068032495, -0.017934754999999997], [0.064353565, -0.023894605], [0.061723135000000005, -0.030332714999999996], [0.058412095000000004, -0.03645812500000001], [0.052912114999999996, -0.041351105], [0.04923510077848818, -0.042541296611502695], [0.045517475, -0.043889555], [0.0394074383914318, -0.04622317448078918], [0.034407135, -0.051652094999999995], [0.028668014999999998, -0.05671060500000001], [0.022340264999999998, -0.06108852499999999], [0.015497455, -0.064730665], [0.008194794999999998, -0.06756343499999999], [0.0005242449999999996, -0.069476465], [-0.007422225000000001, -0.07045138499999999], [-0.015571045000000002, -0.070377805], [-0.023775035, -0.069237325], [-0.031923865, -0.06697480500000001], [-0.039851935, -0.06359018500000001], [-0.047375345, -0.059101895], [-0.054365285, -0.053565125000000005], [-0.060656245000000004, -0.047071815], [-0.066101045, -0.039713975], [-0.07057095499999999, -0.03165712500000001], [-0.074010735, -0.023066845000000002], [-0.07634685499999999, -0.014071874999999998], [-0.077524115, -0.004874575000000006], [-0.07756089499999999, 0.004377914999999996]], 'holes': []}], 'simplify_tolerance': 3.1024358e-05, 'sketch_entity_count': 72}
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
