#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.14318817, 0.11560188, 0.16359032499999998], 'basis': [[0.009142912535576673, -0.14725220406610148, 0.9890567200863872], [0.0, 0.989098061713144, 0.14725835906766607], [-0.9999582027016762, -0.001346370297088215, 0.009043237067351695]], 'axis': [0.9890567200863872, 0.14725835906766607, 0.009043237067351695], 'zmin': -0.0556252487984321, 'zmax': 0.05947701140355902, 'profiles': [{'outer': [[-0.0010323768371324998, -0.09096777141201479], [-0.001009079781700597, -0.07707930051503656], [-0.0010090498743836292, 0.07858285706240037], [-0.0009657697035974686, 0.08270914011186865], [0.0003741142905305994, 0.08271094416728454], [0.0004181979404703866, 0.07717763307913242], [0.00041817981744414695, -0.01686195417506654], [0.0009370198251222964, -0.016861255595092505], [0.0016954363076498219, -0.07644741827823644], [0.0017323080500807836, -0.0764473686331426], [0.001762642953866072, -0.07693265691634109], [0.0017911296178822935, -0.07851307939207397], [0.0018295494163645418, -0.09054679711556488], [0.0017626788855123368, -0.09554042530190801], [0.00042164493945115667, -0.09554223090564974], [0.00040204444963528983, -0.09522866840638075], [0.00038964927751422525, -0.09551536426674663], [-0.0009502347166138706, -0.09551716832216252]], 'holes': []}], 'simplify_tolerance': 3.565063501458686e-05, 'sketch_entity_count': 21}
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
