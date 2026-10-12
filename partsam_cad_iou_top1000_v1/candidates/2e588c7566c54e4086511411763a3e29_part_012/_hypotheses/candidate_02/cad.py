#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.11559052, 0.150696425, 0.02161631], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.09883553, 'zmax': 0.09883553, 'profiles': [{'outer': [[-0.10475933499999998, 1.8199999999995997e-06], [-0.10453015499999999, 0.0036978599999999973], [-0.10387534499999998, 0.007226589999999991], [-0.102878575, 0.010464260000000003], [-0.10163808500000002, 0.013327249999999985], [-0.10026663500000002, 0.015793699999999994], [-0.09884786500000001, 0.01787820000000001], [-0.097447275, 0.019624360000000007], [-0.09610492500000001, 0.021072220000000003], [-0.09466797500000002, 0.022425499999999987], [-0.09293997500000001, 0.02384063], [-0.090870055, 0.02527030999999999], [-0.088425425, 0.026652690000000007], [-0.085584255, 0.02790047000000001], [-0.08237567500000001, 0.02890815999999999], [-0.07887607500000002, 0.029570230000000003], [-0.075209145, 0.029799419999999993], [-0.07154581500000001, 0.029570239999999998], [-0.068042575, 0.02890814], [-0.064834005, 0.02790047000000001], [-0.06199649500000001, 0.026652690000000007], [-0.059551835, 0.02527029], [-0.057481914999999995, 0.023840609999999984], [-0.055753915000000015, 0.022425499999999987], [-0.054316964999999995, 0.021072220000000003], [-0.052974615, 0.019624360000000007], [-0.051570384999999996, 0.01787820000000001], [-0.050155284999999994, 0.015793699999999994], [-0.04878381500000001, 0.013327249999999985], [-0.04754328500000002, 0.010464260000000003], [-0.046872378899829516, 0.008285020000000004], [0.10428089499999998, 0.008285020000000004], [0.10428090313325698, -0.0027091017187838495], [0.104590765, -0.004203369999999998], [0.10472282499999999, -0.005347009999999999], [0.104759335, -0.006493689999999996], [0.104722805, -0.007657419999999998], [0.104563935, -0.008791920000000009], [0.1042808985377533, -0.010089551714764583], [0.10428089499999998, -0.021095799999999998], [-0.05080670500000001, -0.021095799999999998], [-0.0508067328015778, -0.016753323470867505], [-0.05157041500000001, -0.017878199999999997], [-0.052974615, -0.019624370000000002], [-0.054316964999999995, -0.021072229999999997], [-0.055753915000000015, -0.022425509999999996], [-0.057481914999999995, -0.023840639999999996], [-0.059551835, -0.025270310000000004], [-0.061996465, -0.026652690000000007], [-0.064834005, -0.027900460000000002], [-0.06804254500000001, -0.028908150000000007], [-0.07154581500000001, -0.029570239999999998], [-0.07520911499999999, -0.029799420000000007], [-0.07887607500000002, -0.029570239999999998], [-0.08237567500000001, -0.028908160000000002], [-0.085584255, -0.027900460000000002], [-0.088425425, -0.026652690000000007], [-0.090870055, -0.025270310000000004], [-0.09293997500000001, -0.02384063], [-0.094667945, -0.022425509999999996], [-0.09610492500000001, -0.021072229999999997], [-0.097447275, -0.019624370000000002], [-0.098847835, -0.017878199999999997], [-0.10026660499999998, -0.015793710000000002], [-0.10163808500000002, -0.013327260000000007], [-0.102878575, -0.010464269999999998], [-0.10387537500000002, -0.007226590000000005], [-0.10453015499999999, -0.003697870000000006]], 'holes': []}], 'simplify_tolerance': 4.1903733999999996e-05, 'sketch_entity_count': 68}
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
