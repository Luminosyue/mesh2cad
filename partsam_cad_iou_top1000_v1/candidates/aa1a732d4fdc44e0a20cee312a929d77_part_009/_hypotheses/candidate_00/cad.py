#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.15031907, -0.12194826, -0.11127366], 'basis': [[0.0, 0.7459264328537906, 0.6660283453202421], [-0.8993971567942475, 0.29114258370046264, -0.3260686282159678], [-0.4371324219849449, -0.5990240001254029, 0.6708841128863744]], 'axis': [0.6660283453202421, -0.3260686282159678, 0.6708841128863744], 'zmin': -0.023554302701251605, 'zmax': 0.023682217927059372, 'profiles': [{'outer': [[-0.028449405294360144, -0.022679192688118185], [-0.016706809341722514, -0.01602442014861406], [-0.017989384209570258, -0.013034143071194364], [-0.018686503686435266, -0.010275246017823775], [-0.018536542572872208, -0.008475181406003516], [-0.0176431596022516, -0.007870864146778135], [-0.0035922425710279066, 9.207191472691785e-05], [-0.0032883366156098728, 0.0034529619867952983], [0.0020747536432390236, 0.021911700589448788], [0.0026700351852892304, 0.022067779936843168], [0.004556192663851422, 0.021806283964867827], [0.007490019230158565, 0.02116209446044553], [0.008296506072470913, 0.020941095494925826], [0.012881003706671786, 0.03672003512102884], [0.013476267763425115, 0.03687609050746322], [0.015389107805025263, 0.036651158960455524], [0.018296243065646013, 0.03597039305058558], [0.021816477377505177, 0.03504967398458118], [0.025405391351242958, 0.033930440031501787], [0.028459172946383598, 0.03289937638129299], [0.030593439565318296, 0.03198968493499843], [0.031419378119574015, 0.03146202279125788], [0.02602960529768717, 0.012966712304372434], [0.01678653952049988, -0.010135587712827921], [0.01583827071272435, -0.010722100712872742], [0.010442710466978936, -0.013790464523808343], [0.005980293828391337, -0.024943916254167975], [0.005032038134588466, -0.02553041128349279], [-0.01988616385376322, -0.03970096759727762], [-0.02150088910149719, -0.039027832355946424], [-0.023458828862635075, -0.03715681205479596], [-0.02551520774408754, -0.03435021247591023], [-0.027395559830224275, -0.0311066845223642], [-0.028795608045057708, -0.027842441661334417], [-0.029492749378543816, -0.025083574559163834], [-0.029342770779683877, -0.023283485986383568]], 'holes': []}], 'simplify_tolerance': 1.5315411620948167e-05, 'sketch_entity_count': 42}
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
