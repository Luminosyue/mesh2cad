#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.0005056549999999937, 0.15419539499999999, 0.04360965], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.37661043, 'zmax': 0.37661043, 'profiles': [{'outer': [[-0.10080346500000001, 0.034064054999999996], [-0.031967435000000016, 0.097290825], [0.06115743499999998, 0.192920635], [0.07166799499999998, 0.192920635], [0.08062349625534745, 0.18378805809894383], [0.104234365, 0.20354013499999998], [0.16996615499999998, 0.267311485], [0.227964905, 0.338434725], [0.30486088499999997, 0.444684115], [0.31493580499999996, 0.446099965], [0.337754065, 0.42861863499999997], [0.339224395, 0.418325985], [0.261620545, 0.311150875], [0.20138901499999998, 0.237359095], [0.13320648499999999, 0.171137045], [0.10897227499999998, 0.152185395], [0.07686361089859865, 0.14817371727591194], [-0.002995165000000022, 0.066140355], [-0.074499695, 0.0005173949999999937], [-0.152648125, -0.05655555500000001], [-0.26074913499999997, -0.126589685], [-0.152648125, -0.196623805], [-0.074499695, -0.253696745], [-0.002995165000000022, -0.319319695], [0.09100076499999998, -0.415875285], [0.09094646499999999, -0.426440325], [0.07166799499999998, -0.446099965], [0.06110283499999998, -0.446045545], [-0.031967435000000016, -0.350470185], [-0.10080346500000001, -0.287243395], [-0.176120015, -0.23223991500000002], [-0.339278905, -0.126589685], [-0.176120015, -0.020939425000000005]], 'holes': []}, {'outer': [[0.244193585, -0.402750705], [0.08969375499999999, -0.402750705], [0.08560934499999999, -0.39741376500000003], [0.08560934499999999, 0.143580895], [0.08969375499999999, 0.148917835], [0.244193585, 0.148917835], [0.244901535, 0.143580895], [0.244901535, -0.39741376500000003]], 'holes': []}], 'simplify_tolerance': 0.000178439986, 'sketch_entity_count': 44}
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
