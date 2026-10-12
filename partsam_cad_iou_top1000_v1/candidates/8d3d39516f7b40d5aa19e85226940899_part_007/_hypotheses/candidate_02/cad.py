#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.082298765, -0.20960042, -0.36924945000000003], 'basis': [[0.0, 0.9997102772325486, -0.024069931358877694], [-0.7819841123539517, 0.01500274878855501, 0.6231177782368191], [0.6232983619631951, 0.01882230390809252, 0.7817575537528175]], 'axis': [-0.024069931358877694, 0.6231177782368191, 0.7817575537528175], 'zmin': -0.17673296390511883, 'zmax': 0.1609393956771834, 'profiles': [{'outer': [[-0.020155789479154692, 0.026971321528417715], [-0.01861083980984024, 0.028776993820871708], [-0.010482103909352423, 0.03486212557898957], [-0.0011621903344490618, 0.03704794738322628], [0.008627788749136885, 0.036626908554155145], [0.017819347263937486, 0.03466058767651964], [0.02131643793457352, 0.03474712764791641], [0.03031263502888977, 0.032803273601125255], [0.03833692335766489, 0.027003987051534256], [0.03863084996091441, 0.026731492936160083], [0.044463676256240224, 0.01794816712246896], [0.04760904681404441, 0.007119579830133014], [0.04464563036567715, -0.015279782035496216], [0.044456145101156766, -0.015661745949928228], [0.038585952441220595, -0.024707331831868472], [0.030666849249718596, -0.030625866460074522], [0.0217183766457793, -0.03275252863339466], [0.01776693274684037, -0.03224556523206045], [0.00903940899242041, -0.033294611660887465], [-0.0007982915222738916, -0.03254267198102475], [-0.01008017766411386, -0.030547716721035106], [-0.018314054956543105, -0.024585063150916412], [-0.019868720496568393, -0.022374033968983905], [-0.025548652803926382, -0.013870489736923765], [-0.028626940567770626, -0.0033769018399757277], [-0.028646311337320835, 0.007791191792118256], [-0.025720906682334697, 0.018310497596256903]], 'holes': []}], 'simplify_tolerance': 1.525107163027305e-05, 'sketch_entity_count': 27}
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
