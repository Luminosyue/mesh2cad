#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.14453336, 0.020825089999999997, 0.41805598], 'basis': [[0.0, 0.9894200889471473, -0.1450789012496968], [-0.31320304971040414, 0.13777942822678174, 0.9396385894638445], [0.9496861848274418, 0.0454391543200396, 0.3098893893029859]], 'axis': [-0.1450789012496968, 0.9396385894638445, 0.3098893893029859], 'zmin': -0.025727417285241104, 'zmax': 0.014462736849880035, 'profiles': [{'outer': [[-0.06429121941948855, -0.03791029740356655], [-0.0669398420434458, -0.034208129542769194], [-0.061954970321613095, -0.02682734773740074], [-0.059340852128749635, -0.024265654592100127], [-0.03764069299430956, -0.010374463735863424], [-0.030928829506927078, -0.005963659039423475], [-0.030743880538877597, -0.0040748555932075435], [-0.030476423926607894, -0.002615365442164872], [-0.03011981719826862, -0.0013640758845639596], [-0.029674057221829284, -0.0004336139869239503], [-0.029174805296529903, 0.00019165834544863518], [-0.02862206768643148, 0.00045544586508124266], [-0.020575082065797185, 0.0008404659140920427], [-0.011395106983693263, 0.006873228243281866], [-0.007504285264328888, 0.008793209457969926], [-0.007635171938494098, 0.010183160116730039], [-0.00768866075532364, 0.011896481080591888], [-0.007635171938494098, 0.013506444099887509], [-0.007474705488005469, 0.015069337283477105], [-0.007225076393325283, 0.01648031247130799], [-0.006886297182575527, 0.017626808851037824], [-0.0064761985053762156, 0.018516620734511092], [-0.0059947834937578446, 0.019093411919657435], [-0.005495531568458466, 0.01938073792644923], [0.02321352522136769, 0.020754365639158057], [0.03872421564168179, 0.027682932950505234], [0.05058404476102555, 0.03361315325161191], [0.06704682280913539, 0.04114559240956635], [0.06450350022613313, 0.026330907211808], [0.05450152878673454, 0.004504511270265971], [0.04062125828716029, -0.016151856797870113], [0.03313848096874263, -0.023724658718377197], [0.023291211420111202, -0.03081466444010971], [-0.00428297816843862, -0.04195811144420649], [-0.016610975557372832, -0.04369775427573702], [-0.02771094651829193, -0.04442068971531737], [-0.03133846800487757, -0.04471640439150313], [-0.03872874335538869, -0.0436085509022165], [-0.04420909046117882, -0.0426856249772363], [-0.05714993936481387, -0.0418112283567235], [-0.05910547392428138, -0.0411104593837958]], 'holes': []}], 'simplify_tolerance': 2.6797332970516242e-05, 'sketch_entity_count': 74}
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
