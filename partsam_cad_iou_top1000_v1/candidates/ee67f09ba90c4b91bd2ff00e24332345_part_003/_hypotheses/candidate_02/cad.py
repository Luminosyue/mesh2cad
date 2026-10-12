#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0015473249999999987, 0.178422265, 0.330472955], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.254718605, 'zmax': 0.254718605, 'profiles': [{'outer': [[-0.169526945, -0.058586445], [-0.169526915, 0.056635145], [0.09685245114898752, 0.056635094999999996], [0.098055175, 0.05697735500000001], [0.10251863499999997, 0.057867365000000004], [0.10703866499999998, 0.058408495000000005], [0.11157994500000001, 0.058586495], [0.11612825500000001, 0.058408484999999996], [0.120648315, 0.057867365000000004], [0.125111745, 0.05697735500000001], [0.12949030499999997, 0.055731345], [0.133755705, 0.054143565000000005], [0.137886695, 0.052228264999999996], [0.14186208499999997, 0.04999255500000001], [0.145639385, 0.047450685000000006], [0.14921151499999996, 0.044609785], [0.152557365, 0.04150543500000001], [0.155641425, 0.038137635], [0.158463825, 0.034541985], [0.16098909499999997, 0.030739865], [0.163210205, 0.026738385], [0.16511302499999997, 0.022580255], [0.16669043499999997, 0.018286855], [0.167928325, 0.013879525000000002], [0.168812505, 0.009386755000000002], [0.16935010499999997, 0.004837025000000001], [0.16952695499999998, 0.0002659350000000012], [0.16935010499999997, -0.004312284999999999], [0.168670045, -0.009994844999999999], [0.167780565, -0.014421674999999998], [0.16656007499999997, -0.018786445], [0.16498791499999998, -0.023027094999999997], [0.163084795, -0.027143624999999998], [0.160892095, -0.031073985], [0.158368375, -0.034838855], [0.15557577499999997, -0.038396865], [0.15249352499999996, -0.04170663499999999], [0.14918377499999996, -0.044788865], [0.14562576499999996, -0.047581495], [0.141860895, -0.050105205], [0.13790982499999999, -0.052318615], [0.13381399499999996, -0.054201034999999995], [0.129573335, -0.055773185], [0.12520860499999997, -0.056993674999999994], [0.12078177499999998, -0.057883165], [0.11627220499999996, -0.058421005], [0.11176260500000001, -0.058586495]], 'holes': []}], 'simplify_tolerance': 6.7810782e-05, 'sketch_entity_count': 53}
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
