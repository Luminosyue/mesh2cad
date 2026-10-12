#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.13981598, 0.318094325, -4.405000000000034e-05], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.03107215499999999, 'zmax': 0.03107215499999999, 'profiles': [{'outer': [[-0.044407810000000006, -0.012939179999999995], [-0.045506599999999994, -0.00870825], [-0.046174950000000006, -0.004528279999999996], [-0.046395839999999994, -0.0004672599999999971], [-0.04639583, 0.0004672799999999866], [-0.046174950000000006, 0.004539619999999994], [-0.04550661, 0.008719580000000005], [-0.044407810000000006, 0.01294484999999998], [-0.042872900000000005, 0.017181449999999987], [-0.04093017, 0.020868639999999994], [-0.038590990000000006, 0.024487869999999995], [-0.035877980000000004, 0.02800516], [-0.03282514, 0.03137518], [-0.02945512, 0.034071199999999996], [-0.025796239999999998, 0.03656330999999999], [-0.02189381, 0.038834549999999995], [-0.01777616, 0.04086220999999998], [-0.01349425, 0.04211960000000001], [-0.00907641, 0.04310512], [-0.0045736, 0.043801779999999985], [-2.839999999999661e-06, 0.044203909999999985], [0.004573590000000001, 0.043801779999999985], [0.00907639, 0.04310512], [0.013494230000000001, 0.04211960000000001], [0.01777614, 0.04086220999999998], [0.0218938, 0.038834549999999995], [0.02579623, 0.03656330999999999], [0.02945511, 0.034071199999999996], [0.032825129999999994, 0.03137518], [0.035877969999999995, 0.02800516], [0.03859098, 0.024487869999999995], [0.04093017, 0.020868639999999994], [0.04287289, 0.017181449999999987], [0.044407810000000006, 0.01294484999999998], [0.045506599999999994, 0.008719580000000005], [0.04617494, 0.004539619999999994], [0.046395839999999994, 0.0004672799999999866], [0.04639583, -0.0004672599999999971], [0.04617494, -0.004528279999999996], [0.045506599999999994, -0.00870825], [0.044407810000000006, -0.012939179999999995], [0.04287289, -0.017181440000000006], [0.04093017, -0.02086297000000001], [0.03859098, -0.024476540000000005], [0.035877980000000004, -0.027993820000000003], [0.032825129999999994, -0.03137517000000001], [0.02945511, -0.03405986000000001], [0.02579623, -0.03655198000000001], [0.02189381, -0.03882886000000001], [0.01777615, -0.04086787], [0.013494240000000001, -0.04211392000000001], [0.0090764, -0.04309378000000001], [0.004573600000000001, -0.04379045000000001], [-2.8299999999996595e-06, -0.04420391000000001], [-0.00457359, -0.04379045000000001], [-0.0090764, -0.04309378000000001], [-0.01349424, -0.04211392000000001], [-0.01777615, -0.04086787], [-0.021893799999999998, -0.03882886000000001], [-0.02579623, -0.03655198000000001], [-0.02945511, -0.03405986000000001], [-0.032825129999999994, -0.03137517000000001], [-0.035877969999999995, -0.027993820000000003], [-0.03859098, -0.024476540000000005], [-0.04093017, -0.02086297000000001], [-0.04287289, -0.017181440000000006]], 'holes': []}], 'simplify_tolerance': 1.8558336e-05, 'sketch_entity_count': 84}
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
