#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.262877405, -0.35472033999999997, -0.18048930000000002], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.004355045000000002, 'zmax': 0.004355045000000002, 'profiles': [{'outer': [[-0.012374970000000013, 0.0050157499999999855], [-0.01113705000000001, 0.007281619999999989], [-0.009472340000000024, 0.009269009999999966], [-0.007441330000000024, 0.010898009999999958], [-0.0051257700000000295, 0.012109329999999974], [-0.0026139900000000105, 0.012856619999999985], [8.099999999899854e-07, 0.013107849999999976], [0.002613979999999988, 0.012856619999999985], [0.005125759999999979, 0.012109329999999974], [0.007441329999999968, 0.010898009999999958], [0.009472339999999968, 0.009269009999999966], [0.011137059999999976, 0.007281619999999989], [0.012374949999999968, 0.0050157499999999855], [0.01313861999999999, 0.0025578899999999516], [0.01339536999999999, -7.900000000282681e-07], [0.01313861999999999, -0.002557890000000007], [0.012374949999999968, -0.005015740000000046], [0.011137059999999976, -0.007281620000000044], [0.009472339999999968, -0.009269010000000022], [0.007441329999999968, -0.010898010000000014], [0.005125779999999969, -0.012109350000000019], [0.0026139899999999827, -0.01285662000000004], [8.199999999847218e-07, -0.013107850000000032], [-0.0026139900000000105, -0.01285662000000004], [-0.0051257700000000295, -0.012109350000000019], [-0.007441330000000024, -0.010898010000000014], [-0.009472340000000024, -0.009269040000000006], [-0.01113705000000001, -0.007281620000000044], [-0.012374970000000013, -0.005015740000000046], [-0.013138640000000007, -0.002557890000000007], [-0.013395370000000018, -8.200000000124774e-07], [-0.013138640000000007, 0.0025578899999999516]], 'holes': []}], 'simplify_tolerance': 5.358148000000002e-06, 'sketch_entity_count': 35}
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
