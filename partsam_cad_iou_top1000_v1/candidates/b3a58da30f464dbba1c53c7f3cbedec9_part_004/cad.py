#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.18525392000000002, -0.04644949, 0.149900455], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.004295289999999979, 'zmax': 0.004295290000000007, 'profiles': [{'outer': [[-0.019314825000000008, -0.003667729999999994], [-0.021267235000000023, -0.0009343699999999969], [-0.029662545000000012, 0.010166430000000004], [-0.03437620500000002, 0.016135200000000002], [-0.039815035, 0.023275410000000003], [-0.044193995000000014, 0.031029230000000005], [-0.04533753500000001, 0.03981504], [-0.043050435000000026, 0.04834982], [-0.037639485, 0.05537847], [-0.029969335000000014, 0.05981319], [-0.021211425000000006, 0.060956750000000004], [-0.012648755000000012, 0.05866964], [-0.005620105000000014, 0.05328659], [-0.0013806150000000017, 0.04675999], [0.0027751949999999803, 0.039870810000000007], [0.006540544999999981, 0.03808576], [0.019761084999999984, 0.04126537], [0.045337534999999984, -0.0030262499999999942], [0.03596600499999998, -0.012871919999999995], [0.03563129499999999, -0.017027739999999993], [0.03950820499999999, -0.024084279999999993], [0.043050414999999995, -0.03100136], [0.04419396499999999, -0.039787170000000004], [0.04190686499999999, -0.04834983], [0.03652381499999999, -0.05537846999999999], [0.02885367499999998, -0.05981321], [0.020067854999999996, -0.06095675], [0.011505194999999996, -0.05866965999999999], [0.004476554999999993, -0.05325872], [-4.18550000000073e-05, -0.04561645999999999], [-0.0035003950000000172, -0.0373327], [-0.00631743500000001, -0.030276160000000003], [-0.011728375000000013, -0.017473999999999996], [-0.013122945000000025, -0.014405939999999999], [-0.01613521500000001, -0.008994999999999996]], 'holes': [[[-0.018199145, 0.04742939], [-0.022020275000000006, 0.048461370000000004], [-0.025952975000000017, 0.047931440000000006], [-0.029383625000000024, 0.04595115], [-0.031782315000000005, 0.04279941], [-0.032814275000000004, 0.038978290000000006], [-0.032312225, 0.03504559], [-0.030331935000000004, 0.03161495], [-0.027180205000000013, 0.029216290000000002], [-0.023359075000000007, 0.028184300000000002], [-0.019426405000000008, 0.028686350000000003], [-0.01599573500000001, 0.030694520000000003], [-0.013569185000000011, 0.03381837], [-0.012537205000000023, 0.037639500000000006], [-0.013067135000000007, 0.04157219], [-0.015047425000000003, 0.04500284]], [[0.018617515, -0.010389579999999995], [0.03691431499999999, -0.00029287999999999537], [0.017920254999999996, 0.03261903000000001], [1.3954999999982176e-05, 0.021825040000000004], [0.0009064749999999899, 0.017557650000000005], [0.0071820349999999755, 0.004476570000000006], [0.015354234999999994, -0.007488869999999995]], [[0.01485218499999999, -0.03066665999999999], [0.012453514999999998, -0.03381839], [0.011421524999999988, -0.037639509999999994], [0.011923574999999992, -0.04157220999999999], [0.013903854999999993, -0.04500286], [0.017055584999999984, -0.047401519999999996], [0.020876724999999985, -0.0484335], [0.024809424999999996, -0.047931449999999994], [0.028240054999999986, -0.04595116999999999], [0.030666614999999994, -0.04279944], [0.03169860499999999, -0.038978309999999995], [0.031168674999999993, -0.03504561999999999], [0.029188384999999983, -0.03161497], [0.026036644999999983, -0.02918840999999999], [0.02221551499999999, -0.028156419999999995], [0.01828281499999998, -0.02868636]]]}], 'simplify_tolerance': 2.4382700000000003e-05, 'sketch_entity_count': 74}
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
