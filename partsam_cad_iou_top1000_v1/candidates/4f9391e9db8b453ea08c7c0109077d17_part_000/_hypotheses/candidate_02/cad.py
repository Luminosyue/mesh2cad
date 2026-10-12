#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.164528075, 0.289029255, 0.004108914999999991], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.210970535, 'zmax': 0.21097053500000001, 'profiles': [{'outer': [[-0.183643005, -0.003265075000000006], [-0.183643005, 0.003265085000000001], [-0.195225695, 0.025310355000000007], [-0.193295245, 0.03815618500000001], [-0.17403840499999998, 0.057651355], [-0.170129845, 0.06041595499999999], [-0.15878547499999998, 0.06720828499999999], [-0.12463035457239949, 0.07492981632148217], [-0.10487901924599054, 0.07993631496847022], [-0.10265942499999998, 0.080840595], [-0.06912677499999999, 0.102552205], [-0.064050425, 0.105721965], [-0.05556596499999999, 0.110417015], [-0.04243414499999999, 0.114230245], [-0.0032531549999999907, 0.106913595], [0.003253175000000009, 0.106913595], [0.04243416500000001, 0.114230245], [0.05556598500000001, 0.110417015], [0.064050435, 0.105721965], [0.06905530500000001, 0.102599865], [0.10265944500000002, 0.080840595], [0.10834672547135248, 0.07852354891577423], [0.11673713711034922, 0.07651229744047043], [0.157975175, 0.067303605], [0.170320515, 0.060201464999999996], [0.174038445, 0.057651355], [0.19329526500000002, 0.032388675000000006], [0.18364301500000002, 0.003265085000000001], [0.18364301500000002, -0.003265075000000006], [0.195225695, -0.025310345000000012], [0.19329526500000002, -0.038156175000000014], [0.174038445, -0.057651355000000015], [0.170129845, -0.06041595499999999], [0.15878546500000001, -0.06720827500000001], [0.12463025019797865, -0.07492983624234507], [0.10487905753081628, -0.07993629956316375], [0.10265944500000002, -0.08084058499999999], [0.068983815, -0.10264753500000001], [0.064050435, -0.10572194499999998], [0.05556598500000001, -0.11041700500000001], [0.04243416500000001, -0.11423024500000001], [0.003253175000000009, -0.10691359500000003], [-0.0032531549999999907, -0.10691359500000003], [-0.04243414499999999, -0.11423024500000001], [-0.05556596499999999, -0.11041700500000001], [-0.064050425, -0.10572194499999998], [-0.06905529499999999, -0.10259985500000002], [-0.10265942499999998, -0.08084058499999999], [-0.10834684158420614, -0.07852349590161062], [-0.1167358065674651, -0.07651259076203659], [-0.157975165, -0.067303595], [-0.17032050499999998, -0.06020144499999999], [-0.17403840499999998, -0.057651355000000015], [-0.193295245, -0.038156175000000014], [-0.195225695, -0.025310345000000012]], 'holes': []}], 'simplify_tolerance': 7.8090278e-05, 'sketch_entity_count': 67}
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
