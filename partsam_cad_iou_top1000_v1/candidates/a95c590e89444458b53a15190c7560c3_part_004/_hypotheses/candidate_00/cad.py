#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.09059310000000001, 0.40593776000000004, 0.023621845000000002], 'basis': [[0.0, 0.9924338902748003, -0.1227801833930278], [-0.9936943871625379, 0.01376642654144255, 0.11127421274467586], [0.1121225442168894, 0.12200597909243878, 0.986175986395951]], 'axis': [-0.1227801833930278, 0.11127421274467586, 0.986175986395951], 'zmin': -0.021480588471188364, 'zmax': 0.017623055570039573, 'profiles': [{'outer': [[-0.09185109758792667, -0.06078805996863126], [-0.09353127668709701, -0.04750267515038037], [-0.09222408146333076, -0.03206920408276685], [-0.05177656595156699, 0.0014088253399586665], [-0.026039016050692677, 0.016237552856223622], [-0.002089408110869073, 0.02456315845581696], [0.026251374823343523, 0.0319447090225355], [0.057158260826053464, 0.044900192744705546], [0.09467543550792036, 0.07260914487396122], [0.09495715702151034, 0.07194145735480595], [0.09237907162044477, 0.05621949743250314], [0.09353211189649023, 0.04064581117381253], [0.09246324078033227, 0.02509418718820669], [0.0861788315537424, -1.4966616090967504e-05], [0.07609441439031137, -0.013060138687687088], [0.05442761264645636, -0.034264455997181545], [0.024968829699783753, -0.052696793083293704], [0.005151525164136318, -0.05920511464779328], [-0.017196742674124778, -0.06524250130675137], [-0.05025626012267724, -0.07122509419837583], [-0.0756008108074485, -0.06885927872301781], [-0.0915931364283592, -0.061455479098621146]], 'holes': []}], 'simplify_tolerance': 3.7697686741721475e-05, 'sketch_entity_count': 28}
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
