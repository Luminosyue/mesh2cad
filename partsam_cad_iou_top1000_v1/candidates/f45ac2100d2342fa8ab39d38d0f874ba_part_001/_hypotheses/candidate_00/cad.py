#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.107031875, 0.336114405, -1.500000000598245e-08], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.036662315, 'zmax': 0.036662315, 'profiles': [{'outer': [[-0.095726235, 0.06821212500000001], [-0.069539635, 0.09389829500000002], [-0.06916409500000001, 0.09417498499999999], [-0.03636223500000001, 0.110567095], [-7.225000000005982e-06, 0.116220025], [0.036362244999999994, 0.110567095], [0.04428770919923968, 0.10660649274875506], [0.04540044499999999, 0.10881012499999998], [0.045783464999999995, 0.10937279500000002], [0.04631847499999999, 0.10978907500000001], [0.04695698499999999, 0.11002192500000002], [0.047636664999999995, 0.11004349499999999], [0.048288054999999996, 0.10985517499999997], [0.04885184499999999, 0.10947436500000002], [0.04926818499999999, 0.10893947500000001], [0.04950008499999999, 0.108298895], [0.049522664999999993, 0.10762149500000001], [0.049333304999999994, 0.10696810499999998], [0.04830102142806596, 0.10460091515117242], [0.069164095, 0.09417498499999999], [0.06953963499999999, 0.09389829500000002], [0.095726225, 0.06821212500000001], [0.11252436499999999, 0.035867095000000015], [0.118316325, 8.494999999997255e-06], [0.11252436499999999, -0.03586429499999999], [0.095726225, -0.06820931499999999], [0.06953963499999999, -0.09389546500000001], [0.069164095, -0.09417499500000001], [0.036362244999999994, -0.110567095], [-7.225000000005982e-06, -0.116220025], [-0.03636223500000001, -0.110567095], [-0.06916409500000001, -0.09417499500000001], [-0.069539635, -0.09389546500000001], [-0.095726235, -0.06820931499999999], [-0.112524365, -0.03586429499999999], [-0.118316325, 8.494999999997255e-06], [-0.112524365, 0.035867095000000015]], 'holes': [[[-7.225000000005982e-06, 0.08972260500000001], [-0.028519255000000007, 0.085288105], [-0.054058908688230115, 0.07251614359665595], [-0.074132765, 0.052825924999999996], [-0.087146625, 0.02777731499999997], [-0.091624195, 8.494999999997255e-06], [-0.087146625, -0.027774515], [-0.074132765, -0.052823125000000026], [-0.054053023189882546, -0.07251911661541302], [-0.028519255000000007, -0.085288105], [-7.225000000005982e-06, -0.089722635], [0.028519264999999995, -0.085288105], [0.054053012788969824, -0.07251912681755066], [0.07413276499999999, -0.052823125000000026], [0.087146615, -0.027774515], [0.09162419499999999, 8.494999999997255e-06], [0.087146615, 0.02777731499999997], [0.07413276499999999, 0.052825924999999996], [0.054058898287267905, 0.07251615379884213], [0.03724449440803247, 0.08092476105669237], [0.03519755499999999, 0.07669562499999999], [0.034461744999999995, 0.07547733499999998], [0.03392673499999999, 0.07506108499999997], [0.033287084999999994, 0.074831335], [0.032608544999999996, 0.07480663500000001], [0.03195502499999999, 0.074995965], [0.03139335499999999, 0.07537579499999997], [0.030974894999999995, 0.075911705], [0.030745114999999993, 0.076551235], [0.030722544999999993, 0.07722863499999999], [0.03126468499999999, 0.07874336500000001], [0.03317725401024584, 0.08295872118836761], [0.028519264999999995, 0.085288105]]]}], 'simplify_tolerance': 4.7326530000000004e-05, 'sketch_entity_count': 79}
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
