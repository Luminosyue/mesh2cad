#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.23105614, 0.23382748999999997, 0.126634825], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.0991389, 'zmax': 0.0991389, 'profiles': [{'outer': [[-0.091029355, 0.05604361000000002], [-0.07383304499999999, 0.06259970000000004], [-0.08645256499999998, 0.09570025000000004], [0.0015003550000000088, 0.12923212], [0.014119875669829498, 0.09613159447268452], [0.031316175, 0.10268764000000002], [0.04476645500000001, 0.10502360000000005], [0.058033475, 0.10211788000000005], [0.06910432500000001, 0.09440826000000002], [0.07627737500000001, 0.08307676000000003], [0.111287045, -0.008752359999999959], [0.113714695, -0.02340341999999998], [0.11024344500000001, -0.03790820999999997], [0.101430325, -0.05008630999999997], [0.08859498298023175, -0.05807676635595654], [0.092497745, -0.05658884999999997], [0.10229375500000001, -0.08228340999999997], [-0.020850994999999983, -0.12923211999999998], [-0.030647005000000005, -0.10353755999999997], [-0.026757553495009512, -0.10205470666616447], [-0.041641364999999986, -0.10463212999999996], [-0.056338305000000005, -0.10141719999999996], [-0.06857148499999999, -0.09289969999999997], [-0.076513685, -0.08035103999999998], [-0.11152337499999998, 0.011478050000000017], [-0.113714695, 0.024708850000000004], [-0.110586255, 0.03783194000000001], [-0.10262095499999999, 0.04883243000000004]], 'holes': []}], 'simplify_tolerance': 5.1692848000000006e-05, 'sketch_entity_count': 28}
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
