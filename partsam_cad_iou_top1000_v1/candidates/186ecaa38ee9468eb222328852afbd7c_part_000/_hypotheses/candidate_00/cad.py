#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [1.0609999999994235e-05, -0.273118925, 0.0], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.022950605000000013, 'zmax': 0.022950605000000013, 'profiles': [{'outer': [[-0.40453506, 0.27443081], [-0.33965075, 0.34084105], [-0.26109374, 0.39467734], [-0.17374712, 0.43349804999999997], [-0.0817005, 0.45419028000000006], [0.01260453, 0.45473957], [0.10745892, 0.43777078], [0.20023799, 0.40975401], [0.28593659, 0.37459558000000004], [0.35936624, 0.33235665999999997], [0.41881818, 0.27455282000000003], [0.46325445, 0.19971921], [0.49084395, 0.11286088000000001], [0.49999982, 0.019715570000000005], [0.49005049, -0.07483363], [0.46136224, -0.16639194], [0.41478956, -0.25123598999999996], [0.3520416, -0.32545924000000004], [0.27525473, -0.38466692], [0.18955615, -0.42635649], [0.09567843, -0.44961231999999995], [-0.00247206, -0.45473957], [-0.1006836, -0.44173828000000004], [-0.19511072, -0.41121885], [-0.28196901, -0.36434099], [-0.35796243, -0.30293590000000004], [-0.41997784, -0.22956717], [-0.46545184, -0.14704261999999999], [-0.49255306, -0.05890246999999999], [-0.49999982, 0.031190900000000004], [-0.4874258, 0.11926997], [-0.45519727, 0.20130621]], 'holes': []}], 'simplify_tolerance': 0.000199999928, 'sketch_entity_count': 35}
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
