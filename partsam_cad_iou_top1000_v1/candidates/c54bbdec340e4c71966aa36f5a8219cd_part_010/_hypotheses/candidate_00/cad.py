#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.051889955, 0.31865048, 0.05952239], 'basis': [[0.0, 0.8540848805500655, 0.5201336528391336], [-0.984388181310723, 0.09154929811575657, -0.15032842216387232], [-0.176011103330918, -0.5120134205568178, 0.8407510622496651]], 'axis': [0.5201336528391336, -0.15032842216387232, 0.8407510622496651], 'zmin': -0.00649561254310557, 'zmax': 0.0061709563976827, 'profiles': [{'outer': [[-0.018227842262548654, 0.0040223069948580464], [-0.016993144817733064, 0.009182858017916727], [-0.013130355333160246, 0.0127276979157636], [-0.006771136784916586, 0.013860908558246557], [0.0008994968007018059, 0.012779694816322577], [0.00845378029901658, 0.009896820839228418], [0.014438557787872447, 0.005677439196898491], [0.017710319253028035, 0.0006275610305874659], [0.01822784050243762, -0.004557362129261655], [0.016241156593883345, -0.009154241250131522], [0.01202767849092514, -0.01244348801156505], [0.006019150321177897, -0.01383897415494185], [-0.0008996149272834998, -0.013314725303827393], [-0.007687931913059181, -0.011000955342921406], [-0.013335956176469738, -0.007031723024574772], [-0.01695214909488481, -0.0017309814497551588]], 'holes': []}], 'simplify_tolerance': 7.291136552997255e-06, 'sketch_entity_count': 19}
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
