#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.080123485, 0.3042264, -0.138619575], 'basis': [[-0.0, 0.8430938408809449, -0.5377664692676701], [1.234228988893302e-05, 0.5377664692267106, 0.8430938408167299], [0.999999999923834, -6.637269656249573e-06, -1.0405708587726592e-05]], 'axis': [-0.5377664692676701, 0.8430938408167299, -1.0405708587726592e-05], 'zmin': -0.014235241781354274, 'zmax': 0.00463754800288369, 'profiles': [{'outer': [[-0.04117871989856636, 0.01705345786717767], [-0.0315236739047971, 0.0315052286179308], [-0.01706354963515179, 0.04118303111266886], [-1.0841024082627379e-05, 0.044579785929514074], [0.017063990362248854, 0.04118280459898318], [0.03152398609040081, 0.03150481015361018], [0.041178850095901325, 0.01705294350376549], [0.04457596299379544, -9.960018432892006e-06], [0.04117871962259276, -0.01706548232542958], [0.03152367390615475, -0.03152399574908605], [0.01706353963502836, -0.041183036490267166], [-1.142298289209713e-05, -0.04458032166926398], [-0.01706399036237229, -0.04118280997664786], [-0.03152398608904317, -0.03152357728476543], [-0.04117885037187492, -0.017064967962017424], [-0.04457596299391886, 9.954640768214279e-06]], 'holes': []}], 'simplify_tolerance': 1.783202151975561e-05, 'sketch_entity_count': 16}
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
