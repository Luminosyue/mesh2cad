#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.41116002, 0.2347032, -0.1023561], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.04816891000000001, 'zmax': 0.04816891000000001, 'profiles': [{'outer': [[-0.046812909999999985, 0.02702409], [-0.04288021, 0.032896729999999985], [-0.03821509000000001, 0.038215129999999986], [-0.03289671999999999, 0.04288023999999996], [-0.027024069999999983, 0.04681291999999998], [-0.020682939999999997, 0.04992742], [-0.013985479999999995, 0.05219731], [-0.007050479999999998, 0.05358297000000001], [3.300000000011627e-06, 0.054051459999999996], [0.007050480000000012, 0.05358297000000001], [0.013985490000000003, 0.05219731], [0.02068294000000001, 0.04992742], [0.027024080000000006, 0.04681291999999998], [0.03289673, 0.04288023999999996], [0.0382151, 0.038215129999999986], [0.042880220000000004, 0.032896729999999985], [0.04681292000000001, 0.02702409], [0.049927400000000004, 0.020682959999999972], [0.052197280000000006, 0.01398548999999999], [0.053582960000000006, 0.007050489999999965], [0.05405145000000001, -3.310000000034119e-06], [0.053582960000000006, -0.007050480000000026], [0.052197280000000006, -0.013985479999999995], [0.049927400000000004, -0.02068292999999999], [0.04681292000000001, -0.02702409], [0.042880220000000004, -0.03289673000000004], [0.0382151, -0.0382151], [0.03289673, -0.042880240000000014], [0.027024080000000006, -0.046812920000000036], [0.02068294000000001, -0.049927410000000005], [0.013985490000000003, -0.05219731], [0.007050480000000012, -0.05358296000000001], [3.300000000011627e-06, -0.054051459999999996], [-0.007050479999999998, -0.05358296000000001], [-0.013985479999999995, -0.05219731], [-0.020682939999999997, -0.049927410000000005], [-0.027024069999999983, -0.046812920000000036], [-0.03289671999999999, -0.042880240000000014], [-0.03821509000000001, -0.0382151], [-0.04288021, -0.03289673000000004], [-0.046812909999999985, -0.02702409], [-0.04992738999999999, -0.02068292999999999], [-0.052197279999999985, -0.013985479999999995], [-0.053582959999999985, -0.007050480000000026], [-0.05405145, 3.309999999978608e-06], [-0.053582959999999985, 0.007050489999999965], [-0.052197279999999985, 0.01398548999999999], [-0.04992738999999999, 0.020682959999999972]], 'holes': []}], 'simplify_tolerance': 2.1620584e-05, 'sketch_entity_count': 57}
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
