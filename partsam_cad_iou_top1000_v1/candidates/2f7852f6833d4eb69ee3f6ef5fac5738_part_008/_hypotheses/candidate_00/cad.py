#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.015260485, -0.382072685, 0.011379405000000002], 'basis': [[-0.21480710558149765, -0.002635357944807831, 0.9766529384997529], [0.0, 0.9999963594555933, 0.0026983468198215755], [-0.9766564940610897, 0.0005796240702209116, -0.21480632356669088]], 'axis': [0.9766529384997529, 0.0026983468198215755, -0.21480632356669088], 'zmin': -0.05314365665867969, 'zmax': 0.05447641039041341, 'profiles': [{'outer': [[-0.085539361657444, -0.0718245018892959], [-0.02998422482851643, -0.04681650787551567], [-0.007457707833811491, -0.03420757734858264], [-0.02941988278077631, 0.022450794960720343], [-0.05229929408959872, 0.04179177042309998], [-0.06488303961324256, 0.0949417803553132], [-0.03447876734121201, 0.10082881853176806], [0.026155095026631756, 0.1123281500724685], [0.05639931328865495, 0.11792545478212729], [0.06898306096036985, 0.06477547487615842], [0.06657461893542316, 0.0406368637254772], [0.10239065054887699, -0.03603715873372312], [0.10239065054887699, -0.11792852060349832], [0.07833194133297312, -0.11804306860364402], [-0.024176871632340374, -0.11806934493271551], [-0.07866072527288491, -0.11804243646471325], [-0.10259032879001238, -0.11792770050693234]], 'holes': []}], 'simplify_tolerance': 4.7198959942968564e-05, 'sketch_entity_count': 20}
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
