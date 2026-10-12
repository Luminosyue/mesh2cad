#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0, -0.11262039500000001, 0.019146830000000004], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.12595756, 'zmax': 0.12595756, 'profiles': [{'outer': [[-0.47946519, -0.03603467499999999], [-0.48085314, -0.028747914999999985], [-0.48085311, 0.028748075000000012], [-0.47946516, 0.03603484500000001], [-0.47557887, 0.03950473500000001], [-0.47099864, 0.039955825000000014], [0.07790256000000001, 0.03995564500000001], [0.08244807, 0.039504565000000005], [0.08623028, 0.036034675000000016], [0.08761823, 0.028747905000000018], [0.08761823, -0.028748095], [0.08623028, -0.03603485499999998], [0.08244807, -0.03950474499999998], [0.07790256000000001, -0.039955825], [-0.47099864, -0.039955644999999984], [-0.47557889999999997, -0.03950456499999999]], 'holes': []}, {'outer': [[0.09299070000000001, -0.028681235], [0.09299070000000001, 0.028682525000000014], [0.09426910000000001, 0.03554818500000001], [0.09734684, 0.038365465000000015], [0.10151362, 0.03876793500000002], [0.47233027, 0.038767825000000006], [0.47649699, 0.03836535500000002], [0.47957468000000003, 0.03554806500000002], [0.48085314, 0.028682405000000008], [0.48085314, -0.02868135499999999], [0.47957468000000003, -0.03554702499999998], [0.47649699, -0.03836430499999999], [0.47233027, -0.038766774999999976], [0.10151362, -0.03876665499999998], [0.09734684, -0.03836419499999999], [0.09426910000000001, -0.03554690499999999]], 'holes': []}], 'simplify_tolerance': 0.00019234125600000001, 'sketch_entity_count': 44}
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
