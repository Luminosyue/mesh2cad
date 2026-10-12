#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-12.58575964, 4.738121035000001, 14.33311367], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -2.6860427850000006, 'zmax': 2.6860427849999997, 'profiles': [{'outer': [[-5.61526585, 0.5623249999999995], [-5.43887043, 1.1014208799999992], [-5.19795132, 1.858816619999999], [-3.893324849999999, 2.5574421899999997], [-2.3024625800000003, 2.7645268399999985], [-1.0681123699999997, 2.7861752499999994], [-0.708156878795357, 2.756745388655627], [0.1444997800000003, 2.7312188199999987], [1.3944244399999999, 2.6606202099999994], [2.6948118200000017, 2.479073999999999], [3.3763647100000007, 2.305689339999999], [3.9353303900000007, 2.1342644699999997], [5.38181973, 1.3176112199999999], [5.61526585, 0.23194646999999868], [5.407530780000002, -0.79165697], [4.550974849999999, -1.5897688900000002], [4.1343393299999995, -1.8324732800000003], [2.6405210500000003, -2.1219382300000014], [1.4091567999999999, -2.196691040000001], [0.25598705867274474, -2.235340543877511], [-1.054375649999999, -2.666377540000001], [-2.434401509999999, -2.786175250000001], [-3.681834219999999, -2.4739546800000003], [-3.7606420499999995, -2.4204936000000004], [-4.066835702727993, -2.1876919836637563], [-4.465472219999999, -1.8912911400000016], [-5.183247569999999, -0.9361395800000007]], 'holes': []}], 'simplify_tolerance': 0.0022461063400000003, 'sketch_entity_count': 45}
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
