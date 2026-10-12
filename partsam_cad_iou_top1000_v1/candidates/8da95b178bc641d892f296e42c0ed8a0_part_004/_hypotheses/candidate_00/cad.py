#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.260870545, -0.37038678, 0.3281135], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.1005193, 'zmax': 0.10051929999999998, 'profiles': [{'outer': [[-0.12961286000000002, 0.02579701499999998], [-0.10988575, 0.07341417499999997], [-0.07341415000000001, 0.10988578500000001], [-0.02579701000000001, 0.129612895], [0.025797009999999954, 0.129612895], [0.07341414999999996, 0.10988578500000001], [0.10988574999999995, 0.07341417499999997], [0.12961286, 0.02579701499999998], [0.12961286, -0.025796995000000017], [0.10988574999999995, -0.073414165], [0.07341414999999996, -0.109885755], [0.025797009999999954, -0.129612895], [-0.02579701000000001, -0.129612895], [-0.07341415000000001, -0.109885755], [-0.10988575, -0.073414165], [-0.12961286000000002, -0.025796995000000017]], 'holes': [[[-0.015802590000000005, 0.07953637499999999], [-0.04505313000000005, 0.06744894499999998], [-0.06739658000000004, 0.045053184999999996], [-0.07953632000000005, 0.015802625000000015], [-0.07953632000000005, -0.015802604999999997], [-0.06739658000000004, -0.045053165000000006], [-0.04505313000000005, -0.06739662500000002], [-0.015802590000000005, -0.079536365], [0.015802559999999966, -0.079536365], [0.04505311999999995, -0.06739662500000002], [0.06744890999999997, -0.045053165000000006], [0.07953632, -0.015802604999999997], [0.07953632, 0.015802625000000015], [0.06744890999999997, 0.045053184999999996], [0.04505311999999995, 0.06744894499999998], [0.015802559999999966, 0.07953637499999999]]]}], 'simplify_tolerance': 5.184515800000001e-05, 'sketch_entity_count': 50}
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
