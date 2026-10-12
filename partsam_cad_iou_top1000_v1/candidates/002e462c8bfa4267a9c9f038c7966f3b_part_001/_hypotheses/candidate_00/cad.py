#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.39356738, 0.223561995, -0.10597996999999999], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.04224098500000001, 'zmax': 0.04224098500000001, 'profiles': [{'outer': [[-0.08137909, 0.033712149999999996], [-0.07630266000000001, 0.04404786000000005], [-0.06989256, 0.05361998000000001], [-0.062288650000000015, 0.062288670000000046], [-0.05361996000000001, 0.06989258000000004], [-0.04404784000000002, 0.07630267000000002], [-0.03371213000000002, 0.08137911000000003], [-0.022795600000000013, 0.08507889000000002], [-0.011491910000000008, 0.08733749000000002], [5.389999999994011e-06, 0.08810112000000003], [0.011491919999999989, 0.08733749000000002], [0.02279561999999999, 0.08507889000000002], [0.03371213999999999, 0.08137911000000003], [0.044047869999999996, 0.07630267000000002], [0.05361998999999999, 0.06989258000000004], [0.062288659999999996, 0.062288670000000046], [0.06989256999999999, 0.05361998000000001], [0.07630266999999999, 0.04404786000000005], [0.08137910999999999, 0.033712149999999996], [0.08507889999999999, 0.02279561000000002], [0.08733748, 0.011491920000000044], [0.08810109999999999, -5.370000000004538e-06], [0.08733748, -0.011491929999999984], [0.08507889999999999, -0.02279561999999996], [0.08137910999999999, -0.03371211999999996], [0.07630266999999999, -0.04404786999999999], [0.06989256999999999, -0.053619979999999956], [0.062288659999999996, -0.062288679999999985], [0.05361998999999999, -0.06989258999999998], [0.044047869999999996, -0.07630267999999996], [0.03371213999999999, -0.08137911999999997], [0.02279561999999999, -0.08507889999999996], [0.011491919999999989, -0.08733749999999996], [5.389999999994011e-06, -0.08810111999999998], [-0.011491910000000008, -0.08733749999999996], [-0.022795600000000013, -0.08507889999999996], [-0.03371213000000002, -0.08137911999999997], [-0.04404784000000002, -0.07630267999999996], [-0.05361996000000001, -0.06989258999999998], [-0.062288650000000015, -0.062288679999999985], [-0.06989256, -0.053619979999999956], [-0.07630266000000001, -0.04404786999999999], [-0.08137909, -0.03371211999999996], [-0.08507887000000001, -0.02279561999999996], [-0.08733747000000001, -0.011491929999999984], [-0.0881011, 5.390000000049522e-06], [-0.08733747000000001, 0.011491920000000044], [-0.08507887000000001, 0.02279561000000002]], 'holes': []}], 'simplify_tolerance': 3.524044800000001e-05, 'sketch_entity_count': 69}
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
    elif kind == "loft":
        wires = [cq.Wire.makePolygon([vec(p) for p in section], close=True) for section in s["sections"]]
        result = cq.Solid.makeLoft(wires, ruled=bool(s.get("ruled", True)))
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
