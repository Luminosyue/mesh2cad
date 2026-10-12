#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.003244205, -0.132938655, 0.07215178], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.36706140499999995, 'zmax': 0.36706140499999995, 'profiles': [{'outer': [[-0.16875458, -0.004794655], [-0.16839611, 0.008379475], [-0.16696218000000002, 0.021508825], [-0.16445283, 0.034503735], [-0.16086803, 0.047319405], [-0.15629738999999998, 0.059866215], [-0.15069615, 0.072054535], [-0.14410906, 0.083794775], [-0.13662579, 0.094997275], [-0.12824631, 0.105662065], [-0.11901545, 0.115699515], [-0.10902281, 0.125019995], [-0.09831321, 0.133578705], [-0.08693147, 0.141330855], [-0.075012, 0.148186785], [-0.06340619, 0.153967275], [-0.05309989, 0.158313855], [-0.04324168, 0.161495355], [-0.03315942, 0.163646245], [-0.022046539999999996, 0.165035355], [-0.009141250000000004, 0.165841925], [0.004660239999999996, 0.165841925], [0.01837213, 0.164811315], [0.031904749999999996, 0.162750035], [0.04525813000000001, 0.159702955], [0.05825305, 0.155625255], [0.07084468, 0.150606525], [0.08294338000000001, 0.144601985], [0.09450436000000001, 0.137746035], [0.10543799000000001, 0.129993895], [0.11569951, 0.121435185], [0.12519923, 0.112114705], [0.13384756, 0.102122065], [0.14168933, 0.091457285], [0.14859006, 0.080209965], [0.15450498000000001, 0.068469725], [0.15947893, 0.056326215], [0.1633774, 0.043779405], [0.16624522, 0.030963745], [0.16803765, 0.017968835000000002], [0.16875458000000002, 0.004839485], [0.16844091, -0.008334655], [0.16696218, -0.021463995], [0.16449764, -0.034503715], [0.16091284, -0.047319375], [0.15629739, -0.059821385000000005], [0.15069616, -0.072009715], [0.14415389, -0.083749935], [0.1366258, -0.094997255], [0.12824631, -0.105662045], [0.11901545999999999, -0.115654685], [0.10902281, -0.124975165], [0.09831323, -0.133533885], [0.08697629000000001, -0.141286015], [0.075012, -0.148186775], [0.06345102, -0.153922455], [0.053099900000000005, -0.158313825], [0.043286500000000006, -0.161495345], [0.033204239999999996, -0.163646225], [0.022046540000000003, -0.165035335], [0.009141250000000004, -0.165841925], [-0.004615430000000004, -0.165841925], [-0.018327299999999998, -0.164811285], [-0.031904749999999996, -0.162750025], [-0.045213329999999996, -0.159702945], [-0.05820823, -0.155625245], [-0.07079985, -0.150561695], [-0.08294337, -0.144601955], [-0.09450436, -0.137701225], [-0.10543801, -0.129993885], [-0.1156547, -0.121435175], [-0.12515442999999998, -0.112114695], [-0.13384757, -0.102077245], [-0.14164451, -0.091412455], [-0.14854526, -0.080209945], [-0.15450501, -0.068469715], [-0.1594341, -0.056281385], [-0.1633774, -0.043779385], [-0.16624523, -0.030963724999999998], [-0.16803763, -0.017924005]], 'holes': []}], 'simplify_tolerance': 6.7501832e-05, 'sketch_entity_count': 128}
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
