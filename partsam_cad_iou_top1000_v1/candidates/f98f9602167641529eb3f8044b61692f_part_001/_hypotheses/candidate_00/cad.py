#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.23105614, 0.23382748999999997, 0.126634825], 'basis': [[0.0, 0.9999999999503167, -9.968286945026298e-06], [-0.35623705687157986, 9.314323578384457e-06, 0.9343956117323744], [0.9343956117787984, 3.5510732033475606e-06, 0.3562370568538808]], 'axis': [-9.968286945026298e-06, 0.9343956117323744, 0.3562370568538808], 'zmin': -0.11332670345039954, 'zmax': 0.12021991715942468, 'profiles': [{'outer': [[-0.07143094536050014, 0.07010124293373629], [-0.03882893934442482, 0.09158406293291077], [-0.0003679789396562951, 0.09913940293274173], [0.038078719849728875, 0.09158406293321121], [0.07068071074026251, 0.07010124293435627], [0.09247716218700229, 0.037941142935993696], [0.10011806951119585, -7.6167098895609205e-06], [0.09247720492597389, -0.03794112670799543], [0.07068076994793136, -0.070101216706588], [0.038078756807114894, -0.09159830670557553], [-0.00036793841989969856, -0.09913937670538815], [-0.03882888948071209, -0.09159830670593362], [-0.07143090262152856, -0.07010121670705721], [-0.09321308176577327, -0.037941126708861905], [-0.10086826495483243, -6.63706271753449e-06], [-0.093213129410271, 0.037941142935535306]], 'holes': []}], 'simplify_tolerance': 4.019726689320566e-05, 'sketch_entity_count': 34}
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
