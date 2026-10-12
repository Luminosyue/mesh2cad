#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [2.0669999999998676e-05, 0.116165665, 0.23128313500000003], 'basis': [[-0.0, 0.9999999296448956, 0.00037511358802608746], [0.2597852438396535, -0.0003622345941600934, 0.965666348108533], [0.9656664160480947, 9.744897493292446e-05, -0.25978522556243555]], 'axis': [0.00037511358802608746, 0.965666348108533, -0.25978522556243555], 'zmin': -0.018010596299624836, 'zmax': 0.013953213086123073, 'profiles': [{'outer': [[-0.03694338418374114, -2.0752449581282447e-05], [-0.035675201245765245, 0.003923620590597492], [-0.03511027175827041, 0.004558841606867337], [-0.029889700043249725, 0.0086719257291836], [-0.021853282434924962, 0.012021783478431552], [-0.005151864495383085, 0.015796048522775743], [0.010850342288924966, 0.017577308978053808], [0.02143966501260481, 0.015838842372450146], [0.02904624503654472, 0.011937781377023053], [0.031073631495701713, 0.01019723179709387], [0.03518137982887332, 0.005448969617341329], [0.03598887810987878, 0.00315840121471755], [0.036302099451148394, -2.222284505586793e-05], [0.03598887810987878, -0.0031598183407634227], [0.03518137982887332, -0.005491289612955537], [0.031073631495701713, -0.010199146767916688], [0.02904624503654472, -0.011935756943351547], [0.02143966501260481, -0.015879435396006954], [0.010850342288924966, -0.017575728548750388], [-0.005151864495383085, -0.015795029254630524], [-0.021853282434924962, -0.012021334830012229], [-0.029889700043249725, -0.008671353050628123], [-0.03511027175827041, -0.004600457748729155], [-0.035675201245765245, -0.003921138857483599]], 'holes': []}], 'simplify_tolerance': 1.4649096726977907e-05, 'sketch_entity_count': 24}
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
