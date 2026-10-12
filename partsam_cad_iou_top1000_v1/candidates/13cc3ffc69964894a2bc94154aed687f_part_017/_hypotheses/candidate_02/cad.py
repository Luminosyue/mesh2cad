#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.21282769499999998, 0.06508805000000001, 0.19388581], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.02333078000000001, 'zmax': 0.023330779999999995, 'profiles': [{'outer': [[-0.025730749999999997, 0.03932397500000001], [-0.02612415999999998, 0.04058294500000004], [-0.02482582, 0.04502879500000001], [-0.011606389999999994, 0.046799225], [-0.0017310899999999907, 0.04184194499999999], [0.0022425600000000045, 0.038025635], [0.0026360200000000167, 0.03680598500000001], [0.0035016000000000214, 0.03377650500000001], [0.005114649999999998, 0.027835625000000003], [0.01085887000000002, 0.006275325000000026], [0.011685040000000008, 0.002931105000000017], [0.010032650000000004, -0.0019081649999999895], [0.009040020582509183, -0.0037397823776839046], [0.011291629999999997, -0.012176834999999997], [0.016917740000000014, -0.023743884999999992], [0.02045871000000002, -0.027835624999999975], [0.02608480000000002, -0.03834035499999999], [0.026124160000000007, -0.03853708499999997], [0.025652040000000015, -0.038851814999999984], [0.02466848000000002, -0.039363274999999975], [0.02325208000000001, -0.03995345499999997], [0.019239000000000006, -0.04144848499999998], [0.014242420000000006, -0.04310093499999998], [0.011567030000000006, -0.04392714499999997], [0.008970370000000005, -0.044674694999999986], [0.004327830000000005, -0.04593367499999998], [0.0024393300000000173, -0.046366464999999996], [0.0009442199999999956, -0.04664186499999998], [-0.0001179899999999845, -0.04679922499999997], [-0.0006688199999999866, -0.04675990499999999], [-0.0007081699999999802, -0.04656316499999999], [0.0047999400000000025, -0.02756021499999997], [0.0023999700000000013, -0.014970244999999993], [0.0013100905768919928, -0.012313667287707138], [0.0002754100000000037, -0.013121094999999972], [-0.0036983099999999824, -0.01142932499999999], [-0.004406469999999996, -0.010170334999999975], [-0.006098279999999984, -0.006511374999999986], [-0.009599830000000004, 0.0013967050000000258], [-0.014793179999999989, 0.013435855000000024], [-0.02415700999999998, 0.03546831500000003]], 'holes': []}], 'simplify_tolerance': 1.8719689999999996e-05, 'sketch_entity_count': 41}
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
