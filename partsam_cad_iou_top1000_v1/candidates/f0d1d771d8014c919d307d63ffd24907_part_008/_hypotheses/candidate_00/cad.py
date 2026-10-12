#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.07944230000000001, 0.17440075500000002, -0.004469174999999999], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.04995650500000001, 'zmax': 0.049956504999999984, 'profiles': [{'outer': [[-0.124515815, -0.026637610000000006], [-0.12272692500000001, -0.024273680000000006], [-0.11751482499999999, -0.01955516000000001], [-0.10258529499999999, -0.006883510000000009], [-0.094723005, -0.0002832000000000112], [-0.086573595, 0.006424759999999988], [-0.078048745, 0.012945499999999999], [-0.069170535, 0.018904479999999987], [-0.060292325, 0.02399280999999999], [-0.051922075, 0.02792489999999999], [-0.044722325, 0.030752279999999993], [-0.039289395, 0.03261064999999999], [-0.035093225, 0.033818369999999986], [-0.031647945000000004, 0.03466564999999999], [-0.027760975, 0.03548950999999999], [-0.023785655000000003, 0.03610740999999999], [-0.006139655000000001, 0.03799855999999999], [-0.003069835000000001, 0.038241979999999995], [-5.000000000837668e-09, 0.03834496], [0.003069834999999999, 0.038241979999999995], [0.006161744999999999, 0.03799855999999999], [0.023785655, 0.03610740999999999], [0.027760975, 0.03548950999999999], [0.031647955, 0.03466564999999999], [0.035115314999999994, 0.033818369999999986], [0.039289405, 0.03261064999999999], [0.044722345, 0.030752279999999993], [0.051922085, 0.02792489999999999], [0.060292334999999996, 0.02399280999999999], [0.069170555, 0.018904479999999987], [0.07804876499999999, 0.012945499999999999], [0.08657361499999999, 0.006434119999999988], [0.102607385, -0.006883510000000009], [0.11753691499999999, -0.01956452000000001], [0.122748995, -0.024278360000000006], [0.124515815, -0.026632930000000006], [0.12383117499999999, -0.028074700000000008], [0.122064375, -0.03016714000000001], [0.11590261499999999, -0.037404070000000005], [0.11455543500000001, -0.038344960000000004], [0.11188314499999999, -0.037024900000000006], [0.106361865, -0.03264811000000001], [0.099051695, -0.026403560000000006], [0.083746715, -0.012982940000000012], [0.07579607499999999, -0.006143910000000002], [0.067558335, 0.0002972499999999989], [0.059033495, 0.005984749999999997], [0.050574895, 0.010712619999999992], [0.042602175, 0.014382579999999992], [0.035777875, 0.016980569999999987], [0.030609954999999998, 0.018595539999999994], [0.026656725, 0.01960664999999999], [0.016188385, 0.021998679999999993], [0.008348165, 0.023117449999999998], [0.004174084999999999, 0.02349193999999999], [-5.000000000837668e-09, 0.023683859999999987], [-0.004174075000000001, 0.02349193999999999], [-0.008348165000000001, 0.023117449999999998], [-0.016188375, 0.021998679999999993], [-0.026634635, 0.01960664999999999], [-0.030609955, 0.018595539999999994], [-0.035777865, 0.016980569999999987], [-0.042580075, 0.014382579999999992], [-0.050552795000000005, 0.010712619999999992], [-0.059033474999999995, 0.005984749999999997], [-0.067558325, 0.0002972499999999989], [-0.07577398499999999, -0.006143910000000002], [-0.083746715, -0.012982940000000012], [-0.099051685, -0.026403560000000006], [-0.10636184500000001, -0.03265279000000001], [-0.111883125, -0.037024900000000006], [-0.11455542499999999, -0.038344960000000004], [-0.11590261500000001, -0.037404070000000005], [-0.12206436500000001, -0.03016714000000001], [-0.12383116500000002, -0.028074700000000008]], 'holes': []}], 'simplify_tolerance': 4.9806326e-05, 'sketch_entity_count': 108}
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
