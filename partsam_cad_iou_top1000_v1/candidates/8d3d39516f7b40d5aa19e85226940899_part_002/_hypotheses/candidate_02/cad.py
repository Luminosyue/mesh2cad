#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.16837752, -0.14012998499999998, 0.32398966500000004], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.032874645000000036, 'zmax': 0.03287464499999998, 'profiles': [{'outer': [[-0.05078852499999999, 0.013043379999999993], [-0.04733916499999999, 0.018938200000000016], [-0.04572838499999998, 0.021035109999999996], [-0.040570624999999985, 0.026783290000000015], [-0.03427391499999999, 0.03149035], [-0.027098604999999984, 0.034994990000000004], [-0.02257538499999999, 0.03715056], [-0.01430994499999999, 0.039438100000000004], [-0.008761694999999986, 0.04020061], [-8.14499999998719e-06, 0.040992450000000014], [0.008761685000000019, 0.04020061], [0.014309945000000018, 0.039438100000000004], [0.022575385000000003, 0.03715056], [0.027098595000000003, 0.034995], [0.034273915000000016, 0.031490359999999995], [0.04057062500000003, 0.026783310000000005], [0.045728375000000016, 0.02103511999999999], [0.04733915500000002, 0.01893821000000001], [0.05078852500000003, 0.01304340000000001], [0.05291996500000001, 0.0066500200000000065], [0.053635865000000005, -7.310000000010364e-06], [0.05291996500000001, -0.0066499899999999945], [0.05078852500000003, -0.013043389999999988], [0.04733915500000002, -0.01893819999999999], [0.045728375000000016, -0.021035109999999996], [0.04057062500000003, -0.026783289999999987], [0.034273915000000016, -0.03149035], [0.027098595000000003, -0.03499498000000001], [0.022575385000000003, -0.03715056], [0.014309945000000018, -0.03943809000000001], [0.008761685000000019, -0.04020061], [-8.14499999998719e-06, -0.040992449999999986], [-0.008761694999999986, -0.04020061], [-0.01430994499999999, -0.039438100000000004], [-0.02257538499999999, -0.037150569999999994], [-0.027098604999999984, -0.034994990000000004], [-0.03427391499999999, -0.031490359999999995], [-0.040570624999999985, -0.02678330000000001], [-0.04572838499999998, -0.02103511999999999], [-0.04733916499999999, -0.01893821000000001], [-0.05078852499999999, -0.01304340000000001], [-0.052919964999999985, -0.006649999999999989], [-0.05363586499999999, -7.329999999999837e-06], [-0.052919964999999985, 0.006649999999999989]], 'holes': []}], 'simplify_tolerance': 2.1454346e-05, 'sketch_entity_count': 47}
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
