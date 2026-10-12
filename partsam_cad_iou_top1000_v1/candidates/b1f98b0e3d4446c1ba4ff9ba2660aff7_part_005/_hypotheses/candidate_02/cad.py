#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.34926744, -0.200518395, -0.16948142500000002], 'basis': [[0.0, 0.9999999953066057, -9.688544180722144e-05], [-0.8192985802569818, -5.555092522590361e-05, -0.5733671016922656], [-0.5733671043833035, 7.937810492022695e-05, 0.8192985764116903]], 'axis': [-9.688544180722144e-05, -0.5733671016922656, 0.8192985764116903], 'zmin': -0.0733861346374649, 'zmax': 0.05551331512665263, 'profiles': [{'outer': [[-0.1671768510149291, -0.001102466233518896], [-0.15618690897222298, -0.0010937720631132666], [-0.15218112384952356, -0.0028768221534376547], [-0.15171715256241353, -0.004562247120426683], [-0.10345702350374286, -0.004564044469643191], [-0.0849918307162051, -0.011525518943244002], [-0.04009895899645807, -0.011525993348561263], [0.02350338205805164, -0.005078304663760272], [0.1588415138030859, 0.01934579489326816], [0.17831044909350438, 0.016317698340330637], [0.22749721689000396, 0.01563142591669919], [0.22749721689000396, 0.00803507595235188], [0.17829819326458002, 0.007348891149551754], [0.15883285470435068, 0.011746165524132872], [0.023487213857595828, -0.012656358004875787], [-0.04011863823925213, -0.019129826117815926], [-0.0850140196039478, -0.019130298304765942], [-0.10348023388552342, -0.01216920429870163], [-0.15172056968586398, -0.01217099926512962], [-0.15218112384952356, -0.013843892101964895], [-0.15618690897222298, -0.017874121984356468], [-0.16171552267963274, -0.01935213974797959], [-0.16718684240220422, -0.017886609620609437], [-0.17121704882895591, -0.013856379541112535], [-0.17268258096951322, -0.008385059529886822], [-0.17121704882895591, -0.002889309592585295]], 'holes': []}], 'simplify_tolerance': 8.003595957190344e-05, 'sketch_entity_count': 29}
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
