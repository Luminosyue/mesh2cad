#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.009398245000000006, 0.194750415, -0.0025075349999999913], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.135524645, 'zmax': 0.135524645, 'profiles': [{'outer': [[-0.16606481500000003, 0.0013875450000000056], [-0.16331254500000003, 0.014329565000000006], [-0.15874578500000003, 0.026691335000000007], [-0.15246649500000004, 0.03827103500000001], [-0.14443388499999998, 0.04896775500000001], [-0.134403335, 0.058403075000000006], [-0.12282333500000002, 0.066122875], [-0.10251757500000001, 0.07724846500000002], [-0.094179175, 0.08264727500000002], [-0.074750065, 0.097582315], [-0.06353704500000001, 0.10520122500000001], [-0.05159009500000001, 0.111810975], [-0.039092665000000006, 0.116982755], [-0.02622827500000001, 0.120590365], [-0.013139625000000009, 0.12263385500000001], [-1.0195000000008843e-05, 0.12328978500000001], [0.013139624999999992, 0.12263385500000001], [0.02622826499999999, 0.120590365], [0.03909266499999999, 0.116982755], [0.051590084999999994, 0.111810975], [0.06353705499999998, 0.10520122500000001], [0.07475006499999999, 0.097582315], [0.09417918499999998, 0.08264727500000002], [0.10251757499999999, 0.07724846500000002], [0.12282333499999999, 0.066122875], [0.134403335, 0.058403075000000006], [0.14443389499999998, 0.04896775500000001], [0.15246648499999998, 0.03827103500000001], [0.15874579499999997, 0.026691335000000007], [0.16331255499999997, 0.014329565000000006], [0.16606481499999998, 0.0013875450000000056], [0.167002635, -0.011857214999999994], [0.16606481499999998, -0.02502629499999999], [0.163271765, -0.037690804999999994], [0.158603065, -0.04949755499999999], [0.15214030499999998, -0.06006813499999999], [0.143883435, -0.06917548499999998], [0.133689785, -0.07656732499999999], [0.122007835, -0.082142735], [0.11071327499999999, -0.086103555], [0.101396275, -0.089004785], [0.093098645, -0.092107835], [0.08414862499999999, -0.09664890500000001], [0.07401612499999999, -0.10222431499999998], [0.062966205, -0.10785017499999999], [0.05122311499999999, -0.112996715], [0.03890917499999999, -0.11741163500000001], [0.026146724999999992, -0.120716515], [0.013119234999999991, -0.122659095], [-1.0195000000008843e-05, -0.12328978500000001], [-0.01311923500000001, -0.122659095], [-0.026146715000000008, -0.120716515], [-0.038909185000000006, -0.11741163500000001], [-0.05122310500000001, -0.112996715], [-0.06296620500000001, -0.10785017499999999], [-0.074016125, -0.10222431499999998], [-0.08414861500000001, -0.09664890500000001], [-0.09309864500000001, -0.092107835], [-0.101396285, -0.089004785], [-0.11071327500000001, -0.086103555], [-0.12200785500000001, -0.082142735], [-0.133689775, -0.07656732499999999], [-0.143883435, -0.06917548499999998], [-0.15214029499999998, -0.06006813499999999], [-0.158603055, -0.04949755499999999], [-0.16327175500000002, -0.037690804999999994], [-0.16606481500000003, -0.02502629499999999], [-0.167002635, -0.011857214999999994]], 'holes': []}], 'simplify_tolerance': 6.6801054e-05, 'sketch_entity_count': 89}
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
