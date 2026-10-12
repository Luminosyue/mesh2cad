#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.18525392000000002, -0.05608608, -0.120618605], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.004295289999999979, 'zmax': 0.004295290000000007, 'profiles': [{'outer': [[-0.066507135, -0.012383769999999995], [-0.066507135, -0.003514299999999998], [-0.063132255, 0.0046579000000000065], [-0.056856685000000004, 0.01093347], [-0.048684505, 0.014308330000000001], [-0.040902795000000006, 0.014726700000000002], [-0.032870065000000004, 0.014866150000000002], [-0.029411505000000004, 0.017236930000000004], [-0.025590365000000004, 0.030290110000000002], [0.025562514999999994, 0.030290100000000004], [0.029411544999999997, 0.01723691], [0.032870074999999985, 0.014866130000000005], [0.04090282499999999, 0.014726670000000004], [0.048656644999999984, 0.014308300000000003], [0.056856695, 0.010933430000000001], [0.063104395, 0.004657860000000007], [0.06650713500000001, -0.003514329999999996], [0.06650713500000001, -0.012383819999999997], [0.063104395, -0.020556009999999993], [0.056856685000000004, -0.02683158], [0.04865663499999999, -0.030206439999999994], [0.039759265, -0.030290110000000002], [0.030861874999999997, -0.029174449999999998], [0.023331205000000008, -0.028058789999999993], [0.009552815000000006, -0.02635740999999999], [0.0062058450000000015, -0.026022709999999998], [-1.3945000000001317e-05, -0.025939029999999995], [-0.006205835000000007, -0.026022709999999998], [-0.009552815000000006, -0.026357399999999996], [-0.023359065, -0.02805876999999999], [-0.030889775000000008, -0.029174429999999994], [-0.039787125000000007, -0.03029009], [-0.048684505, -0.030206409999999996], [-0.056856695, -0.026831539999999994], [-0.063132265, -0.02055597]], 'holes': [[[-0.038587805, 0.0005020700000000003], [-0.042269465000000006, 0.0020082000000000017], [-0.046230045, 0.0020082000000000017], [-0.04988382500000001, 0.0005020700000000003], [-0.052700855000000005, -0.0023149699999999995], [-0.05420699500000001, -0.005968749999999995], [-0.054207005, -0.009929329999999993], [-0.052700865, -0.013583110000000002], [-0.04988382500000001, -0.016400149999999995], [-0.046230045, -0.01790627999999999], [-0.042269465000000006, -0.01790627999999999], [-0.038587805, -0.016400149999999995], [-0.035798655, -0.013583110000000002], [-0.03429251500000001, -0.009929329999999993], [-0.034292505, -0.005968749999999995], [-0.035798645000000004, -0.0023149699999999995]], [[-1.3935000000006581e-05, 0.0010041000000000008], [0.014461715, 0.002091860000000001], [0.018617535000000004, 0.003458540000000003], [0.018980154999999985, 0.024377120000000002], [-0.01900800500000001, 0.024377130000000004], [-0.018617535000000004, 0.0034585500000000047], [-0.014461705000000005, 0.0020918700000000026]], [[0.034264644999999996, -0.009929359999999991], [0.035798645000000004, -0.01358314], [0.038587835, -0.01640017], [0.042241605, -0.01790631], [0.04620218499999999, -0.01790631], [0.049883835, -0.016400179999999993], [0.05267300500000001, -0.01358314], [0.05420700499999999, -0.009929359999999991], [0.05420700499999999, -0.00596878], [0.05267300500000001, -0.0023149999999999976], [0.049883835, 0.0005020400000000022], [0.04620218499999999, 0.0020081800000000052], [0.042241605, 0.0020081800000000052], [0.038587835, 0.0005020400000000022], [0.035798645000000004, -0.002314989999999996], [0.034264644999999996, -0.005968769999999998]]]}], 'simplify_tolerance': 2.6602854e-05, 'sketch_entity_count': 74}
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
