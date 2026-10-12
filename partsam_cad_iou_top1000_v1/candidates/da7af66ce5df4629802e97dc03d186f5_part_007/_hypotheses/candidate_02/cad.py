#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0802229, -0.178752345, 0.007974555000000001], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.12442119500000001, 'zmax': 0.12442119500000001, 'profiles': [{'outer': [[-0.07634685499999999, 0.014071879999999995], [-0.074010735, 0.02306685], [-0.07057095499999999, 0.031657130000000006], [-0.066101045, 0.039713990000000005], [-0.060656245000000004, 0.047071829999999995], [-0.054365285, 0.05356512000000001], [-0.047375345, 0.059101909999999994], [-0.039851935, 0.0635902], [-0.031923865, 0.06697481000000001], [-0.023775035, 0.06923736000000001], [-0.015571045000000002, 0.07037782], [-0.007422225000000001, 0.07045138], [0.0005242449999999996, 0.06947646], [0.008194794999999998, 0.06756343], [0.015497455, 0.06473066000000001], [0.022340264999999998, 0.06108851999999999], [0.028668014999999998, 0.05671062], [0.034407135, 0.05165209], [0.039403031202216526, 0.04622795444643824], [0.045517475, 0.04387115], [0.04900218518066777, 0.04261667272342502], [0.052912114999999996, 0.04135109000000001], [0.058412095000000004, 0.036458130000000005], [0.061723135000000005, 0.030332730000000002], [0.064353565, 0.023894609999999997], [0.068032495, 0.017934759999999994], [0.07209769499999999, 0.012250819999999996], [0.075482305, 0.006272570000000005], [0.077468925, 0.0002943200000000007], [0.07756089499999999, -0.00011037999999999326], [0.077524115, -0.0064381200000000055], [0.07743213499999999, -0.006769209999999998], [0.07509602500000001, -0.012857839999999995], [0.071067605, -0.01852339], [0.06639536500000001, -0.02369227], [0.061943864999999994, -0.02878758], [0.05843049499999999, -0.03454509], [0.05468043128072793, -0.039359790928980065], [0.053905415, -0.04044977], [0.047504094999999996, -0.04403671], [0.040845244999999995, -0.04637282], [0.03783450289471587, -0.048520618680733214], [0.035400435, -0.05045643], [0.030010814999999996, -0.055698899999999996], [0.023811825000000002, -0.06024237], [0.016950635, -0.06412364], [0.009519214999999998, -0.06717714], [0.0015727449999999987, -0.06931091], [-0.007201495000000001, -0.07045138], [-0.015773385, -0.07039619999999999], [-0.024345275, -0.06916376], [-0.032770015, -0.06673567], [-0.040826845, -0.06314871999999999], [-0.048368645, -0.05847649], [-0.055266625, -0.052810949999999995], [-0.061392025, -0.04624407], [-0.066652885, -0.03890462], [-0.07095723500000001, -0.030921360000000002], [-0.074249865, -0.022423039999999998], [-0.076457215, -0.013520039999999997], [-0.07756089499999999, -0.004377930000000002], [-0.077524115, 0.004874580000000003]], 'holes': []}], 'simplify_tolerance': 3.1024358e-05, 'sketch_entity_count': 62}
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
