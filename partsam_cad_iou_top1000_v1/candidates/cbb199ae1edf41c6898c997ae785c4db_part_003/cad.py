#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.007655015000000001, 0.16681433, 8.519999999997974e-06], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.10416489, 'zmax': 0.10416489, 'profiles': [{'outer': [[-0.02888019, -0.030822885], [-0.028872386631966906, -0.03084154654499052], [-0.026948203202743333, -0.030044188575357567], [-0.026957519999999985, -0.030021735], [-0.01734413999999998, -0.026056225000000002], [-0.017341190240012933, -0.026063160449940666], [0.0076906700000000106, -0.015681795000000002], [0.028079050000000022, -0.007241570996469842], [0.028079050000000022, 0.044441835], [0.03849359000000002, 0.044441835], [0.03849359000000002, -0.015962205], [0.03259890259310673, -0.015962205], [0.03284572000000002, -0.016563045000000002], [-0.001802459999999978, -0.030902995000000003], [-0.014791808447744099, -0.03627514109735913], [-0.022951899999999997, -0.039675175], [-0.022960252657738715, -0.0396551896112101], [-0.02488483191226176, -0.04045156785433742], [-0.02487457999999998, -0.040476275], [-0.03452802999999999, -0.044441835], [-0.038493589999999994, -0.034828455]], 'holes': [[[-0.024884883119984852, -0.040451589043756585], [-0.03451975102961946, -0.04443843404408895], [-0.024874639999999976, -0.040476275]], [[-0.03848261341215665, -0.034823906436872734], [-0.028872437828915284, -0.030841567760376845], [-0.0288801811556968, -0.030822906314802726]], [[-0.02296020144999549, -0.0396551684217826], [-0.02295190884429865, -0.039675153685151045], [-0.014800510988535794, -0.036278742151527286]], [[-0.02695745999999999, -0.030021735], [-0.02694815200577482, -0.0300441673599629], [-0.017341241405699433, -0.026063181652372452], [-0.017344131200045618, -0.02605624611996956]], [[0.003996141058238689, -0.017221232542773985], [0.005769434418628954, -0.016486401563601212], [0.005767998875851356, -0.016482956301790645]], [[0.0076937307690642725, -0.015688996800805634], [0.012164733195166316, -0.01383626833294888], [0.007690730000000007, -0.015681795000000002]], [[-0.003916313640490685, -0.031774932842808905], [-0.001802520000000002, -0.030902995000000003], [-0.001803484068664913, -0.030900657855959874]]]}], 'simplify_tolerance': 1.7776734000000002e-05, 'sketch_entity_count': 46}
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
