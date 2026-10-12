#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.09779490999999998, -0.06325351, -0.3219344], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.03545297, 'zmax': 0.03545297, 'profiles': [{'outer': [[-0.17806208, -0.015406550000000019], [-0.17806208, 0.02496039999999998], [-0.1657576, 0.02496039999999998], [-0.1657576, 0.02598317999999998], [-0.16540599, 0.02601064714487048], [-0.16540599, 0.026557549999999985], [-0.13146889, 0.029208179999999986], [-0.12034511999999997, 0.02730210999999999], [-0.12034511999999997, 0.023817569999999982], [-0.11723292000000002, 0.023817569999999982], [-0.11723292000000002, 0.024755709999999986], [0.00828509999999999, 0.024755709999999986], [0.01946848000000001, 0.020809539999999987], [0.03132587000000003, 0.020809539999999987], [0.03132587000000003, 0.03272842999999999], [0.17806208, 0.03272842999999999], [0.17806208, -0.03272843], [0.03132587000000003, -0.03272843], [0.03132587000000003, -0.011251250000000018], [0.01946848000000001, -0.011251250000000018], [0.00828509999999999, -0.015197430000000012], [-0.11723292000000002, -0.015197430000000012], [-0.11723292000000002, -0.014259280000000013], [-0.12034511999999997, -0.014259280000000013], [-0.12034511999999997, -0.017743830000000016], [-0.13146889, -0.019649900000000012], [-0.16540599, -0.01699927000000001], [-0.16540599, -0.016448347144870513], [-0.1657576, -0.016420880000000013], [-0.1657576, -0.015406550000000019]], 'holes': []}], 'simplify_tolerance': 7.1224832e-05, 'sketch_entity_count': 30}
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
