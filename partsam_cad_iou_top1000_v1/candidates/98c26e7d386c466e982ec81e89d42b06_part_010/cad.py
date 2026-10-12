#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.14208565, -0.12341362, -0.12828073499999998], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.027907270000000012, 'zmax': 0.027907269999999984, 'profiles': [{'outer': [[-0.310035575, 0.003519919999999996], [-0.31676580499999996, 0.020152119999999996], [-0.31425165499999996, 0.037557900000000005], [-0.29943736499999996, 0.05159855000000001], [-0.283346705, 0.05577593], [-0.08553973499999998, 0.0583674], [0.12773906500000004, 0.058367329999999995], [0.270002265, 0.05148234], [0.286170325, 0.04916156000000001], [0.30257042500000003, 0.04192849], [0.31444504500000003, 0.02885481000000001], [0.316765805, 0.010946200000000003], [0.312162895, -0.005802019999999991], [0.300404335, -0.018991730000000012], [0.22664251500000004, -0.05364854999999999], [0.20989426500000002, -0.05778723999999999], [0.11617385500000002, -0.058367399999999986], [-0.21855857499999998, -0.058367310000000006], [-0.23538417499999997, -0.05709088000000001], [-0.251088015, -0.051018199999999986]], 'holes': [[[-0.08546237499999998, 0.04672487], [-0.281451425, 0.044288110000000006], [-0.295453395, 0.04065225], [-0.303266665, 0.033728610000000006], [-0.305355365, 0.02255024], [-0.29986288499999997, 0.00990204], [-0.24540214499999996, -0.04084549000000001], [-0.23248318499999998, -0.045835139999999996], [-0.21855857499999998, -0.046724779999999994], [0.11617385500000002, -0.04672487], [0.20877256500000002, -0.04622208], [0.222271765, -0.04285696], [0.29324861500000005, -0.009786010000000012], [0.301874185, -0.00038689000000000084], [0.305161915, 0.011603760000000005], [0.30415626500000004, 0.023478360000000004], [0.295608125, 0.03256805], [0.28241839500000004, 0.0381379], [0.269306025, 0.03983980000000001], [0.12773906500000004, 0.0467248]]]}], 'simplify_tolerance': 0.000126706322, 'sketch_entity_count': 58}
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
