#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.64595458, 1.356767715, 0.66545542], 'basis': [[-0.0, 0.9998497331614731, 0.01733525589459722], [0.5524452498428356, -0.014449788444668703, 0.8334239314658485], [0.8335491862668255, 0.00957677977378025, -0.5523622356416825]], 'axis': [0.01733525589459722, 0.8334239314658485, -0.5523622356416825], 'zmin': -0.5037877333184407, 'zmax': 0.503787831703528, 'profiles': [{'outer': [[-0.25650939567121184, 0.04923530274282161], [-0.255479957156597, 0.05515847461073968], [-0.22591628199638655, 0.13143264896393295], [-0.22488439070366192, 0.13740559848646444], [-0.1732086728683622, 0.2007643285591264], [-0.1044771766061244, 0.24505554717999892], [-0.02541771821846996, 0.2659435866435711], [0.05623078386058726, 0.2613837638100477], [0.13247598686157203, 0.23182267330143116], [0.19585442072627698, 0.18015397626063323], [0.2401624526983042, 0.11143506856981848], [0.2610625590215703, 0.032392779546892], [0.2600309202141358, 0.026419890628527173], [0.255475041800492, -0.05525838933857971], [0.25444556869489016, -0.0611814918383826], [0.2248841584814045, -0.13740565365859567], [0.1732085478359843, -0.20076438998662727], [0.10447706186176299, -0.24505550602467108], [0.025417734889453713, -0.2659436564415167], [-0.05623089105046672, -0.2613840275141059], [-0.13247615279039943, -0.23182300016696494], [-0.19585468550949175, -0.1801541767930617], [-0.24016269364655815, -0.11143524631980252], [-0.2610628904887201, -0.03239307083193884]], 'holes': []}], 'simplify_tolerance': 0.00010637744861701757, 'sketch_entity_count': 24}
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
