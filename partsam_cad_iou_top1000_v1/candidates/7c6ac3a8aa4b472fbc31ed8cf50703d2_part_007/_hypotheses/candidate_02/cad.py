#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.334511625, -0.16881781, -0.017903895000000003], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.442759665, 'zmax': 0.442759665, 'profiles': [{'outer': [[-0.09918377000000002, -0.021728555000000038], [-0.10085935000000001, -0.001783715000000019], [-0.09869733000000001, 0.019242184999999967], [-0.09350841000000001, 0.03643049499999995], [-0.07059074000000001, 0.051726894999999995], [-0.06478112179657819, 0.05217006387762381], [-0.03640563749465124, 0.054740058027298956], [-0.027079620000000026, 0.05696989499999999], [-0.022466032348675165, 0.05714116330617461], [-0.0009188400000000041, 0.059834584999999996], [0.0308397036263048, 0.05972649499999999], [0.04215987999999998, 0.06237499499999999], [0.04345710999999999, 0.06237499499999999], [0.051410707292632994, 0.06052421546818539], [0.06821249999999998, 0.05794279499999999], [0.08129288000000001, 0.048970295], [0.09177876000000001, 0.03502507499999996], [0.09869730999999998, 0.01762064499999999], [0.10085935000000001, -0.0012431549999999958], [0.09864324999999996, -0.01729635500000004], [0.0916707, -0.03372792500000005], [0.08118481, -0.046700165000000016], [0.06853680999999998, -0.05513213500000003], [0.059338867423355236, -0.05641839776440451], [0.05778064999999999, -0.05696986500000001], [0.0504111283847209, -0.05848794459990511], [0.04280846999999999, -0.062374995000000044], [0.042051759999999994, -0.062374995000000044], [0.027566069999999998, -0.05978052500000003], [0.024738025402827938, -0.057996855000000014], [-0.0006485900000000044, -0.057996855000000014], [-0.012229679108330534, -0.05727158985242883], [-0.02675528000000002, -0.058213035000000024], [-0.04242824364033814, -0.055712259843219564], [-0.06961783000000002, -0.052645785], [-0.09258955, -0.03951136500000002], [-0.09356246000000001, -0.038700625000000044], [-0.09492733498249567, -0.03320699751384191]], 'holes': []}], 'simplify_tolerance': 4.034374000000001e-05, 'sketch_entity_count': 38}
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
