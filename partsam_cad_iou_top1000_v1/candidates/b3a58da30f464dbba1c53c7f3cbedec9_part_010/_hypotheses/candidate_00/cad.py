#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0022845999999999977, -0.075059295, 0.0], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.19030753, 'zmax': 0.19030753, 'profiles': [{'outer': [[-0.36734518, -0.036159905000000006], [-0.36910251, 2.2634999999993077e-05], [-0.36734518, 0.036160125], [-0.36202815, 0.072027265], [-0.35319656, 0.107128375], [-0.34098554, 0.14123818500000002], [-0.32553017, 0.173996245], [-0.30687568, 0.205042015], [-0.28533736, 0.234150245], [-0.26100534, 0.261005535], [-0.23415008, 0.285337465], [-0.20504184, 0.306875785], [-0.17399602, 0.32553035500000005], [-0.14123797, 0.34098559500000003], [-0.10712815, 0.35319656499999996], [-0.07202703, 0.36202824499999997], [-0.0361599, 0.36734521499999995], [2.264e-05, 0.36910247500000004], [0.03616013, 0.36734521499999995], [0.07202727, 0.362028185], [0.10712837, 0.353196505], [0.14123818, 0.34098553499999995], [0.17399625, 0.325530235], [0.20504202, 0.30687566499999996], [0.23415026, 0.28533734499999996], [0.26100552, 0.261005355], [0.28533748, 0.234150065], [0.3068758, 0.205041845], [0.32553032, 0.173996035], [0.3409856, 0.14123797500000002], [0.35319659, 0.107128165], [0.36202824, 0.072027045], [0.36734518, 0.036159895], [0.36910251, -2.264500000000169e-05], [0.36734518, -0.036160134999999996], [0.36202818, -0.07202726500000001], [0.35319653, -0.107128365], [0.34098554, -0.141238185], [0.3255302, -0.173996235], [0.30687568, -0.20504203499999998], [0.28533736, -0.234150265], [0.26100534, -0.26100552499999996], [0.23415008, -0.285337505], [0.20504184, -0.306875765], [0.17399605, -0.32553029499999997], [0.14123797, -0.34098553499999995], [0.10712817, -0.35319662500000004], [0.07202705, -0.36202824499999997], [0.0361599, -0.36734521499999995], [-2.264e-05, -0.36910247500000004], [-0.03616013, -0.36734521499999995], [-0.07202725, -0.362028185], [-0.10712836, -0.35319656499999996], [-0.14123818, -0.340985475], [-0.17399622, -0.32553017500000003], [-0.20504202, -0.306875645], [-0.23415026, -0.28533738500000005], [-0.26100552, -0.26100534500000006], [-0.28533748, -0.23415008499999998], [-0.3068758, -0.20504185500000002], [-0.32553029, -0.173996035], [-0.3409856, -0.14123797500000002], [-0.35319662, -0.107128155], [-0.36202821, -0.072027025]], 'holes': []}], 'simplify_tolerance': 0.00014764100400000002, 'sketch_entity_count': 70}
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
