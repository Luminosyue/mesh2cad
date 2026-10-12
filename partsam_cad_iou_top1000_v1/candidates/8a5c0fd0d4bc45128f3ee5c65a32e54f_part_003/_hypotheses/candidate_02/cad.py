#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.003235219999999997, 0.212926775, 0.072162615], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.13800685000000001, 'zmax': 0.13800685000000001, 'profiles': [{'outer': [[-0.135816675, -0.0043045550000000155], [-0.13645689500000002, -0.0037654350000000114], [-0.13699601500000003, -0.0031252250000000092], [-0.13743401500000002, -0.0024175950000000224], [-0.137754155, -0.00164267500000001], [-0.13793946499999998, -0.0008339550000000251], [-0.138006845, -8.43500000000108e-06], [-0.13793946499999998, 0.0008339549999999973], [-0.137754155, 0.0016426149999999862], [-0.13743401500000002, 0.0024007249999999924], [-0.13699601500000003, 0.0031252249999999815], [-0.13645689500000002, 0.0037485649999999815], [-0.135816675, 0.00428769499999998], [-0.13510908500000002, 0.004725724999999986], [-0.134334075, 0.005045864999999983], [-0.13352541499999998, 0.005247984999999983], [-0.132699895, 0.0053153950000000005], [0.132699855, 0.0053153950000000005], [0.133525395, 0.005247984999999983], [0.134334085, 0.005045864999999983], [0.135109065, 0.004725724999999986], [0.135816655, 0.00428769499999998], [0.136456875, 0.0037485649999999815], [0.13699599499999998, 0.0031252249999999815], [0.13743402500000002, 0.0024007249999999924], [0.137754125, 0.0016426149999999862], [0.13793946499999998, 0.0008339549999999973], [0.138006845, -8.43500000000108e-06], [0.13793946499999998, -0.0008339550000000251], [0.137754125, -0.00164267500000001], [0.13743402500000002, -0.0024175950000000224], [0.13699599499999998, -0.0031252250000000092], [0.136456875, -0.0037654350000000114], [0.135816655, -0.0043045550000000155], [0.135109065, -0.004742595000000016], [0.134334085, -0.005062725000000018], [0.133525395, -0.0052479850000000106], [0.132699855, -0.0053153950000000005], [-0.132699895, -0.0053153950000000005], [-0.13352541499999998, -0.0052479850000000106], [-0.134334075, -0.005062725000000018], [-0.13510908500000002, -0.004742595000000016]], 'holes': []}], 'simplify_tolerance': 5.5202737999999996e-05, 'sketch_entity_count': 42}
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
