#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.00035132499999999955, -0.195476525, -0.159686355], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.175915775, 'zmax': 0.175915775, 'profiles': [{'outer': [[-0.02438816499999999, 0.0018986050000000254], [-0.02470460499999999, 0.003978055000000008], [-0.02470460499999999, 0.004294495000000009], [-0.02371838586860243, 0.005517418591317651], [-0.023932025128129114, 0.006627313615141349], [-0.025292275000000003, 0.010171155000000015], [-0.024116935000000006, 0.022873795000000002], [-0.018647114999999992, 0.03376822500000001], [-0.010238945, 0.041001045000000014], [-0.00038423500000001054, 0.043532525000000016], [0.009470465000000011, 0.041001025000000024], [0.017833395000000002, 0.03376821500000002], [0.023348435, 0.022873785000000008], [0.025292275000000003, 0.010171135000000026], [0.023348425000000006, -0.002667104999999975], [0.017833385000000007, -0.013471134999999995], [0.009470444999999994, -0.02079436499999998], [0.008430725, -0.04032296499999999], [0.005673234999999999, -0.04032296499999999], [0.005808845000000007, -0.043035274999999984], [0.005673234999999999, -0.043306504999999995], [-0.0052212050000000065, -0.04353252499999999], [-0.005284698617068352, -0.04054898499999998], [-0.00843074499999999, -0.04054898499999998], [-0.00874718499999999, -0.03928325499999999], [-0.010238954999999994, -0.020794354999999987], [-0.014714284999999994, -0.013471134999999995], [-0.019912855000000007, -0.005786264999999985], [-0.022986845000000006, -0.0017629949999999894], [-0.024116935000000006, 0.000542455000000025], [-0.024116935000000006, 0.0009945150000000014], [-0.022879207146753355, 0.001157731661384804], [-0.022979896918423035, 0.0016808334394648934]], 'holes': [[[-0.009786884999999995, 0.025043625000000014], [-0.012770444999999991, 0.017268355000000013], [-0.013358115000000004, 0.007956095000000024], [-0.012454015000000013, 0.004656125000000011], [-0.012996504999999992, 0.0036164150000000117], [-0.012906074999999989, 0.002034235000000023], [-0.010600625000000002, 0.0015369750000000237], [-0.012770444999999991, 0.0010849150000000196], [-0.012227965000000007, -0.0004972549999999742], [-0.010510204999999995, -0.003616414999999984], [-0.009109511450405438, -0.006512731617444586], [-0.007617084999999996, -0.007504054999999982], [-0.007450214016910542, -0.008091724999999994], [0.006659939868159801, -0.008091724999999994], [0.006848574999999996, -0.007504054999999982], [0.011119239466380427, -0.004603824113380574], [0.012318384999999987, -0.0013109549999999748], [0.013358115000000004, 0.007956085000000002], [0.012318384999999987, 0.017268335000000024], [0.009470465000000011, 0.02504361500000002], [0.007645358898768415, 0.027163709123479114], [0.006848594999999985, 0.02771074500000001], [-0.00038423500000001054, 0.029202515000000012], [-0.007548670023845429, 0.027724851452602672]]]}], 'simplify_tolerance': 1.741301e-05, 'sketch_entity_count': 60}
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
