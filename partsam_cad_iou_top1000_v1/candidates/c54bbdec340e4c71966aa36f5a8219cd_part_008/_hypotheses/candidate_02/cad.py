#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.00158553, 0.248339115, 0.046688485], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.01911774499999999, 'zmax': 0.01911774500000002, 'profiles': [{'outer': [[-0.018821765, -0.01033418], [-0.020477685000000002, -0.007118330000000001], [-0.021498965000000002, -0.0036278300000000003], [-0.021842955, 1.3299999999999076e-06], [-0.021498965000000002, 0.00362783], [-0.020477685000000002, 0.00711833], [-0.018821765, 0.01033417], [-0.016592535000000002, 0.01315271], [-0.013875335000000003, 0.01546726], [-0.010774144999999999, 0.01718451], [-0.007411635, 0.018243130000000003], [-0.003913135000000005, 0.018600449999999998], [0.003913145, 0.018600449999999998], [0.007411645000000001, 0.018243130000000003], [0.010774144999999999, 0.01718451], [0.013875325, 0.01546726], [0.016592545, 0.01315271], [0.018821754999999996, 0.01033417], [0.020477675, 0.00711833], [0.021498975000000003, 0.00362783], [0.021842954999999997, 1.3299999999999076e-06], [0.021498975000000003, -0.0036278300000000003], [0.020477675, -0.007118330000000001], [0.018821754999999996, -0.01033418], [0.016592545, -0.01315271], [0.013875325, -0.0154646], [0.010774144999999999, -0.017184520000000002], [0.007411645000000001, -0.018243130000000003], [0.003913145, -0.018600449999999998], [-0.003913135000000005, -0.018600449999999998], [-0.007411635, -0.018243130000000003], [-0.010774144999999999, -0.017184520000000002], [-0.013875335000000003, -0.0154646], [-0.016592535000000002, -0.01315271]], 'holes': []}], 'simplify_tolerance': 8.737181999999999e-06, 'sketch_entity_count': 34}
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
