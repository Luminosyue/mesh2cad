#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.051889975000000005, 0.31865048, 0.05952239], 'basis': [[0.0, 0.854087435145561, -0.5201294580452804], [-0.9843857799690147, -0.09155554491787396, -0.15034034185668774], [-0.17602453293445935, 0.5120080422427643, 0.8407515260074984]], 'axis': [-0.5201294580452804, -0.15034034185668774, 0.8407515260074984], 'zmin': -0.00649561154227073, 'zmax': 0.006170952917070671, 'profiles': [{'outer': [[-0.016952153972960796, 0.0017308642792102408], [-0.013335997115783834, 0.00703163216868637], [-0.0076880025835065445, 0.011000912446012876], [-0.0008997054130740734, 0.013314720603746341], [0.006019052399274577, 0.013839025524622876], [0.01202758805081398, 0.012443580997276115], [0.016241089626331598, 0.009161043154078877], [0.018227807974539253, 0.004557491393478541], [0.017710325537353466, -0.000627434586974107], [0.014438600921234241, -0.00567733554145944], [0.008453852356982924, -0.00989676007965204], [0.0008995872867805405, -0.012779679975790426], [-0.006771040392724516, -0.013860957433523917], [-0.013130267086636085, -0.012727791959864896], [-0.016993079380026865, -0.009182978483773844], [-0.018227809734784585, -0.004022434658776821]], 'holes': []}], 'simplify_tolerance': 7.291123541864768e-06, 'sketch_entity_count': 28}
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
