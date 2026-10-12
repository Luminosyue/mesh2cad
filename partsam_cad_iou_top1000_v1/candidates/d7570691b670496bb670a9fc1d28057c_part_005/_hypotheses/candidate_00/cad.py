#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.13881637, -0.292828765, -0.026042679999999995], 'basis': [[-0.0, 0.9382318743495578, 0.3460071530395228], [0.12833029028945953, -0.3431461873999112, 0.930474089197076], [0.99173148411968, 0.04440319839179141, -0.12040356879410245]], 'axis': [0.3460071530395228, 0.930474089197076, -0.12040356879410245], 'zmin': -0.15236377619739017, 'zmax': 0.1736326028754533, 'profiles': [{'outer': [[-0.08627569633464506, 0.045073257022111866], [-0.06941252970169799, 0.07484991256226756], [-0.03859388268515376, 0.08974040784052802], [-0.016467552395085617, 0.08820997211369404], [0.004346434989370085, 0.08436973763026798], [0.02063739012460513, 0.08369435258428978], [0.023311084023120765, 0.0824141683123842], [0.042821579201573035, 0.061702449887850355], [0.052000250110046005, 0.051868087470642796], [0.05654939214630629, 0.04691950201495649], [0.057411203371392425, 0.04434215371330832], [0.054198189414216134, 0.02842018314316919], [0.05832385285149862, 0.006098243013472778], [0.05875666335164729, -0.01057662151129952], [0.05916853011454441, -0.011228508376660703], [0.05883380982827488, -0.013548839250672113], [0.05889870985495636, -0.016049238737736712], [0.05815216052089076, -0.018274133766876668], [0.05729324520405693, -0.024228262660653893], [0.056620283344065395, -0.030317729423231965], [0.053977001193941276, -0.03988258926513396], [0.045262677069784735, -0.04813652029739262], [0.036455675058799694, -0.056294345059691886], [0.02671300414449226, -0.058334523740879295], [0.020700440440811582, -0.05849574948374585], [0.007565289898451419, -0.05956068507326402], [0.0060856799198545745, -0.058479668363846576], [-0.009114377356231638, -0.057066586243385446], [-0.031066537189096945, -0.051458816271537686], [-0.04715216952352547, -0.05360548829512394], [-0.04967771689877013, -0.05258474914132543], [-0.054486543081390434, -0.04754367273694118], [-0.0669397617507801, -0.03429390301585555], [-0.07966933920846053, -0.020631981103988766], [-0.08291604357328244, -0.01709009654574231], [-0.08400397381752683, -0.014330532267844727], [-0.08362244839387335, 0.0019706465705175056], [-0.08615049090502351, 0.02293730761559453]], 'holes': []}], 'simplify_tolerance': 2.986021858275841e-05, 'sketch_entity_count': 50}
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
