#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.039240525, 0.05844449999999998, 0.09182492], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.013703225, 'zmax': 0.013703225, 'profiles': [{'outer': [[-0.27949694, -0.18458145999999997], [-0.25880471000000005, -0.14734775], [-0.23573211000000002, -0.11157896999999999], [-0.21326974, -0.07544400999999998], [-0.18922046, -0.04022460999999998], [-0.15613741, 0.006592210000000015], [-0.12140631999999998, 0.04968566000000002], [-0.09406085, 0.08118170000000002], [-0.06757000999999999, 0.11273879], [-0.03967525999999999, 0.14301407000000002], [-0.03249158715541002, 0.1502429942258401], [-0.035890829999999985, 0.22846842000000003], [-0.027403108293019965, 0.22894338418910254], [-0.03192333, 0.33400463999999996], [-0.029176599999999997, 0.33412664999999997], [-0.020692219999999997, 0.19379836000000003], [-0.02502874727971475, 0.19355416], [-0.022994503952997628, 0.15979990144057227], [-0.010620770000000002, 0.17225158000000002], [0.01928827000000001, 0.20057362000000004], [0.06067261, 0.23915023], [0.10162968, 0.27418655000000003], [0.13477377000000001, 0.30195922], [0.16877240999999998, 0.32863319], [0.20374766, 0.35402536000000007], [0.23969956, 0.37795252], [0.27656703, 0.40047586], [0.31404487999999997, 0.42196161], [0.35256036999999996, 0.44155502], [0.35603960999999995, 0.43966281000000007], [0.35732140999999995, 0.43734336000000007], [0.36202142000000004, 0.43307066000000005], [0.32497083000000004, 0.41109662999999996], [0.28773712, 0.38967204], [0.25117487, 0.3673318], [0.21546713, 0.34364873000000007], [0.18073603, 0.31843972], [0.14698152, 0.29188776000000005], [0.07226998000000001, 0.22993338], [0.0014649200000000084, 0.16315687], [-0.021786623046147244, 0.13975749849725239], [0.01318438000000001, -0.44051737], [-0.006775329999999996, -0.44155502], [-0.03159199299499173, 0.1295409910327857], [-0.05493498999999999, 0.10413229000000002], [-0.08130378999999999, 0.07281935], [-0.10846603999999999, 0.04150647000000002], [-0.14264782, -0.0017701399999999826], [-0.17566982, -0.04846482999999999], [-0.19965812000000002, -0.08362322999999998], [-0.22205934000000002, -0.11963614999999998], [-0.24507102, -0.15534388999999998], [-0.26564111999999995, -0.19245547], [-0.28676053999999995, -0.22944504], [-0.30824622, -0.26625144], [-0.32942667999999997, -0.30330201999999995], [-0.34975263, -0.33699548], [-0.35304871000000004, -0.3352253399999999], [-0.35689415999999996, -0.34029155999999994], [-0.36067857999999997, -0.33827728], [-0.36202142000000004, -0.33040327], [-0.34328249, -0.29561114]], 'holes': []}], 'simplify_tolerance': 0.00017662200800000003, 'sketch_entity_count': 71}
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
