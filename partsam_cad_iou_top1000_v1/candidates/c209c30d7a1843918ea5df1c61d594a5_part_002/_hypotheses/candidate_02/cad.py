#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.008384029999999987, -0.091780635, -0.0011914949999999869], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.24896332, 'zmax': 0.24896332, 'profiles': [{'outer': [[-0.0934434407535179, -0.21469187499999998], [-0.24155675359712123, -0.21459254500000002], [-0.24155675359712123, -0.137653705], [-0.19347556090630055, -0.137653705], [-0.19347556090630055, -0.078645765], [-0.1548318124009248, -0.078645765], [-0.1548318124009248, -0.137653705], [-0.08774092314027511, -0.137653705], [-0.07416665094416083, 0.045727945], [-0.06646770963532837, 0.045727945], [-0.06646770963532837, 0.18316480499999999], [0.06645095941491555, 0.18316480499999999], [0.06645095941491555, 0.045727945], [0.07419955137709104, 0.045727945], [0.08775360181721334, -0.137653705], [0.2415400033767084, -0.137653705], [0.2415400033767084, -0.21459254500000002], [0.09344762432161723, -0.21469187499999998], [0.2415400033767084, -0.21469187499999998], [0.2415400033767084, -0.345685985], [0.251542685, -0.345685985], [0.251542685, -0.408219605], [-0.251542685, -0.408219605], [-0.251542685, -0.345685985], [-0.24155675359712123, -0.345685985], [-0.24155675359712123, -0.21469187499999998]], 'holes': []}, {'outer': [[-0.07480329264786867, 0.354725035], [-8.375110206415988e-06, 0.408219605], [0.0747864828690244, 0.354725035], [0.07534200641042886, 0.354725035], [0.07534200641042886, 0.18733707500000002], [-0.07535881663163124, 0.18733707500000002], [-0.07535881663163124, 0.354725035]], 'holes': []}], 'simplify_tolerance': 0.000163287842, 'sketch_entity_count': 33}
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
