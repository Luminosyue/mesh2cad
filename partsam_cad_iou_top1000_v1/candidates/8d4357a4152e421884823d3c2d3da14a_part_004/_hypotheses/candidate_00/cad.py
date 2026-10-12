#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.06596486, -0.46588063, -0.013473035000000001], 'basis': [[0.0, 0.9998095765994829, 0.019514367526589565], [-0.1328286368398399, -0.019341451069491433, 0.9909502820554604], [0.9911390181176755, -0.00259206683734853, 0.1328033431591268]], 'axis': [0.019514367526589565, 0.9909502820554604, 0.1328033431591268], 'zmin': -0.03752118653947038, 'zmax': 0.03101486862224648, 'profiles': [{'outer': [[-0.07817569872761633, 0.004915387305485192], [-0.07587320317274836, 0.015563158242172328], [-0.0681135534457557, 0.028521145398170054], [-0.044622174568177214, 0.04219754129409811], [0.002147334837879127, 0.05348797213149107], [0.035315930934574725, 0.0563282486954983], [0.06021944538692197, 0.05662668859248524], [0.07671850362012277, 0.05032789805437639], [0.082006895068171, 0.039235124115342725], [0.07725034818255688, 0.02830095465857744], [0.07696281938808879, 0.028105661428028894], [0.06311465809665996, 0.022401718291119383], [0.05414224793659579, 0.01965292544940388], [0.06311465809665996, 0.01689766659098157], [0.07725034818255688, 0.011336955616211395], [0.082006895068171, 0.0012407305149525266], [0.07725034818255688, -0.008666564519974733], [0.07696281938808879, -0.008902929927929997], [0.06311465809665996, -0.014360420004207725], [0.05427904473132972, -0.01730998939702429], [0.06311465809665996, -0.020685965242958508], [0.07725034818255688, -0.027109261929939885], [0.082006895068171, -0.03880741192911375], [0.07671304834800777, -0.05006025655566347], [0.07613964444812048, -0.05052549111259775], [0.0602030769140042, -0.05620878470164252], [0.03520678830025616, -0.05545277703778844], [0.0017980911596088716, -0.05224891303253412], [-0.0451187610684348, -0.033000969176366954], [-0.06893877280362627, -0.018740914949053916], [-0.07598234182220782, -0.005811725634568272]], 'holes': []}], 'simplify_tolerance': 3.2036518759157467e-05, 'sketch_entity_count': 37}
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
