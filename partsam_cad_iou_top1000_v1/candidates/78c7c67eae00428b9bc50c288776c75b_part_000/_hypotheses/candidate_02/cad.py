#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.058312829999999996, 0.09434703, -0.010599255000000002], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.048746695, 'zmax': 0.048746695, 'profiles': [{'outer': [[-0.07439752999999999, -0.021135369999999994], [-0.07429638, -0.020553539999999995], [-0.07052711, -0.005552619999999994], [-0.07518174999999999, 0.011800909999999998], [-0.07748368, 0.028496720000000003], [-0.07895091000000001, 0.04109446], [-0.07915327, 0.050100080000000005], [-0.07626948, 0.05794205000000001], [-0.07009712000000001, 0.06596110000000001], [-0.06053497999999999, 0.07167814000000002], [-0.05425320664220223, 0.0741933755508857], [-0.04816487, 0.07681336000000001], [-0.036427230000000005, 0.07979837], [-0.025397870000000003, 0.08126557], [-0.013204839999999995, 0.08101262], [0.0026561299999999927, 0.07709164], [0.022969340000000005, 0.07127339], [0.04209366, 0.06080057], [0.055121449999999995, 0.05002419000000001], [0.06334284, 0.04013319], [0.06878164, 0.0316588], [0.07260141, 0.02363975], [0.07535878, 0.01529185000000001], [0.07743308, 0.005577930000000009], [0.07915327, -0.004338369999999994], [0.07685128, -0.015823059999999993], [0.07472637, -0.024423939999999998], [0.07184251999999999, -0.03241769], [0.06776974, -0.040259649999999994], [0.0621033, -0.048152219999999996], [0.053704829999999995, -0.05634834], [0.04049996, -0.06424091], [0.021021520000000002, -0.07152634999999999], [0.002251420000000004, -0.07769873999999999], [-0.01082698, -0.08073433999999999], [-0.022665829999999998, -0.08126557], [-0.03339168000000001, -0.08022839999999999], [-0.04437044000000001, -0.07749637], [-0.05706933, -0.07360068], [-0.06690976000000001, -0.06912317], [-0.07343629000000002, -0.062217169999999995], [-0.07667425, -0.055437669999999994], [-0.07687661000000001, -0.04746921], [-0.0762370266656727, -0.03998930734664381], [-0.07596597, -0.035832739999999995], [-0.07462852392890681, -0.023868953981066084]], 'holes': []}], 'simplify_tolerance': 3.2506228e-05, 'sketch_entity_count': 49}
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
