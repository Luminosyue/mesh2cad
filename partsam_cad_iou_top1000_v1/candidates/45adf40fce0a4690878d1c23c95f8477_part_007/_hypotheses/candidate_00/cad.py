#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.046004935000000004, 0.25066173, -0.03050252], 'basis': [[0.0, 0.9245223468919828, 0.3811278395726824], [-0.9999992746812822, 0.0004590394755388824, -0.0011135168024385144], [-0.0012044238910848232, -0.3811275631335265, 0.9245216763186196]], 'axis': [0.3811278395726824, -0.0011135168024385144, 0.9245216763186196], 'zmin': -0.03548995200355926, 'zmax': 0.039135786734165755, 'profiles': [{'outer': [[-0.01249585171720998, 0.001626348761870853], [-0.006241970877470102, 0.012458082218193386], [0.0062835200375502935, 0.012452332519242522], [0.00850429367723592, 0.008642610426827044], [0.012555130112830814, 0.0016148493639691276], [0.012564621310331252, 0.0015762114374125486], [0.01140298244383185, -0.00043531421613685636], [0.010725098068295066, -0.0015852788099311624], [0.009438711564745548, -0.0038347485418003774], [0.007473574849412424, -0.007226946642571722], [0.006283020502741466, -0.009255477747389685], [0.003961104931421629, -0.009258681337872608], [3.520070943714544e-05, -0.009247707149931159], [-0.0038915093729260785, -0.009255076675306203], [-0.00624247041227893, -0.009249728048438823], [-0.012486360519709541, 0.0015877108353142722]], 'holes': []}], 'simplify_tolerance': 5.0120946055082465e-06, 'sketch_entity_count': 16}
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
