#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [2.7199999999977242e-06, -0.046236815, 2.799999999997249e-06], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.022796584999999994, 'zmax': 0.022796585, 'profiles': [{'outer': [[-0.24994758, -0.0476776], [-0.25361177, -0.023958899999999998], [-0.25483316, 2.275554012798678e-18], [-0.25361177, 0.023928860000000003], [-0.24994758, 0.047647560000000005], [-0.24387193, 0.0709159], [-0.23544744, 0.09349371000000001], [-0.22473673, 0.1151708], [-0.21189643, 0.13573699], [-0.19698912999999998, 0.15498219000000002], [-0.18020278, 0.17275620000000003], [-0.16166264, 0.1888489], [-0.1415879, 0.20314015000000002], [-0.12013519, 0.21544986], [-0.09752372, 0.22568792999999998], [-0.07397271, 0.23376430999999998], [-0.04973271, 0.23958888], [-0.024991629999999997, 0.24313172], [2.7507394962083404e-18, 0.24430264000000002], [0.024960310000000003, 0.24313172], [0.049701390000000005, 0.23958888], [0.0739727, 0.23376430999999998], [0.09752371, 0.22568792999999998], [0.12013518000000001, 0.21544986], [0.14158788, 0.20314015000000002], [0.16166262, 0.1888489], [0.18020277, 0.17275620000000003], [0.19698914, 0.15498219000000002], [0.21189641, 0.13573699], [0.22473671, 0.1151708], [0.2354161, 0.09349371000000001], [0.24384061, 0.0709159], [0.24991624, 0.047647560000000005], [0.25361177, 0.023928860000000003], [0.25483316, 2.275554012798678e-18], [0.25361177, -0.023958899999999998], [0.24991624, -0.0476776], [0.24384061, -0.07091592], [0.2354161, -0.09349372], [0.22473671, -0.11517082], [0.21189641, -0.13573703999999998], [0.19698914, -0.15498222], [0.18020277, -0.17275623], [0.16166262, -0.18884890999999998], [0.14158788, -0.20314019], [0.12013518000000001, -0.21544988999999998], [0.09752371, -0.22571799999999997], [0.0739727, -0.23379434999999998], [0.049701390000000005, -0.23961894], [0.024960310000000003, -0.24313172], [2.7507394962083404e-18, -0.24430264000000002], [-0.024991629999999997, -0.24313172], [-0.04973271, -0.23961894], [-0.07397271, -0.23379434999999998], [-0.09752372, -0.22571799999999997], [-0.12013519, -0.21544988999999998], [-0.1415879, -0.20314019], [-0.16166264, -0.18884890999999998], [-0.18020278, -0.17275623], [-0.19698912999999998, -0.15498222], [-0.21189643, -0.13573703999999998], [-0.22473673, -0.11517082], [-0.23544744, -0.09349372], [-0.24387193, -0.07091592]], 'holes': []}], 'simplify_tolerance': 0.000101933264, 'sketch_entity_count': 67}
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
