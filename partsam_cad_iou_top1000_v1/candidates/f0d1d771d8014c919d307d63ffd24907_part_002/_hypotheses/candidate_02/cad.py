#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.021767090000000003, -0.223519705, 0.061327915], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.106755145, 'zmax': 0.10675514500000001, 'profiles': [{'outer': [[-0.065058515, 0.008717959999999997], [-0.064931255, 0.029208329999999998], [-0.064915345, 0.05125776], [-0.064215355, 0.07612303], [-0.058535954999999994, 0.09839517], [-0.044059074999999996, 0.10929262], [-0.027577684999999998, 0.11091531], [0.029757174999999997, 0.11091531], [0.04574539500000001, 0.10924489999999999], [0.059172295, 0.09825199999999999], [0.06431080500000001, 0.07602758], [0.06493123499999999, 0.051289589999999996], [0.064963075, 0.029208329999999998], [0.065074435, 0.008717959999999997], [0.0651021285408127, -0.010220912325649313], [0.06690392500000002, -0.015463240000000003], [0.068987965, -0.038292190000000004], [0.06687212499999999, -0.061264320000000004], [0.05984046500000001, -0.08194560000000001], [0.05627519949542568, -0.08634094701392175], [0.055608765000000004, -0.08824545], [0.054940605, -0.08939087], [0.05287006360287081, -0.09099004970949859], [0.05217250500000001, -0.09371802], [0.049643015, -0.09936562], [0.045968085000000006, -0.10310415], [0.038554675, -0.10790857000000001], [0.03526156500000001, -0.10921309], [0.03017080500000001, -0.11008806], [0.028500385000000003, -0.11021533], [0.023425505, -0.11040623000000001], [0.015157440973557864, -0.11045396], [0.0005329350000000052, -0.11091531], [-0.013584684866739333, -0.11045394], [-0.022550544999999998, -0.11040623000000001], [-0.028007224999999997, -0.11023123], [-0.029773084999999998, -0.11010397000000001], [-0.035102484999999996, -0.10922899], [-0.038443305, -0.10792449], [-0.045920384999999994, -0.10312007000000001], [-0.049627115, -0.09938152], [-0.052140675, -0.09371802], [-0.0529436324106537, -0.09058266878653667], [-0.054304254999999996, -0.08956585], [-0.054956515, -0.08843635], [-0.05592869299278676, -0.08586802748093543], [-0.059172304999999994, -0.08215241000000001], [-0.066776665, -0.06135977], [-0.068987965, -0.038292190000000004], [-0.066808485, -0.015383690000000002], [-0.0650877208165253, -0.010725387981931506]], 'holes': []}], 'simplify_tolerance': 4.4366124e-05, 'sketch_entity_count': 84}
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
