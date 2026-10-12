#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0, -0.045095739999999995, -0.10499710500000001], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.23777923, 'zmax': 0.23777923, 'profiles': [{'outer': [[-0.104345945, -0.19382899], [-0.104345945, 0.19382896], [-0.103979705, 0.27647561], [-0.103186215, 0.34184828], [-0.10190438499999999, 0.38622355], [-0.10019531499999998, 0.41326377], [-0.097875825, 0.42870659], [-0.095068035, 0.43804553], [-0.09171088499999999, 0.44610268], [-0.087804415, 0.45379359], [-0.08322649499999998, 0.46105719], [-0.07803817499999999, 0.46789354], [-0.07211741499999999, 0.47430265], [-0.06522002499999999, 0.48016238], [-0.05728497499999999, 0.48547274], [-0.04800706499999999, 0.49023378], [-0.03732527499999999, 0.49420133], [-0.025483724999999985, 0.49731427], [-0.012909714999999988, 0.49926758], [3.0525000000003466e-05, 0.5], [0.012970755, 0.49926758], [0.02554476500000001, 0.49731427], [0.037325275000000005, 0.49420133], [0.04800707500000001, 0.49023378], [0.057284995000000005, 0.48547274], [0.065281065, 0.48016238], [0.07211743500000001, 0.47430265], [0.078038195, 0.46789354], [0.083287545, 0.46105719], [0.087804425, 0.45379359], [0.09177194500000001, 0.44610268], [0.095129085, 0.43804553], [0.09793686500000001, 0.42870659], [0.10019531500000001, 0.41326377], [0.101965445, 0.38622355], [0.103247265, 0.34184828], [0.10397972500000001, 0.27647561], [0.104529065, 0.09976804], [0.10440700500000001, -0.19382899], [0.10397972500000001, -0.27647564], [0.103247265, -0.34184828], [0.101965445, -0.38622355], [0.10019531500000001, -0.41326377], [0.09793686500000001, -0.42870662], [0.095129085, -0.43804553], [0.09177194500000001, -0.44610268], [0.087804425, -0.45379359], [0.083287545, -0.46105722], [0.078038195, -0.46789354], [0.07211743500000001, -0.47430265], [0.065281065, -0.48016238], [0.057284995000000005, -0.48547274], [0.04800707500000001, -0.49023381], [0.037325275000000005, -0.49420133], [0.02554476500000001, -0.4973143], [0.012970755, -0.49926758], [3.0525000000003466e-05, -0.5], [-0.012909714999999988, -0.49926758], [-0.025483724999999985, -0.4973143], [-0.03732527499999999, -0.49420133], [-0.04800706499999999, -0.49023381], [-0.05728497499999999, -0.48547274], [-0.06522002499999999, -0.48016238], [-0.07211741499999999, -0.47430265], [-0.07803817499999999, -0.46789354], [-0.08322649499999998, -0.46105722], [-0.087804415, -0.45379359], [-0.09171088499999999, -0.44610268], [-0.095068035, -0.43804553], [-0.097875825, -0.42870662], [-0.10019531499999998, -0.41326377], [-0.10190438499999999, -0.38622355], [-0.103186215, -0.34184828], [-0.103979705, -0.27647564]], 'holes': []}], 'simplify_tolerance': 0.0002, 'sketch_entity_count': 80}
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
    elif kind == "loft":
        wires = [cq.Wire.makePolygon([vec(p) for p in section], close=True) for section in s["sections"]]
        result = cq.Solid.makeLoft(wires, ruled=bool(s.get("ruled", True)))
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
