#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.11430557999999999, -0.06717563, -0.008533884999999998], 'basis': [[0.0, 0.9760929292929786, -0.21735361369034603], [-0.9219700466763561, -0.08417262014127098, -0.37800291407626874], [-0.38726119484347726, 0.200393521359363, 0.8999284435807088]], 'axis': [-0.21735361369034603, -0.37800291407626874, 0.8999284435807088], 'zmin': -0.06887048285081061, 'zmax': 0.07803463434165898, 'profiles': [{'outer': [[-0.04709968830903233, 0.01746487085473689], [-0.03796083296299199, 0.03143023195580198], [-0.02377760976330695, 0.04121780818944102], [-0.006501632429431487, 0.04565674153885012], [-0.003267906978595574, 0.046577594163109436], [0.01379364021268436, 0.04556935539927495], [0.029836784612259117, 0.03919604937232773], [0.042930384775754754, 0.02816548140056191], [0.04516341559872949, 0.024365538122410994], [0.0539734325795853, 0.010287467401048378], [0.05740668642782635, -0.006544550540391891], [0.05440552736888061, -0.022878901754486793], [0.04526667202284026, -0.036791475749935715], [0.031110533871122573, -0.04659305774552933], [0.013611260029096192, -0.051121192089499674], [-0.0050639225108067365, -0.049795181882135886], [-0.022653262141515813, -0.042764721302337404], [-0.0371514239467576, -0.030958477415856785], [-0.046667584300036556, -0.015701526741859956], [-0.05014806532668032, 0.0011261916428411756]], 'holes': []}], 'simplify_tolerance': 2.1510950350901336e-05, 'sketch_entity_count': 35}
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
