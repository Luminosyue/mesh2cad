#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.002261474999999999, -0.064848975, -0.20692605], 'basis': [[0.0, 0.9999936703920438, 0.003557973559292808], [-0.9471007527335508, 0.0011418831773368785, -0.32093435508581913], [-0.3209363864873245, -0.00336975943621229, 0.947094757957091]], 'axis': [0.003557973559292808, -0.32093435508581913, 0.947094757957091], 'zmin': -0.21980022367360638, 'zmax': 0.13028045622771822, 'profiles': [{'outer': [[-0.33150340448152865, 0.05847196636215392], [-0.32417580330982587, 0.06599493185306196], [-0.31083042508787356, 0.07013466909413302], [-0.2930830621921142, 0.0714691535125413], [-0.21499337959350037, 0.07116449991637414], [0.2438849502373209, 0.07091132007659723], [0.27109102965343684, 0.07081367322712226], [0.296243400102386, 0.06964987271616548], [0.296243400102386, -0.06932213763992429], [0.27109102965343684, -0.07074833073521959], [0.2438849502373209, -0.07079870294883606], [-0.14457563956159217, -0.07060045150818137], [-0.2547566101856185, -0.0706967326950465], [-0.2930830621921142, -0.07090685529743637], [-0.31083042508787356, -0.07002134376763762], [-0.32417580330982587, -0.06624308112686095], [-0.33150340448152865, -0.0588920407649907], [-0.33341056979516226, -0.00022678559336243267]], 'holes': []}], 'simplify_tolerance': 0.00012593079397950967, 'sketch_entity_count': 21}
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
