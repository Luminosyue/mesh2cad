#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.072227705, 0.34468811499999996, -0.028462639999999997], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.16191044, 'zmax': 0.16191044, 'profiles': [{'outer': [[-0.13334995500000002, 0.04835740499999999], [-0.11380988500000006, 0.06972626500000001], [-0.09087938500000003, 0.093293705], [-0.06681883500000002, 0.11675838499999999], [-0.04397058500000006, 0.137819065], [-0.024594665000000016, 0.154421075], [-0.010561115000000065, 0.164920605], [-0.0032669350000000263, 0.168310835], [0.057747802195882915, 0.12079566481543404], [0.06101113499999994, 0.122698735], [0.09285848947144308, 0.10147419577849148], [0.09839969499999995, 0.10903273499999999], [0.11491948499999996, 0.128120915], [0.12428891499999997, 0.134367175], [0.15352731499999997, 0.11805285499999998], [0.15531486499999997, 0.11055321500000001], [0.14982890499999996, 0.08975962500000001], [0.13760345499999996, 0.057726845], [0.11985081499999997, 0.017577974999999996], [0.09829699499999997, -0.026741925], [0.07503777499999997, -0.070918005], [0.05237442499999995, -0.110594285], [0.032526014999999964, -0.141928475], [0.017423984999999975, -0.161797435], [0.008527094999999985, -0.168310835], [-0.040621405000000055, -0.14090112500000002], [-0.04191583500000001, -0.133668575], [-0.03501206500000004, -0.113676335], [-0.026663285691370102, -0.09583708355295435], [-0.07558536500000002, -0.063244715], [-0.07607484500000006, -0.058321535], [-0.07175749668699034, -0.048949119423790606], [-0.15531486500000002, 0.016119134999999993], [-0.15517092500000002, 0.020166884999999996], [-0.14760971500000003, 0.031282834999999995]], 'holes': []}], 'simplify_tolerance': 6.7324334e-05, 'sketch_entity_count': 38}
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
