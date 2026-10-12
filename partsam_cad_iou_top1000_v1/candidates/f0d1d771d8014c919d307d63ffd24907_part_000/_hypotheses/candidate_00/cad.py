#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.01878988, -0.07630456, 1.720000000003663e-06], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.07223794, 'zmax': 0.07223794, 'profiles': [{'outer': [[-0.10377849, -0.031813190000000005], [-0.10409635, -0.005955040000000009], [-0.10273145, 0.022576799999999994], [-0.09867415999999998, 0.051669549999999995], [-0.08859639999999999, 0.10592866999999999], [-0.08450173999999999, 0.12612157999999998], [-0.07962179, 0.13730247], [-0.07195595999999999, 0.14713716], [-0.046490439999999994, 0.15240975], [-0.020632289999999998, 0.15315764999999998], [0.020632300000000003, 0.15315764999999998], [0.04649045, 0.15240975], [0.07195596000000001, 0.14713716], [0.07962179, 0.13730247], [0.08450175000000001, 0.12612157999999998], [0.08859642000000001, 0.10592866999999999], [0.09867418, 0.051669549999999995], [0.10273146, 0.022576799999999994], [0.10409635, -0.005955040000000009], [0.1037785, -0.031813190000000005], [0.10316149, -0.053314920000000016], [0.10232013000000001, -0.07109589], [0.10127309000000001, -0.08693237000000001], [0.10065608000000001, -0.10493773], [0.09932858, -0.12731820000000002], [0.08850294, -0.14627709], [0.06249521, -0.15315765], [0.035795690000000005, -0.14627709], [0.023156420000000004, -0.12731820000000002], [0.020407940000000003, -0.10493773], [0.019996600000000003, -0.08693237000000001], [0.019903120000000003, -0.07109589], [0.019286110000000002, -0.05451153], [0.016201080000000003, -0.04136743000000001], [0.009264440000000004, -0.03587047], [9.350000000003663e-06, -0.03508519], [-0.009245739999999997, -0.03587047], [-0.016201069999999998, -0.04136743000000001], [-0.019267409999999995, -0.05451153], [-0.019903109999999995, -0.07109589], [-0.019996589999999995, -0.08693237000000001], [-0.020407919999999996, -0.10493773], [-0.023156399999999997, -0.12731820000000002], [-0.035795679999999996, -0.14627709], [-0.062495209999999995, -0.15315765], [-0.08848423999999999, -0.14627709], [-0.09930986, -0.12731820000000002], [-0.10065605999999999, -0.10493773], [-0.10127306, -0.08693237000000001], [-0.10232010999999999, -0.07109589], [-0.10316149, -0.053314920000000016]], 'holes': []}], 'simplify_tolerance': 6.126305999999999e-05, 'sketch_entity_count': 51}
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
