#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.04428899, -0.43273970500000003, -0.206454835], 'basis': [[0.0, 0.9999999999951386, 3.118138728438339e-06], [-0.5000286933801413, -2.7003356938815754e-06, 0.8660088370156837], [0.8660088370198936, -1.5591588341590374e-06, 0.5000286933777105]], 'axis': [3.118138728438339e-06, 0.8660088370156837, 0.5000286933777105], 'zmin': -0.07047015767882686, 'zmax': 0.07012436678144914, 'profiles': [{'outer': [[-0.008743066229902821, 0.013007866021639334], [-0.0031032723455503433, 0.015330096047016606], [0.0030186888726638967, 0.015330126589319292], [0.008641577148548268, 0.013007896523672194], [0.012939123557237375, 0.008666336004748382], [0.015276891321949398, 0.0030459060372495304], [0.015276891321949398, -0.0030457039627208595], [0.012939123557237375, -0.008666143995167352], [0.008641577148548268, -0.0129740034762015], [0.0030186888726638967, -0.015329873410531653], [-0.0031032723455503433, -0.01532990395283434], [-0.008743066229902821, -0.01297403397823436], [-0.013055238224433828, -0.00866614396983091], [-0.015376165022752814, -0.0030457039113847505], [-0.015376165022752814, 0.0030459060885856394], [-0.013055238224433828, 0.008666336030084825]], 'holes': []}], 'simplify_tolerance': 6.132006108430727e-06, 'sketch_entity_count': 16}
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
