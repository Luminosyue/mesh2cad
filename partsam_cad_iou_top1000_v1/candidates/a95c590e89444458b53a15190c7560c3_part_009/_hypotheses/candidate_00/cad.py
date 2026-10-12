#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.179383815, -0.04579688999999999, 0.022570680000000003], 'basis': [[-0.2617881685727015, -0.5115318617793465, 0.8184143872024162], [0.0, 0.8479876538683012, 0.5300159798411123], [-0.9651253570367689, 0.13875191267687068, -0.2219931348784445]], 'axis': [0.8184143872024162, 0.5300159798411123, -0.2219931348784445], 'zmin': -0.028834890995304056, 'zmax': 0.009999401671530062, 'profiles': [{'outer': [[-0.006523048343542419, -0.04930202034947489], [-0.003914335696457678, -0.0388379336491522], [0.0048591083343685, -0.03107220303814308], [0.015115353911194129, -0.02807628876293774], [0.039429250355829615, 0.13021071875798984], [0.04741108799111652, 0.13937119812717677], [0.06079435585084898, 0.14167913601686], [0.0744184610921764, 0.13624419110133176], [0.0831227722672339, 0.12510802123709924], [0.08357004031144544, 0.11258947740362134], [0.03551024312315265, -0.05110720188595256], [0.03124074031485245, -0.06089868084565401], [0.022476607268909227, -0.0686463144360221], [0.011781368708772525, -0.07001028960478123], [-0.061190420116883276, -0.13459652950712478], [-0.07259715449579736, -0.12181986813889761], [-0.07952925092154847, -0.11388333268292336]], 'holes': []}], 'simplify_tolerance': 5.525513310479695e-05, 'sketch_entity_count': 17}
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
