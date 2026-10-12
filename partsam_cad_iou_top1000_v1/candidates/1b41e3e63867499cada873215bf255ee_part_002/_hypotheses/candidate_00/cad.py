#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0, -0.11262039500000001, 0.019146830000000004], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.039955825, 'zmax': 0.039955825000000014, 'profiles': [{'outer': [[-0.48085314, -0.09047362], [-0.48068738, 0.09662751], [-0.47945631, 0.10105468], [-0.47649699, 0.10285395], [-0.47235394, 0.10311436], [-0.10148990000000001, 0.10311436], [-0.09734684, 0.10285395], [-0.09438753, 0.10105468], [-0.0931564, 0.09662751], [-0.09299070000000001, 0.09047208], [-0.09299070000000001, -0.09047362], [-0.0931564, -0.09662905], [-0.09438753, -0.10105622], [-0.09734684, -0.1028555], [-0.10148990000000001, -0.10311592], [-0.47235394, -0.10311592], [-0.47649699, -0.1028555], [-0.47945631, -0.10105622], [-0.48068738, -0.09662905]], 'holes': []}, {'outer': [[-0.08744472, -0.09673513], [-0.08744472, 0.09674577], [-0.08602208, 0.10170769], [-0.08230931, 0.10399783], [-0.07793725000000001, 0.10431011], [0.1118060182952397, 0.10431011], [0.11447163999999999, 0.11748505], [0.12331322, 0.12492733], [0.14674717, 0.12595756], [0.26156431, 0.12595756], [0.28499827, 0.12492733], [0.29383984, 0.11748505], [0.29650548471685817, 0.10431011], [0.46041551, 0.10431011], [0.46485695, 0.10403252], [0.46874323, 0.10177711], [0.47072107, 0.09688456], [0.47169262, 0.09060406], [0.47956929, 0.02540489], [0.48085314, 5.31e-06], [0.47956929, -0.02542895], [0.47502372, -0.0639447], [0.47072107, -0.09687392], [0.46874323, -0.10180116], [0.46485695, -0.10402189], [0.46041551, -0.10429948], [0.29650763234528565, -0.10429948], [0.29383984, -0.11748505], [0.28499827, -0.12492733], [0.26156431, -0.12595756], [0.14674717, -0.12595756], [0.12331322, -0.12492733], [0.11447163999999999, -0.11748505], [0.11180387068535237, -0.10429948], [-0.07793725000000001, -0.10429948], [-0.08230931, -0.10402189], [-0.08602208, -0.10169706]], 'holes': []}], 'simplify_tolerance': 0.00019234125600000001, 'sketch_entity_count': 59}
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
