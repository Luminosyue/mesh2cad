#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.004488505000000004, 0.045208614999999994, -0.047659150000000004], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.19797648499999998, 'zmax': 0.19797648499999998, 'profiles': [{'outer': [[-0.09938097999999998, -0.03228915499999999], [-0.10162863999999999, -0.024386044999999995], [-0.10322377999999999, -0.016337924999999996], [-0.10419050999999999, -0.008193124999999996], [-0.10450471, 5.000000003439753e-09], [-0.10419050999999999, 0.008193125000000004], [-0.10322377999999999, 0.016362095000000004], [-0.10162863999999999, 0.024410215000000002], [-0.09938097999999998, 0.032289155], [-0.09655326, 0.039998915], [-0.09312133, 0.047442825], [-0.08910934999999998, 0.054596705], [-0.08454150999999999, 0.061436395000000005], [-0.07946610999999998, 0.067865225], [-0.07388317999999999, 0.07390735500000001], [-0.06786522, 0.079466125], [-0.06143639, 0.084541515], [-0.05459669999999999, 0.089109375], [-0.04744281999999999, 0.09312134500000001], [-0.03999890999999999, 0.09655327500000001], [-0.032289149999999996, 0.099405165], [-0.02438603999999999, 0.101628665], [-0.01633792, 0.10322379500000001], [-0.008193119999999998, 0.104190535], [6.938893903907228e-18, 0.104504715], [0.008193130000000007, 0.104190535], [0.016362090000000003, 0.10322379500000001], [0.024410220000000003, 0.101628665], [0.03228915, 0.099405165], [0.03999892000000001, 0.09655327500000001], [0.047442830000000005, 0.09312134500000001], [0.05459671000000001, 0.089109375], [0.06143639000000001, 0.084541515], [0.06786523, 0.079466125], [0.07390735000000001, 0.07390735500000001], [0.07946613, 0.067865225], [0.08454151000000001, 0.061436395000000005], [0.08910937000000001, 0.054596705], [0.09312133, 0.047442825], [0.09655326, 0.039998915], [0.09940516, 0.032289155], [0.10162865, 0.024410215000000002], [0.10322378, 0.016362095000000004], [0.10419053, 0.008193125000000004], [0.10450471, 5.000000003439753e-09], [0.10419053, -0.008193124999999996], [0.10322378, -0.016337924999999996], [0.10162865, -0.024386044999999995], [0.09940516, -0.03228915499999999], [0.09655326, -0.039998914999999996], [0.09312133, -0.047442824999999994], [0.08910937000000001, -0.054596704999999995], [0.08454151000000001, -0.06143639499999999], [0.07946613, -0.067865235], [0.07390735000000001, -0.073883195], [0.06786523, -0.07946611499999999], [0.06143639000000001, -0.084541515], [0.05459671000000001, -0.089109365], [0.047442830000000005, -0.093121345], [0.03999892000000001, -0.096553275], [0.03228915, -0.099380995], [0.024410220000000003, -0.10162866499999999], [0.016362090000000003, -0.103223785], [0.008193130000000007, -0.10419052499999999], [6.938893903907228e-18, -0.104504715], [-0.008193119999999998, -0.10419052499999999], [-0.01633792, -0.103223785], [-0.02438603999999999, -0.10162866499999999], [-0.032289149999999996, -0.099380995], [-0.03999890999999999, -0.096553275], [-0.04744281999999999, -0.093121345], [-0.05459669999999999, -0.089109365], [-0.06143639, -0.084541515], [-0.06786522, -0.07946611499999999], [-0.07388317999999999, -0.073883195], [-0.07946610999999998, -0.067865235], [-0.08454150999999999, -0.06143639499999999], [-0.08910934999999998, -0.054596704999999995], [-0.09312133, -0.047442824999999994], [-0.09655326, -0.039998914999999996]], 'holes': []}], 'simplify_tolerance': 4.1801886e-05, 'sketch_entity_count': 80}
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
