#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.003627474999999998, 0.387350265, -0.17201771500000002], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.10615530500000003, 'zmax': 0.10615530499999998, 'profiles': [{'outer': [[-0.05193906499999998, -0.064099185], [-0.06644790499999997, -0.064099185], [-0.06644790499999997, -0.058764085], [-0.09213442499999996, -0.058764085], [-0.09213442499999996, -0.019401514999999998], [-0.106591235, -0.019401514999999998], [-0.106591235, 0.024905775], [-0.09213442499999996, 0.024905775], [-0.09213442499999996, 0.058855175], [-0.06644790499999997, 0.058855175], [-0.06644790499999997, 0.06409917500000001], [-0.05193906499999998, 0.06409917500000001], [-0.05193906499999998, 0.06439846499999999], [-0.03661044499999999, 0.06439846499999999], [-0.03661044499999999, 0.06409917500000001], [-0.022101604999999996, 0.06409917500000001], [-0.022101604999999996, 0.058855175], [0.0047430350000000066, 0.058855175], [0.08398866500000002, 0.039661855], [0.0896569154951845, 0.03089886186201391], [0.09407327500000001, 0.029147825000000002], [0.09407327500000001, 0.024071265222017763], [0.097321418838637, 0.019049704831673477], [0.10328607500000002, 0.017371575], [0.10659123500000002, 0.013676055000000003], [0.10659123500000002, -0.013584964999999997], [0.10328607500000002, -0.017267485], [0.09732964135522747, -0.018945903177777272], [0.09407327500000001, -0.023980177798648507], [0.09407327500000001, -0.029056734999999997], [0.08965972879840582, -0.030803428381329438], [0.08398866500000002, -0.039570774999999996], [0.0047430350000000066, -0.058764085], [-0.022101604999999996, -0.058764085], [-0.022101604999999996, -0.064099185], [-0.03661044499999999, -0.064099185], [-0.03661044499999999, -0.06439846499999999], [-0.05193906499999998, -0.06439846499999999]], 'holes': []}], 'simplify_tolerance': 4.263649400000001e-05, 'sketch_entity_count': 38}
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
