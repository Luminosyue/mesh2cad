#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.166383645, 0.14755416, -0.179050755], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.067650865, 'zmax': 0.06765086499999999, 'profiles': [{'outer': [[-0.005124624999999994, -0.08495554], [-0.005124624999999994, -0.07485144999999999], [-0.0033244749999999934, -0.07485144999999999], [-0.0033244749999999934, -0.07125114999999999], [-0.0019598450000000156, -0.07122213], [-0.0019598450000000156, 0.004180970000000006], [-0.004311645000000003, 0.004180970000000006], [-0.004311645000000003, 0.0002903300000000053], [-0.0073312650000000035, 0.0002903300000000053], [-0.0073312650000000035, -0.04305848999999999], [-0.011628405000000008, -0.04305848999999999], [-0.011628405000000008, 0.06776696000000001], [-0.0073312650000000035, 0.06776696000000001], [-0.0073312650000000035, 0.024389120000000014], [-0.004311645000000003, 0.024389120000000014], [-0.004311645000000003, 0.02052751], [-0.0019598450000000156, 0.02052751], [-0.0019598450000000156, 0.07506628671999784], [-0.0029760550000000052, 0.07604185000000002], [-0.0037890150000000067, 0.07900342000000002], [-0.003005095000000013, 0.08196497], [-0.0007113450000000021, 0.08417159000000002], [0.0023953649999999826, 0.08495554000000002], [0.005473034999999987, 0.08417159000000002], [0.00773774499999999, 0.08199400000000001], [0.008579745, 0.07900342000000002], [0.00773774499999999, 0.07604185000000002], [0.006750574999999981, 0.07509266366846087], [0.006750574999999981, 0.02052751], [0.009131424999999999, 0.02052751], [0.009131424999999999, 0.004180970000000006], [0.006750574999999981, 0.004180970000000006], [0.006750574999999981, -0.04067763999999999], [0.006692484999999998, -0.04302945999999999], [0.006692484999999998, -0.05117939600154991], [0.006750574999999981, -0.05139141999999999], [0.006692484999999998, -0.051600543999999936], [0.006750574999999981, -0.07122213], [0.008086165000000006, -0.07125114999999999], [0.008086165000000006, -0.07485144999999999], [0.01162840499999998, -0.07485144999999999], [0.01162840499999998, -0.08440389999999999]], 'holes': []}], 'simplify_tolerance': 3.3982216000000005e-05, 'sketch_entity_count': 45}
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
