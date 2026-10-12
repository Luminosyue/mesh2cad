#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-1.114145695, 2.496029495, 0.76164004], 'basis': [[0.08583630438495421, 0.1504382575572736, 0.9848860134617939], [0.0, 0.9885344433798602, -0.15099554381394864], [-0.9963092536203473, 0.012960899459585786, 0.08485214337696496]], 'axis': [0.9848860134617939, -0.15099554381394864, 0.08485214337696496], 'zmin': -0.27483029079892507, 'zmax': 0.2752291575730191, 'profiles': [{'outer': [[-0.045148811966728306, -0.583457966776846], [-0.45905616081608724, -0.33840044310135614], [-0.4927523460230117, -0.3183117178357631], [-0.4926277910295623, -0.31810143318000395], [-0.4933543202913938, -0.3176710600054209], [-0.29307059981075034, 0.020465740577277118], [-0.2930872176344446, 0.03315469747218611], [-0.29649393232798915, 0.040121553562764485], [0.029247748168212132, 0.5900208096704533], [0.13617753998877144, 0.5310436986622622], [0.2684083982639747, 0.45345406745028183], [0.3990365649613509, 0.37533448405002434], [0.49988590171174296, 0.3112298750055978], [0.17414423203699717, -0.23866937972731747], [0.1663346990896497, -0.23913431079784486], [0.1551347291782496, -0.24532140110945225]], 'holes': []}], 'simplify_tolerance': 0.0002346957552894599, 'sketch_entity_count': 16}
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
