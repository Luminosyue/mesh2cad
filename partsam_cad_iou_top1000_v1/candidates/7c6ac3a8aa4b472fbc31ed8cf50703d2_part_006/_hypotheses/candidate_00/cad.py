#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.00265352499999999, -0.176063255, -0.3687053], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.286852165, 'zmax': 0.286852165, 'profiles': [{'outer': [[-0.12747156879228194, 0.03727166199836777], [-0.1273881, 0.043123965000000014], [-0.10938164, 0.07999144500000001], [-0.08081546, 0.108618645], [-0.07042780206951486, 0.11390050511131904], [-0.04480251000000002, 0.128151085], [-0.04004147000000002, 0.129249785], [-0.03784409, 0.129921215], [0.0020753199999999916, 0.136269255], [0.04199474999999997, 0.129921215], [0.07806870999999999, 0.111609545], [0.10663488999999998, 0.083043385], [0.12494656999999998, 0.047030445000000004], [0.13129458, 0.00711104500000001], [0.13129458, 0.005340934999999991], [0.13048635027027622, 0.00025838500371399713], [0.13050109, -0.0008850350000000062], [0.1304015893946706, -0.0013924109242527706], [0.13129458, -0.007111014999999998], [0.12494656999999998, -0.047030445000000004], [0.10663488999999998, -0.08304332499999997], [0.07806870999999999, -0.111609565], [0.04199474999999997, -0.129982275], [0.0020753199999999916, -0.136269255], [-0.03784409, -0.129982275], [-0.07385701, -0.111609565], [-0.10242319, -0.08304332499999997], [-0.11478153449818752, -0.058819376686883036], [-0.12128420000000001, -0.04690834499999999], [-0.13129458000000002, -0.008331804999999998], [-0.12946342000000002, 0.033357735]], 'holes': []}], 'simplify_tolerance': 5.4507702000000005e-05, 'sketch_entity_count': 46}
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
