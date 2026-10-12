#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.00772355, 0.118714235, 0.38287592], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.017308, 'zmax': 0.017308, 'profiles': [{'outer': [[-0.11712384000000003, -0.042673105], [-0.1171239, -0.010402015], [-0.11507922000000004, -0.009229564999999995], [-0.11304891, -0.009229564999999995], [-0.11304891, -0.012875604999999998], [-0.11057532000000003, -0.012875604999999998], [-0.11057532000000003, -0.009229564999999995], [0.027531209999999973, -0.009229515000000008], [0.036510529999999985, -0.013733455000000006], [0.07464384999999996, -0.013733435000000002], [0.07714604999999997, -0.011660205000000007], [0.07714604999999997, 0.05175239500000001], [0.07876175999999996, 0.057814845000000004], [0.08320844, 0.062247315], [0.08927088999999999, 0.063877295], [0.09900796, 0.063877295], [0.10507041, 0.062247315], [0.10950290999999995, 0.057814845000000004], [0.11113291999999997, 0.05175242499999999], [0.11113291999999997, 0.030734044999999988], [0.11630886999999995, 0.024785974999999988], [0.11712383999999998, 0.023713595000000004], [0.1171239, -0.044903555], [0.10125285, -0.044903565000000006], [0.10125285, -0.061332215], [0.10092402, -0.062604755], [0.09998029999999997, -0.06353413499999999], [0.09870779999999996, -0.063877295], [0.09344601999999996, -0.063877295], [0.09344601999999996, -0.058000725], [0.08212185, -0.058000735000000005], [0.07963394999999995, -0.057328725000000004], [0.07780378999999998, -0.055512834999999996], [0.07714604999999997, -0.053024955], [0.07714604999999997, -0.041414795000000004], [0.07464390999999998, -0.039327265], [0.036510529999999985, -0.039327274999999995], [0.027531209999999973, -0.043845515], [-0.11057526000000001, -0.043845554999999994], [-0.1105752692447245, -0.040199504999999996], [-0.11304885000000003, -0.040199504999999996], [-0.11304885000000003, -0.043845554999999994], [-0.11507922000000004, -0.043845554999999994]], 'holes': []}], 'simplify_tolerance': 4.6849560000000003e-05, 'sketch_entity_count': 46}
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
