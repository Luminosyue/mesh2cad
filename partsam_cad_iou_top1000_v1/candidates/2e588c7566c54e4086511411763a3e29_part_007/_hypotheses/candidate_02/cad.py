#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.1181699, 0.07408419499999999, -0.047670805], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.029548405, 'zmax': 0.029548404999999996, 'profiles': [{'outer': [[-0.181111365, 1.8199999999995997e-06], [-0.180882185, 0.0036978800000000006], [-0.180227365, 0.007226579999999996], [-0.17923059500000002, 0.010464269999999998], [-0.17799010499999998, 0.013327249999999999], [-0.176618635, 0.01579370999999999], [-0.175199875, 0.017878199999999997], [-0.17379930500000002, 0.019624359999999993], [-0.172456935, 0.021072229999999997], [-0.171019985, 0.022425509999999996], [-0.169292005, 0.023840619999999993], [-0.16722208500000002, 0.025270299999999996], [-0.164777425, 0.026652679999999998], [-0.161936295, 0.027900469999999997], [-0.158727705, 0.028908149999999994], [-0.155228095, 0.029570239999999998], [-0.151561155, 0.029799419999999993], [-0.147897835, 0.029570239999999998], [-0.14439458500000002, 0.028908149999999994], [-0.141186015, 0.027900469999999997], [-0.13834848500000002, 0.026652679999999998], [-0.135903865, 0.025270299999999996], [-0.13383392500000002, 0.023840619999999993], [-0.132105945, 0.022425509999999996], [-0.130668995, 0.021072229999999997], [-0.129326635, 0.019624359999999993], [-0.127922425, 0.017878199999999997], [-0.12606540500000002, 0.014998994348910302], [-0.12606540500000002, 0.016988679999999992], [0.181111365, 0.016988679999999992], [0.181111365, -0.012392150000000018], [-0.1247306653698956, -0.012392150000000018], [-0.125135835, -0.013327240000000018], [-0.12650730500000001, -0.015793710000000016], [-0.127922425, -0.017878190000000016], [-0.129326635, -0.019624360000000007], [-0.132105945, -0.02242551000000001], [-0.13383392500000002, -0.023840620000000007], [-0.135903865, -0.025270299999999996], [-0.13834848500000002, -0.026652680000000012], [-0.141186015, -0.027900460000000016], [-0.14439458500000002, -0.02890814], [-0.147897835, -0.029570230000000003], [-0.151561155, -0.029799419999999993], [-0.155228095, -0.029570230000000003], [-0.158727705, -0.02890814], [-0.161936295, -0.027900460000000016], [-0.164777425, -0.026652680000000012], [-0.16722208500000002, -0.025270299999999996], [-0.169292005, -0.023840620000000007], [-0.171019985, -0.02242551000000001], [-0.172456935, -0.021072229999999997], [-0.17379930500000002, -0.019624360000000007], [-0.175199875, -0.017878190000000016], [-0.176618635, -0.015793710000000016], [-0.17799010499999998, -0.013327240000000018], [-0.17923059500000002, -0.010464269999999998], [-0.180227365, -0.00722658000000001], [-0.180882185, -0.003697870000000006]], 'holes': []}], 'simplify_tolerance': 7.2444546e-05, 'sketch_entity_count': 59}
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
