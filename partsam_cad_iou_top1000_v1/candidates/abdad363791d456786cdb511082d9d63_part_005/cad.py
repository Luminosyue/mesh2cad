#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [3.6652019000000005, 3.91202116, 2.0158913099999998], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.5104825500000003, 'zmax': 0.5104825499999999, 'profiles': [{'outer': [[-0.58976651, -0.5812904800000003], [-0.71040035, -0.41815186000000004], [-0.7747194800000003, -0.2257208799999999], [-2.84482122, -1.30302644], [-2.84652686, -1.10013747], [-2.7854535600000006, -0.9066515000000002], [-0.7283980900000002, 0.19573832000000024], [-0.5616850900000001, 0.3319044099999999], [-0.4297294700000003, 0.44757318999999995], [-0.26494456000000044, 0.5650420199999999], [-0.06435895000000036, 0.57117605], [0.017724622169185137, 0.5299917974317984], [1.3066649394060117, 1.2004460418955174], [1.36610818, 1.3887648600000002], [1.5089552399999997, 1.5888934099999998], [1.7066528799999998, 1.7350850099999997], [1.9398519999999997, 1.81302786], [2.18572211, 1.81509447], [2.4201967699999996, 1.74108267], [2.6203243699999996, 1.5982356099999997], [2.76651597, 1.4005370099999999], [2.84445977, 1.1673397999999997], [2.84652686, 0.9214692099999997], [2.7725145799999997, 0.6869940799999998], [2.62966752, 0.4868655200000003], [2.43196845, 0.3406748799999999], [2.19877076, 0.26273108], [1.9529006399999997, 0.2606644600000001], [1.7749494456349195, 0.31683491024639815], [0.47763496924401294, -0.35797539664278905], [0.4613234999999998, -0.43944216], [0.3746306899999998, -0.5996212999999999], [0.1664869699999998, -0.69864535], [-0.014525890000000263, -0.7480583200000002], [-0.21315599000000018, -0.7644307600000002], [-2.2591059200000005, -1.81509447], [-2.4525916600000004, -1.75402069], [-2.6177351500000006, -1.63614535]], 'holes': []}], 'simplify_tolerance': 0.001138610744, 'sketch_entity_count': 38}
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
