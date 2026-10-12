#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.173990225, 0.147539645, -0.179050755], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.067650875, 'zmax': 0.067650875, 'profiles': [{'outer': [[-0.005124624999999994, -0.084941025], [-0.005124624999999994, -0.074836935], [-0.0033244749999999934, -0.074836935], [-0.0033244749999999934, -0.07123663499999999], [-0.0019598450000000156, -0.071207615], [-0.0019598450000000156, 0.004195484999999999], [-0.004311645000000003, 0.004195484999999999], [-0.004311645000000003, 0.00030484499999999803], [-0.0073312650000000035, 0.00030484499999999803], [-0.0073312650000000035, -0.043043975], [-0.011628405000000008, -0.043043975], [-0.011628405000000008, 0.06778147500000001], [-0.0073312650000000035, 0.06778147500000001], [-0.0073312650000000035, 0.024403635000000007], [-0.004311645000000003, 0.024403635000000007], [-0.004311645000000003, 0.02054202499999999], [-0.0019598450000000156, 0.02054202499999999], [-0.0019598450000000156, 0.07508080171999783], [-0.0029760550000000052, 0.07605636500000001], [-0.0037890150000000067, 0.07901793500000001], [-0.003005095000000013, 0.08197948499999999], [-0.0007113450000000021, 0.08418610500000001], [0.0023953649999999826, 0.08497005500000002], [0.005473034999999987, 0.08418610500000001], [0.00773774499999999, 0.082008515], [0.008579745, 0.07901793500000001], [0.00773774499999999, 0.07605636500000001], [0.006750574999999981, 0.07510717866846087], [0.006750574999999981, 0.02054202499999999], [0.009131424999999999, 0.02054202499999999], [0.009131424999999999, 0.004195484999999999], [0.006750574999999981, 0.004195484999999999], [0.006750574999999981, -0.040663124999999994], [0.006692484999999998, -0.043014945], [0.006692484999999998, -0.05116488100154991], [0.006750574999999981, -0.051376905], [0.006692484999999998, -0.05158602899999994], [0.006750574999999981, -0.071207615], [0.008086165000000006, -0.07123663499999999], [0.008086165000000006, -0.074836935], [0.01162840499999998, -0.074836935], [0.01162840499999998, -0.084970055]], 'holes': []}], 'simplify_tolerance': 3.398802200000001e-05, 'sketch_entity_count': 48}
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
