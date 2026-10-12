#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.07322263, 0.058697785, 0.21169613], 'basis': [[0.0, 0.9996491648703137, 0.026486735814070395], [-0.1240206835189058, -0.026282248492858817, 0.9919315064426895], [0.9922796329964166, -0.003284903079845692, 0.12397717270631968]], 'axis': [0.026486735814070395, 0.9919315064426895, 0.12397717270631968], 'zmin': -0.015884943564987812, 'zmax': 0.019237022686543984, 'profiles': [{'outer': [[-0.030204267888972618, 0.07593569376159501], [0.0010090367162021296, 0.08190450841516185], [0.03233124741431689, 0.07563557719640841], [0.05907213553536524, 0.057965736335180394], [0.07711726838239491, 0.03164946504984587], [0.08360789406160601, 0.0007833978128355492], [0.07746483492015463, -0.029879741591664028], [0.0597880633499104, -0.05592182123936369], [0.033067949750529756, -0.07396679284329076], [0.0009779291071144469, -0.08151024099904661], [-0.03111209842046461, -0.07623140289854533], [-0.058195407280368205, -0.05886718788707117], [-0.07607451841160333, -0.03213044641332359], [-0.08205674876973253, -7.837385697430332e-05], [-0.07497986652486487, 0.032219423402742295], [-0.056696095373709884, 0.058649906419606074]], 'holes': []}], 'simplify_tolerance': 3.313292856626771e-05, 'sketch_entity_count': 16}
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
