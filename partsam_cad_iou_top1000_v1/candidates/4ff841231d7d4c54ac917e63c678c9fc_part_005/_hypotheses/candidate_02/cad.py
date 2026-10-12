#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.005181539999999999, -0.032377645, 0.05782457], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.0197435, 'zmax': 0.0197435, 'profiles': [{'outer': [[0.0006434899999999966, -0.127747875], [-0.001989730000000002, -0.127139675], [-0.00219184245802984, -0.056878764540794706], [-0.03385609, -0.03990228500000001], [-0.05021856, 0.005837454999999995], [-0.024721509999999995, 0.05228482499999999], [-0.000336973659456563, 0.06145484315091448], [0.0017899200000000004, 0.127389175], [0.005251689999999996, 0.127747875], [0.008202689999999999, 0.12682776499999998], [0.006166721533841453, 0.06354853736458786], [0.03776126, 0.044358234999999996], [0.050218559999999995, 0.005011904999999997], [0.03228663, -0.041266935000000005], [0.004108017121098549, -0.057667950820411734], [0.004309549999999995, -0.12740479500000002]], 'holes': [[[-0.021386499999999996, -0.024638875000000005], [-0.0022563975953839585, -0.03443728433946141], [-0.0023613619071452866, 0.0020517484592294474], [-0.030843888096623157, 0.00097200560168668]], [[-0.028561529854687625, 0.00992057711108181], [-0.0019662279767759124, 0.010947477939182732], [-0.0009990243238819309, 0.04093107694612776], [-0.013901069999999995, 0.036406444999999996]], [[0.004477974573510854, 0.011061180562349174], [0.030211149763101856, 0.011515221151332198], [0.02370386, 0.031293314999999995], [0.005467292156054631, 0.0418098161871547]], [[0.019136559999999997, -0.025784475], [0.03033521761667775, 0.0026465379880335304], [0.003935029999999999, 0.002191144999999995], [0.004040692495311035, -0.034371469553506936]]]}], 'simplify_tolerance': 5.1099150000000004e-05, 'sketch_entity_count': 35}
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
