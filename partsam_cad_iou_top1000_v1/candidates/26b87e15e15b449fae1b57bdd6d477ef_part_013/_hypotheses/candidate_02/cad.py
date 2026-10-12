#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.175373055, -0.38736844000000004, -0.17692912], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.050204219999999966, 'zmax': 0.05020422000000002, 'profiles': [{'outer': [[-0.04633684000000002, 0.023137565], [-0.04601799000000001, 0.025091835000000007], [-0.04089572999999999, 0.041960305], [-0.03249236999999999, 0.057995624999999995], [-0.023194149999999997, 0.070369255], [-0.014327919999999994, 0.078865205], [-0.008156550000000012, 0.082969175], [-0.007858260000000006, 0.083133745], [-0.004679989999999995, 0.084254885], [-0.0012137299999999962, 0.08343202499999999], [0.005831929999999985, 0.079760055], [0.014883309999999983, 0.072878945], [0.025292389999999998, 0.06182188499999999], [0.026207809999999998, 0.060608175], [0.036442050000000004, 0.045405995000000005], [0.043446559999999995, 0.029082665000000008], [0.04690253999999999, 0.015248464999999989], [0.04846596, 0.003203965000000003], [0.048239669999999985, -0.008943375000000003], [0.04633682, -0.023137565], [0.04601796, -0.025091835000000007], [0.040906, -0.041960305], [0.03249234000000001, -0.057995624999999995], [0.023194119999999985, -0.070358965], [0.014327900000000005, -0.078865195], [0.007858219999999999, -0.08313374499999998], [0.004690250000000007, -0.084254885], [0.001223969999999991, -0.08343204500000001], [-0.005831969999999992, -0.079760035], [-0.014883339999999995, -0.072878945], [-0.025282109999999997, -0.061821875], [-0.026207830000000015, -0.060608174999999986], [-0.036442050000000004, -0.045405995000000005], [-0.04344657000000002, -0.029082665000000008], [-0.04690253, -0.015248475000000011], [-0.04846596, -0.0032039849999999925], [-0.04823967000000001, 0.008943375000000003]], 'holes': []}], 'simplify_tolerance': 3.3701954000000004e-05, 'sketch_entity_count': 46}
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
