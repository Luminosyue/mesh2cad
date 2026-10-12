#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.01342949, 0.019580655000000002, -0.388554465], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.076843015, 'zmax': 0.076843015, 'profiles': [{'outer': [[-0.009181934999999974, -0.013347600000000001], [-0.009181934999999974, 0.0010514099999999992], [-0.005653454999999974, 0.0010514099999999992], [-0.005653454999999974, 0.0028702979473931227], [-0.005752014999999999, 0.002990249999999998], [-0.005752014999999999, 0.004074259999999998], [-0.006864654999999997, 0.004074259999999998], [-0.007281474999999982, 0.004138149999999998], [-0.009820094999999973, 0.004932199999999999], [-0.010028614999999963, 0.005288159999999998], [-0.010028614999999963, 0.00603657], [-0.009820094999999973, 0.006383399999999999], [-0.007281474999999982, 0.00718658], [-0.006864654999999997, 0.00725047], [-0.006424235, 0.007251309999999999], [-0.005752014999999999, 0.00725132], [-0.005752014999999999, 0.008334409999999999], [-0.005517824999999976, 0.008619429999999999], [-0.004110954999999972, 0.008619549999999998], [-0.0022319149999999732, 0.008619549999999998], [-0.0022319149999999732, 0.01049631], [-0.004049584999999967, 0.01049631], [-0.004049584999999967, 0.0133476], [0.004896355000000019, 0.0133476], [0.004896355000000019, 0.01049631], [0.003114265000000005, 0.01049631], [0.003114265000000005, 0.00861954], [0.005081155000000004, 0.008619429999999999], [0.005296155000000025, 0.008334409999999999], [0.005296155000000025, 0.007250501785740671], [0.005344495000000005, 0.007250499999999998], [0.005751055000000005, 0.00716836], [0.0075450820969079875, 0.006485441314273671], [0.007874144999999999, 0.006383450000000001], [0.008074475000000025, 0.006036629999999999], [0.008074475000000025, 0.00528821], [0.007874144999999999, 0.00494138], [0.007563204562921911, 0.0048510908714074555], [0.006500135000000018, 0.0044382286890202755], [0.006500135000000018, 0.0010514099999999992], [0.010028615000000018, 0.0010514099999999992], [0.010028615000000018, -0.013347600000000001]], 'holes': []}], 'simplify_tolerance': 5.33904e-06, 'sketch_entity_count': 54}
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
