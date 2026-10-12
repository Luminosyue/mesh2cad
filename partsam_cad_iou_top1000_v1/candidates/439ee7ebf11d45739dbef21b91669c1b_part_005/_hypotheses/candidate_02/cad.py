#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.114291555, -0.06717559, -0.008533844999999998], 'basis': [[-0.052814547525377994, -0.40862639841890785, 0.9111723712255995], [0.0, 0.9124458373461465, 0.40919749988201265], [-0.9986043378484241, 0.021611580804784418, -0.04819041404085137]], 'axis': [0.9111723712255995, 0.40919749988201265, -0.04819041404085137], 'zmin': -0.04748497004224752, 'zmax': 0.04829917381926503, 'profiles': [{'outer': [[-0.06664019338211909, -0.04195745445800778], [-0.0726370400628304, -0.028276114388034426], [-0.07805335063929132, -0.015383551799679882], [-0.08211679025426438, -0.004881430711596668], [-0.08448827795571424, 0.00208822571399035], [-0.08484019810684519, 0.004575355138532622], [-0.016065495541669528, 0.04235526762775473], [0.04039706131831831, 0.07357619993539707], [0.04251926939977132, 0.07065062245700449], [0.04708110157821953, 0.0620364852825115], [0.053393977026031436, 0.04877932326233718], [0.060867854989709876, 0.03251816634449093], [0.06846366252972903, 0.015118392621022846], [0.07539200318765359, -0.001202899806922008], [0.08067379126646186, -0.014583698257475814], [0.08377764737515901, -0.023324123967878706], [0.08432036405693548, -0.026455621394815942], [0.023853278733059785, -0.04871627872769232], [-0.050324052901332114, -0.0741221125032876], [-0.05203710962097038, -0.07186198360066996], [-0.055732312043911894, -0.06514876924147499], [-0.06079671087084882, -0.05474332360275496]], 'holes': []}], 'simplify_tolerance': 3.3832112432756136e-05, 'sketch_entity_count': 22}
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
