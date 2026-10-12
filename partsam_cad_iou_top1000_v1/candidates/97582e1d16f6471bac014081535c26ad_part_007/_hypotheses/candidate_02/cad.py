#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.21196648, -0.163685425, 0.08160827999999999], 'basis': [[-0.036901216165533324, 0.2137087460737454, 0.9762002213158385], [0.0, 0.9768655466738797, -0.21385439841523574], [-0.999318918186534, -0.007891487383870702, -0.036047526702474714]], 'axis': [0.9762002213158385, -0.21385439841523574, -0.036047526702474714], 'zmin': -0.05573289917312943, 'zmax': 0.05676290989469994, 'profiles': [{'outer': [[-0.04760682174134043, 0.03675074620029325], [-0.04705615817693999, 0.0482658282411927], [-0.046335506946200054, 0.052046483029060585], [0.0454086651800756, 0.05277097444386539], [0.046187974215020106, 0.04825770431437063], [0.046907428739319794, 0.036136858413491145], [0.047472457578161306, 0.018128685042823244], [0.04696038992667422, 0.010788590154817257], [0.04666673732417499, -0.002624468552089486], [0.04423047036020637, -0.015162491160696179], [0.04161584471887191, -0.020931642799605767], [0.03305219489098184, -0.036076847543602034], [0.02175672557647631, -0.037449520923576916], [0.01687940309984322, -0.044830022625799465], [-0.042857861108739834, -0.0453017597842478], [-0.04458176225645878, -0.0455112555696193], [-0.04458336249948175, -0.04531538583716052], [-0.04679040299835905, -0.04533281453978549], [-0.04760682174134043, -0.022509620181366187], [-0.04790489832614859, -0.0015474871858642625], [-0.04790489832614859, 0.01924115920693618]], 'holes': []}], 'simplify_tolerance': 1.965644600269694e-05, 'sketch_entity_count': 21}
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
