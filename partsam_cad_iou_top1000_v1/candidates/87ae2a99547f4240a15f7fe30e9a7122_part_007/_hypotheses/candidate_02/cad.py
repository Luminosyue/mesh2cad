#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.033998915000000005, -0.45354258999999997, -0.08679538], 'basis': [[0.0, 0.9147724751566535, 0.4039694526765233], [-0.9999999984881269, -2.2213714985273483e-05, 5.03020584969196e-05], [5.498860084121513e-05, -0.4039694520657727, 0.9147724737736336]], 'axis': [0.4039694526765233, 5.03020584969196e-05, 0.9147724737736336], 'zmin': -0.04637156752813554, 'zmax': 0.04622732224385253, 'profiles': [{'outer': [[-0.024576475483205906, 0.07437672164926298], [-0.009567431785832067, 0.08275835646912932], [0.0064501789683279, 0.08542390311875563], [0.02083285079167764, 0.08489833230871496], [0.031377553846106986, 0.08294315558802359], [0.03829973043379386, 0.07814777360245573], [0.04243167901108475, 0.06831119193853871], [0.04473291910366205, 0.05120667800109685], [0.04602583332544437, 0.025799368417042917], [0.04645725983942439, -0.0042017145967489945], [0.046027159356857535, -0.033891657951310016], [0.04473535366182717, -0.05839139613620309], [0.042434840920519676, -0.07401876393700108], [0.038303289131074496, -0.08204527633445391], [0.031381283746547146, -0.08495615801232723], [0.020836631838665097, -0.08531128622854711], [0.006453960554753532, -0.08481656352187604], [-0.009563779949409207, -0.08162980220247178], [-0.024573200513358453, -0.07305599411106227], [-0.03655749928563991, -0.056455702239815136], [-0.04396967480382706, -0.030553477240330845], [-0.0464571882343681, 0.0006752931189421588], [-0.04397106221076705, 0.0318991731996405], [-0.03656003775026519, 0.0578106750206075]], 'holes': []}], 'simplify_tolerance': 3.4147037869460555e-05, 'sketch_entity_count': 27}
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
