#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.131193155, -0.371129495, 0.0035348400000000044], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.056570814999999997, 'zmax': 0.056570814999999997, 'profiles': [{'outer': [[-0.09391070000000001, -0.010865305000000006], [-0.0925079, -0.008671815], [-0.08457573000000002, 0.002524995000000002], [-0.07613344999999999, 0.009487944999999998], [-0.06837984, 0.014384974999999994], [-0.05708097, 0.021220424999999987], [-0.04570558, 0.028285375], [-0.020735850000000004, 0.04409871499999998], [-0.010431680000000004, 0.05055156499999999], [0.0008926899999999955, 0.057463505], [0.013058749999999994, 0.06470704499999999], [0.025224799999999995, 0.07136393499999999], [0.02919724719652449, 0.0729462365638553], [0.03836004, 0.07682207499999999], [0.03922725, 0.07702614499999999], [0.047014489718581076, 0.07846353162405305], [0.053484729999999994, 0.079857225], [0.06608436000000001, 0.07774025500000001], [0.07802087999999999, 0.069655085], [0.08809548, 0.057234015], [0.0948544, 0.04277244499999999], [0.09686932000000001, 0.028489495000000004], [0.09327309, 0.016246924999999995], [0.09099151996787634, 0.013337570633285561], [0.08388710999999999, 0.003953344999999997], [0.07322587, -0.005458144999999998], [0.061926989999999994, -0.013466825000000002], [0.050067009999999995, -0.02122043500000001], [0.03892117, -0.028387455000000006], [0.0285915, -0.034840305], [0.007626099999999995, -0.04772050500000001], [-0.007881150000000003, -0.057463525], [-0.02121160046384505, -0.06630509009413031], [-0.026653090000000004, -0.07013967500000001], [-0.031532462861269324, -0.07263450019759801], [-0.036957260000000006, -0.07569983500000001], [-0.03976289062263291, -0.07659573139901762], [-0.04513098315141099, -0.07847259391363763], [-0.04876623000000001, -0.079857225], [-0.06047318, -0.078173875], [-0.07302182000000002, -0.069170485], [-0.08467775999999999, -0.05501502500000001], [-0.09329856, -0.038666105000000006], [-0.09686932000000001, -0.023209855]], 'holes': []}], 'simplify_tolerance': 3.8747728000000005e-05, 'sketch_entity_count': 44}
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
