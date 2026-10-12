#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.088968935, -0.26760395000000003, 0.0], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.41103098, 'zmax': 0.41103098, 'profiles': [{'outer': [[-0.20775382000000003, -0.312783005], [-0.20775382000000003, 0.312783045], [-0.20733267000000002, 0.35387867500000003], [-0.20420912000000002, 0.39216429500000005], [-0.19575083000000004, 0.408672755], [-0.17915020000000004, 0.411031065], [-0.13001506000000004, 0.411031065], [-0.11611687000000004, 0.410730005], [-0.11004515000000004, 0.408773065], [-0.10702685000000003, 0.40315318499999997], [-0.10435951000000004, 0.391160725], [-0.09762100000000004, 0.371541205], [-0.07340439000000004, 0.34921211500000005], [-0.022093270000000026, 0.32984353499999997], [0.042028049999999983, 0.315542865], [0.10102529999999998, 0.306510825], [0.14658055999999997, 0.298532595], [0.17500875999999999, 0.286239015], [0.19101274999999995, 0.263207425], [0.20034841999999997, 0.227280155], [0.20448980999999994, 0.19672189499999998], [0.20722735999999997, 0.151963375], [0.20775381999999998, 0.086531585], [0.20775381999999998, -0.086531515], [0.20722735999999997, -0.151963295], [0.20448980999999994, -0.19672184499999998], [0.20034841999999997, -0.22728010499999998], [0.19101274999999995, -0.263207375], [0.17500875999999999, -0.286238965], [0.14658055999999997, -0.29853254500000004], [0.10102529999999998, -0.30651080500000005], [0.042028049999999983, -0.31554275499999995], [-0.022093270000000026, -0.329843455], [-0.07340439000000004, -0.349212045], [-0.09762100000000004, -0.37154119500000005], [-0.10435951000000004, -0.391160665], [-0.10702685000000003, -0.40315311499999995], [-0.11004515000000004, -0.408773065], [-0.11611687000000004, -0.410730005], [-0.13001506000000004, -0.411031065], [-0.17915020000000004, -0.411031065], [-0.19575083000000004, -0.408672685], [-0.20420912000000002, -0.39216422500000003], [-0.20733267000000002, -0.35387861499999995]], 'holes': []}], 'simplify_tolerance': 0.000164412426, 'sketch_entity_count': 47}
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
