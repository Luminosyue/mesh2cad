#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.233418285, -0.1686378, -0.07462521999999999], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.047934685000000005, 'zmax': 0.04793468499999998, 'profiles': [{'outer': [[-0.10612185999999998, 0.04395628], [-0.08123037, 0.08123041], [-0.04395622999999999, 0.10612189000000001], [-6.979999999989772e-06, 0.11487247], [0.04395629000000001, 0.10612186], [0.08123042, 0.08123037000000001], [0.10612190000000002, 0.043956220000000004], [0.11487247, 6.980000000017528e-06], [0.10612187000000001, -0.04395631], [0.08123038000000002, -0.08123041], [0.043956220000000004, -0.10612190999999999], [-7.039999999985946e-06, -0.11487247], [-0.04395629999999999, -0.10612188], [-0.08123040999999999, -0.08123037999999999], [-0.10612189, -0.043956229999999985], [-0.11487246999999999, -6.989999999984509e-06]], 'holes': [[[-0.10073689, 0.04172658000000001], [-0.10504802802101464, 0.020054400861654206], [-0.10073465999999999, 0.041724890000000014], [-0.07710676, 0.07710681], [-0.04172482999999999, 0.10073470000000001], [-0.019586894832598525, 0.10514249894093573], [-0.041726509999999994, 0.10073691], [-0.0771075, 0.07710754]], [[-0.10518907795212952, -0.01935288400789391], [-0.10073692, -0.041726529999999984], [-0.07710753999999999, -0.0771075], [-0.04172656999999999, -0.10073690000000002], [-0.019112052920599292, -0.10523700651164151], [-0.041724889999999994, -0.10073462999999999], [-0.07710681, -0.07710676], [-0.10073468999999999, -0.04172481]], [[0.019726549727001517, -0.10511325910328725], [0.04172652, -0.10073693], [0.07710749, -0.07710755999999999], [0.10073689, -0.04172659000000001], [0.1050660976677647, -0.019963574377314042], [0.10073465000000001, -0.04172487], [0.07710675, -0.07710679000000001], [0.04172482000000001, -0.10073465999999998]], [[0.07710679000000001, 0.07710677], [0.10073468000000002, 0.04172482999999999], [0.10518677085757008, 0.019364467962443302], [0.10073692000000001, 0.04172652000000002], [0.07710755, 0.07710749], [0.04172658000000001, 0.10073688], [0.02018914182974001, 0.10502121570186136], [0.041724880000000006, 0.10073467]]]}], 'simplify_tolerance': 4.5948988000000004e-05, 'sketch_entity_count': 48}
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
