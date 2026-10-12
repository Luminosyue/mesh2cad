#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.34250258, 0.08800374, -0.1476696], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.10522796000000001, 'zmax': 0.10522796000000001, 'profiles': [{'outer': [[-0.1972528, 0.01955591000000001], [-0.1861787, 0.036139000000000004], [-0.16959563, 0.04721306], [-0.15003658, 0.05110619999999999], [-0.13048378000000002, 0.04721306], [-0.11390070000000002, 0.036139000000000004], [-0.10282660000000002, 0.01955591000000001], [-0.09893351, 3.080000000002525e-06], [-0.10282660000000002, -0.019555939999999994], [-0.11390070000000002, -0.036139], [-0.13048378000000002, -0.04721309], [-0.15003658, -0.0511062], [-0.16959563, -0.04721309], [-0.1861787, -0.036139], [-0.1972528, -0.019555939999999994], [-0.20114590000000002, 3.080000000002525e-06]], 'holes': []}, {'outer': [[0.10754693999999998, -0.04347028], [0.09556292, -0.04015957], [0.08540202999999999, -0.030738669999999996], [0.07861285999999998, -0.016633999999999996], [0.07622522999999998, 3.3200000000011e-06], [0.07861285999999998, 0.016632960000000002], [0.08540202999999999, 0.030737680000000003], [0.09556292, 0.040158550000000015], [0.10754693999999998, 0.04346923999999999], [0.13221257765257616, 0.04346923999999999], [0.13625211999999998, 0.04721473000000001], [0.15034921, 0.05110513], [0.16431660999999997, 0.05110513], [0.17841363999999998, 0.04721473000000001], [0.19035955, 0.03613846], [0.19834633000000002, 0.019554600000000005], [0.2011459, 3.3200000000011e-06], [0.19834633000000002, -0.019555580000000003], [0.19035955, -0.03613947], [0.17841363999999998, -0.047215719999999996], [0.16431660999999997, -0.05110617], [0.15034921, -0.05110617], [0.13625211999999998, -0.047215719999999996], [0.13221262428403113, -0.04347028]], 'holes': []}], 'simplify_tolerance': 8.045836e-05, 'sketch_entity_count': 40}
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
