#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0005719200000000035, -0.107112335, 0.026705265000000006], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.284087015, 'zmax': 0.284087015, 'profiles': [{'outer': [[-0.320207715, -0.025192480000000003], [-0.32118794500000003, 1.9489999999996468e-05], [-0.320207715, 0.025192259999999998], [-0.31722778500000004, 0.050247389999999996], [-0.312326525, 0.07498884], [-0.30546480499999995, 0.09925977999999999], [-0.29672101500000003, 0.12290336], [-0.28617355499999997, 0.14580196], [-0.273861645, 0.16783793], [-0.259863705, 0.18877602999999998], [-0.244218965, 0.20857704999999999], [-0.227123465, 0.22712334], [-0.208577185, 0.24421886], [-0.188776185, 0.25986363], [-0.167838095, 0.27386157], [-0.145802145, 0.28617348], [-0.12290355500000001, 0.29672094], [-0.099259975, 0.30546479], [-0.07498906500000001, 0.31232651], [-0.050247605, 0.31722774], [-0.025192485000000008, 0.32020776], [-1.9725000000005155e-05, 0.32118799], [0.025192254999999997, 0.32020776], [0.050247375, 0.3172278], [0.074988825, 0.31232656999999997], [0.09925979499999998, 0.30546485], [0.122903335, 0.29672106], [0.145801945, 0.2861736], [0.167837885, 0.27386169], [0.188776005, 0.25986375], [0.20857700499999998, 0.24421901], [0.22712329499999998, 0.22712352], [0.244218825, 0.20857723], [0.259863615, 0.18877621], [0.27386152499999994, 0.16783814], [0.286173405, 0.14580217], [0.29672086499999994, 0.12290359], [0.30546471499999994, 0.09926], [0.31232646499999994, 0.07498908], [0.31722772499999996, 0.050247629999999995], [0.320207715, 0.025192499999999996], [0.32118794500000003, 1.9729999999996452e-05], [0.320207715, -0.025192250000000003], [0.31722778500000004, -0.050247370000000006], [0.312326525, -0.07498883], [0.305464775, -0.09925979], [0.296720985, -0.12290335000000001], [0.28617352500000004, -0.14580196], [0.273861645, -0.1678379], [0.25986373500000004, -0.18877601], [0.244218945, -0.20857704], [0.227123465, -0.22712332], [0.208577185, -0.24421884], [0.18877618499999999, -0.25986366], [0.167838095, -0.27386157], [0.145802155, -0.28617345], [0.122903555, -0.29672091], [0.09926000499999998, -0.30546476], [0.074989065, -0.31232653], [0.050247605, -0.31722776], [0.025192494999999995, -0.32020776], [-1.948500000000658e-05, -0.32118799], [-0.025192255000000007, -0.32020776], [-0.05024737500000001, -0.31722782], [-0.07498882500000001, -0.31232659], [-0.099259755, -0.30546482], [-0.122903335, -0.29672102], [-0.145801935, -0.28617357], [-0.167837885, -0.27386169], [-0.188776005, -0.25986378], [-0.208577005, -0.24421899], [-0.227123295, -0.2271235], [-0.244218815, -0.20857721], [-0.259863585, -0.18877619], [-0.273861525, -0.16783811], [-0.28617343500000003, -0.14580217], [-0.296720895, -0.12290357], [-0.305464745, -0.09926002], [-0.31232646500000005, -0.07498906000000001], [-0.31722772499999996, -0.050247610000000005]], 'holes': []}], 'simplify_tolerance': 0.000128475196, 'sketch_entity_count': 92}
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
