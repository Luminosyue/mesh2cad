#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-5.620000000011727e-06, 0.052253629999999995, -0.10797199500000002], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.39202776500000003, 'zmax': 0.39202776500000003, 'profiles': [{'outer': [[-0.11710832000000002, 0.048527910000000014], [-0.10538315000000001, 0.07039895000000002], [-0.08963791000000002, 0.08963784000000001], [-0.07039903, 0.10538309000000001], [-0.048528, 0.11710827000000001], [-0.024742620000000007, 0.12428694000000001], [-1.0000000000287557e-07, 0.1267277], [0.024694759999999996, 0.12428694000000001], [0.048480129999999996, 0.11710827000000001], [0.07039903, 0.10538309000000001], [0.08959004, 0.08963784000000001], [0.10538313999999999, 0.07039895000000002], [0.11706045999999999, 0.048527910000000014], [0.124287, 0.02474252000000001], [0.12672776, 1.1726324121788534e-17], [0.124287, -0.02469467999999999], [0.11706045999999999, -0.04848004999999999], [0.10538313999999999, -0.07039895999999998], [0.08959004, -0.08958997999999999], [0.07039903, -0.10538308999999998], [0.048480129999999996, -0.11706040999999999], [0.024694759999999996, -0.12428695], [9.999999999593667e-08, -0.1267277], [-0.024742620000000007, -0.12428695], [-0.048528, -0.11706040999999999], [-0.07039903, -0.10538308999999998], [-0.08963791000000002, -0.08958997999999999], [-0.10538315000000001, -0.07039895999999998], [-0.11710832000000002, -0.04848004999999999], [-0.12428701, -0.02469467999999999], [-0.12672776, 1.1726324121788534e-17], [-0.12428701, 0.02474252000000001]], 'holes': []}], 'simplify_tolerance': 5.0691104e-05, 'sketch_entity_count': 32}
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
