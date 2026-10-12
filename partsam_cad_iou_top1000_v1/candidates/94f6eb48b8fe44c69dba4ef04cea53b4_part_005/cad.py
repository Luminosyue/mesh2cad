#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.074349025, -0.117411185, -0.20902038], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.023911015000000008, 'zmax': 0.023911015, 'profiles': [{'outer': [[-0.019356609999999996, -0.03504649500000001], [-0.02464915000000001, -0.029806315], [-0.028979389999999994, -0.023424045000000004], [-0.03219933, -0.016123634999999997], [-0.034179390000000004, -0.008218565000000011], [-0.03484559000000001, -1.4999999992104662e-08], [-0.034179390000000004, 0.008218575000000006], [-0.03219933, 0.016146024999999994], [-0.028979389999999994, 0.023424045000000004], [-0.02464915000000001, 0.029828704999999997], [-0.019356609999999996, 0.03506888500000001], [-0.013342380000000015, 0.03896543500000001], [-0.006791480000000016, 0.041361585000000006], [0.0, 0.042167764999999996], [0.006791450000000004, 0.041361585000000006], [0.013323840000000003, 0.03896543500000001], [0.0193566, 0.03506888500000001], [0.024630619999999992, 0.029828704999999997], [0.028960879999999994, 0.023424045000000004], [0.03218079999999998, 0.016146015], [0.034160880000000005, 0.008218564999999997], [0.03484558999999998, -1.4999999992104662e-08], [0.034160880000000005, -0.008218565000000011], [0.03218079999999998, -0.016123634999999997], [0.028960879999999994, -0.023424045000000004], [0.024630619999999992, -0.029806315], [0.0193566, -0.03504649500000001], [0.013323849999999998, -0.03894303499999999], [0.006791469999999994, -0.041339185], [0.0, -0.042167764999999996], [-0.006791480000000016, -0.041339185], [-0.013342380000000015, -0.03894303499999999]], 'holes': []}], 'simplify_tolerance': 1.6867106e-05, 'sketch_entity_count': 32}
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
