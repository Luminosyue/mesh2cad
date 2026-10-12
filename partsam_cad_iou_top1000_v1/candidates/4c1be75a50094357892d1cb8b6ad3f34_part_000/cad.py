#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0, -0.063747, -5.100000000091143e-07], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.054714, 'zmax': 0.054714, 'profiles': [{'outer': [[-0.27357548, 0.113319], [-0.26114949, 0.139588], [-0.24621147999999998, 0.16451301], [-0.22889948, 0.18785401], [-0.20938547999999998, 0.20938601], [-0.18785348, 0.2289], [-0.16451248, 0.24621201], [-0.13958747, 0.26115], [-0.11331847999999999, 0.27357599], [-0.08595747999999999, 0.28336501], [-0.05776847999999999, 0.290427], [-0.02902347999999999, 0.294689], [5.200000000091143e-07, 0.29611599], [0.02902452000000001, 0.294689], [0.05776952000000001, 0.290427], [0.08595851000000002, 0.28336501], [0.11331952, 0.27357599], [0.13958852000000002, 0.26115], [0.16451353000000002, 0.24621201], [0.18785453000000002, 0.2289], [0.20938653000000002, 0.20938601], [0.22890053000000002, 0.18785401], [0.24621253, 0.16451301], [0.26115051, 0.139588], [0.2735765, 0.113319], [0.28336552, 0.085958], [0.29042751, 0.057769], [0.29468951, 0.029024], [0.2961165, 0.0], [0.29468951, -0.029024], [0.29042751, -0.05777], [0.28336552, -0.085958], [0.2735765, -0.113319], [0.26115051, -0.139588], [0.24621253, -0.16451401], [0.22890053000000002, -0.18785401], [0.20938653000000002, -0.20938601], [0.18785352, -0.2289], [0.16451353000000002, -0.24621201], [0.13958852000000002, -0.26115099], [0.11331952, -0.27357599], [0.08595851000000002, -0.28336501], [0.05776952000000001, -0.290427], [0.02902452000000001, -0.294689], [5.200000000091143e-07, -0.29611599], [-0.02902447999999999, -0.294689], [-0.05776947999999999, -0.290427], [-0.08595747999999999, -0.28336501], [-0.11331847999999999, -0.27357599], [-0.13958747, -0.26115], [-0.16451348, -0.24621201], [-0.18785348, -0.2289], [-0.20938547999999998, -0.20938601], [-0.22889948, -0.18785299], [-0.24621147999999998, -0.16451301], [-0.26115048, -0.139587], [-0.27357548, -0.113318], [-0.28336449999999996, -0.085957], [-0.29042649, -0.057769], [-0.2946895, -0.029024], [-0.2961165, 0.0], [-0.29468848999999997, 0.029024], [-0.29042649, 0.057769], [-0.28336449999999996, 0.085958]], 'holes': []}], 'simplify_tolerance': 0.00011844660000000001, 'sketch_entity_count': 64}
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
