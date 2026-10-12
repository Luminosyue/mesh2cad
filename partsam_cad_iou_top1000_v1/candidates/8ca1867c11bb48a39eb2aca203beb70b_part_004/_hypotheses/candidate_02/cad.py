#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.15743965, -0.20765885, -0.22567872], 'basis': [[0.0, 0.9999192038411513, -0.01271163992875076], [-0.9612409345657303, 0.0035047230546312244, 0.2756874727504165], [0.275709749039096, 0.012218948644975434, 0.9611632699904893]], 'axis': [-0.01271163992875076, 0.2756874727504165, 0.9611632699904893], 'zmin': -0.07850616315018158, 'zmax': 0.078506163277298, 'profiles': [{'outer': [[-0.05596098006362446, 0.031961783601435007], [-0.03868481216167643, 0.032174376753104215], [-0.016750498477289412, 0.03229844664817475], [0.0072690400484051055, 0.03231973494883466], [0.030375426532770915, 0.03223548813566959], [0.049810351276843544, 0.032055763116626494], [0.0632364965340345, 0.031802767568040305], [0.06906669589163356, 0.03150592767330049], [0.07846261448994334, 0.023659328396837483], [0.07846261448994334, -0.023519209450517074], [0.06906669589163356, -0.03138313072177343], [0.06652210806145904, -0.031686760442193346], [0.05601915661137186, -0.031961373649215974], [0.038697774692959375, -0.032173801816523205], [0.016763482990488538, -0.03229787165949872], [-0.007210853888248329, -0.03231932503166286], [-0.030317240372614136, -0.0322350782184978], [-0.04979736676364442, -0.03205518812795046], [-0.06322353400275155, -0.031802192631459295], [-0.06900851934388616, -0.031505517721081455], [-0.07844961626612049, -0.02365876372182692], [-0.07844961626612049, 0.023519774125527637], [-0.06900851934388616, 0.03138354067399246], [-0.06650913867486426, 0.03168733522153763]], 'holes': []}], 'simplify_tolerance': 3.138244615121276e-05, 'sketch_entity_count': 27}
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
