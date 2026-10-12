#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.01888546, -0.052492205, -0.175816105], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.05149277, 'zmax': 0.05149277, 'profiles': [{'outer': [[-0.023657244999999993, -0.123839255], [-0.02712932500000001, -0.123368465], [-0.02712932500000001, -0.013379934999999996], [-0.021538665000000012, -0.010260955000000002], [-0.01742485499999999, -0.010260955000000002], [-0.01742485499999999, 0.012639799136875346], [-0.01877279500000001, 0.012572405000000002], [-0.021538665000000012, 0.012984355000000003], [-0.02712932500000001, 0.016162185000000003], [-0.02712932500000001, 0.150631845], [0.02248029500000001, 0.150631845], [0.02712932500000001, 0.150102185], [0.02712932500000001, 0.015691394999999997], [0.021126764999999992, 0.012572405000000002], [0.016742554999999992, 0.012747766645388077], [0.016742554999999992, -0.010260955000000002], [0.017478135000000006, -0.010260955000000002], [0.021126764999999992, -0.010672904999999996], [0.02712932500000001, -0.013909564999999999], [0.02712932500000001, -0.123839255], [0.021597544999999996, -0.123780395], [0.016230369476641155, -0.12343782171437301], [0.013889629313427397, -0.12345316980828666], [0.014870374999999991, -0.150163795], [0.012588634999999987, -0.150163795], [-0.00016562500000000258, -0.150631845], [-0.012919915000000004, -0.150163795], [-0.015201655000000008, -0.150163795], [-0.013924972931263635, -0.12347018368170201], [-0.015927592446253785, -0.12345933008267243], [-0.019067004999999998, -0.123780395]], 'holes': []}], 'simplify_tolerance': 6.0252738e-05, 'sketch_entity_count': 31}
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
