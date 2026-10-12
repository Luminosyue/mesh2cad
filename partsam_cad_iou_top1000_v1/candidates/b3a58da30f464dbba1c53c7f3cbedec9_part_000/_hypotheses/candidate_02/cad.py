#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.04565291, 0.40542519, -1.1999999999234845e-07], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.26171476, 'zmax': 0.26171476, 'profiles': [{'outer': [[-0.09413939999999998, 0.002987280000000002], [-0.09273362000000002, 0.00586275], [-0.09052909000000003, 0.008163110000000001], [-0.08771752999999999, 0.00966475], [-0.08455455, 0.010207890000000004], [-0.08238196000000003, 0.010271780000000001], [-0.07618374, 0.010048140000000004], [-0.07070765540400707, 0.009984831632801077], [-0.05116731000000002, 0.010112040000000003], [-0.0026998325441446856, 0.01008009018214123], [0.015671129999999978, 0.010271780000000001], [0.03234893, 0.010239830000000005], [0.04647058075588744, 0.010016200938183898], [0.052689699022179196, 0.01011223569047326], [0.060304639999999965, 0.016438050000000003], [0.06187016000000001, 0.017109000000000006], [0.06509721000000002, 0.01714094], [0.06757866448067096, 0.01705913408969606], [0.08765363999999998, 0.01714094], [0.08912331000000001, 0.016533900000000004], [0.09436303000000001, 0.008834060000000005], [0.09455471999999998, 1.5979999999998773e-05], [0.09458666999999998, -0.008834059999999998], [0.08925116, -0.016501949999999998], [0.08778143, -0.017140939999999997], [0.06753225764170682, -0.017058280168774483], [0.06199800999999999, -0.017108989999999998], [0.060432490000000005, -0.01643805], [0.05230868125378792, -0.010108772673415157], [0.04640668078307174, -0.010016190796609916], [0.032157239999999976, -0.010207879999999996], [0.015479440000000011, -0.010271789999999996], [-0.002795700000000012, -0.010080079999999998], [-0.03726924000000004, -0.010112039999999996], [-0.07068847357506389, -0.009984609873942346], [-0.07618374, -0.010048139999999997], [-0.08238196000000003, -0.010271789999999996], [-0.08413916999999999, -0.010239829999999998], [-0.08733410000000003, -0.00976059], [-0.0902096, -0.00838676], [-0.09250998999999999, -0.006150289999999996], [-0.09401161000000002, -0.003338729999999998], [-0.09458666999999998, -0.00020767000000000008]], 'holes': []}], 'simplify_tolerance': 3.7834668e-05, 'sketch_entity_count': 55}
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
