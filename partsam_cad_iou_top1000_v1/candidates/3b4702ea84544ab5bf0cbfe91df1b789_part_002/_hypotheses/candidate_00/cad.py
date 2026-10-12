#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [1.2149999999988559e-06, -0.095747235, 0.14659055499999998], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.107701495, 'zmax': 0.107701495, 'profiles': [{'outer': [[-0.12563672499999998, 0.046277745], [-0.11841086788670577, 0.05030816254284217], [-0.163786625, 0.11359994500000001], [-0.16112733499999998, 0.125116895], [-0.158707985, 0.127836185], [-0.10648180499999998, 0.157988215], [-0.10284276499999997, 0.159087905], [-0.08858654499999999, 0.158907975], [-0.08662706499999998, 0.157808255], [-0.037958862186988636, 0.09518244804904319], [-0.025623204999999982, 0.102062995], [0.07437031500000002, 0.046277745], [0.07437031500000002, 0.03292044085679497], [0.151389935, 0.033161235000000004], [0.15372929500000002, 0.032181495000000004], [0.16270694500000002, 0.020364605], [0.163786625, 0.016685585000000003], [0.163786625, -0.016685574999999998], [0.16270694500000002, -0.020364604999999997], [0.15372929500000002, -0.032181475], [0.15136993500000004, -0.033161224999999996], [0.07437031500000002, -0.03292050136087084], [0.07437031500000002, -0.046277755], [-0.025623204999999982, -0.102062995], [-0.03795887802337153, -0.0951824404492722], [-0.08662706499999998, -0.157808235], [-0.08858654499999999, -0.158927955], [-0.10284276499999997, -0.159087905], [-0.10648180499999998, -0.157988195], [-0.158707985, -0.127836175], [-0.16112733499999998, -0.125116895], [-0.163786625, -0.113599945], [-0.14175530775726933, -0.08311447762090256], [-0.1183668666336556, -0.05033271470677293], [-0.12563672499999998, -0.046277755]], 'holes': []}], 'simplify_tolerance': 6.551465e-05, 'sketch_entity_count': 50}
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
