#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.012520375, -0.481139, 0.018940820000000004], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.01855582, 'zmax': 0.01855582, 'profiles': [{'outer': [[-0.10117194000000002, 0.138527815], [-0.09610571000000001, 0.141457705], [-0.09030702000000002, 0.142495245], [-0.08450838, 0.141457705], [-0.07944215, 0.138527815], [-0.07565772000000001, 0.134011095], [-0.07370445, 0.128517605], [-0.07370445, 0.122657805], [-0.07565772000000001, 0.117103315], [-0.07944215, 0.112647375], [-0.08450838, 0.109717465], [-0.09030702000000002, 0.108679935], [-0.09610571000000001, 0.109717465], [-0.10117194000000002, 0.112647375], [-0.10495636, 0.117103315], [-0.10697064, 0.122657805], [-0.10697064, 0.128517605], [-0.10495636, 0.134011095]], 'holes': []}, {'outer': [[0.06924858, 0.147988735], [0.07382645999999998, 0.150613515], [0.07901481999999999, 0.151529105], [0.08420311, 0.150613515], [0.08878099, 0.147988735], [0.09213819000000001, 0.143960325], [0.09396932999999999, 0.139016095], [0.09396932999999999, 0.13370575499999998], [0.09213819000000001, 0.12876153499999998], [0.08878099, 0.124733095], [0.08420311, 0.122108325], [0.07901481999999999, 0.121192735], [0.07382645999999998, 0.122108325], [0.06924858, 0.124733095], [0.06589139, 0.12876153499999998], [0.06406023, 0.13370575499999998], [0.06406023, 0.139016095], [0.06589139, 0.143960325]], 'holes': []}, {'outer': [[0.07486422000000001, -0.141884775], [0.07333823, -0.136208235], [0.07382652, -0.130348635], [0.07632908, -0.125038085], [0.08047974, -0.120887365], [0.08579019999999998, -0.118384885], [0.09164988999999998, -0.11789649499999999], [0.09732647, -0.119422435], [0.10208753000000001, -0.122779735], [0.10544461, -0.127601785], [0.10697064, -0.133217345], [0.10648236, -0.139077055], [0.10397973999999999, -0.144387395], [0.09982902999999999, -0.148538195], [0.09451868, -0.151040705], [0.08865904999999999, -0.151529105], [0.08304347000000001, -0.150002955], [0.07822129, -0.146645845]], 'holes': []}], 'simplify_tolerance': 6.0611642e-05, 'sketch_entity_count': 66}
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
