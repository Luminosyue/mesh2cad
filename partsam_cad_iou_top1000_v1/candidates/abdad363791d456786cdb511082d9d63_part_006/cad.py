#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-3.6186573500000003, 3.2531065050000003, 1.4705590000000002], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.5104825499999999, 'zmax': 0.5104825500000003, 'profiles': [{'outer': [[-1.94845617, -2.4075272350000003], [-0.3914847399999999, -0.7338446650000003], [-0.5598293599999997, -0.6205891650000002], [-0.68493855, -0.46085682500000047], [-2.2740782499999996, -2.169816045], [-2.34370339, -1.9792403250000004], [-2.35102975, -1.7764766550000004], [-0.7825909899999997, -0.048258935000000225], [-0.67117512, 0.13591775499999947], [-0.5856338699999997, 0.28913077499999984], [-0.4697660199999998, 0.4550448349999998], [-0.28284489999999973, 0.5280700649999996], [-0.19170511162504394, 0.5167875868944705], [0.797875754487632, 1.5805576277933422], [0.7907453800000002, 1.7779065049999994], [0.8582335700000002, 2.0143423949999995], [0.9954799400000002, 2.218351455], [1.1890529400000003, 2.3699637349999993], [1.4200013900000001, 2.4543386349999996], [1.6657198700000002, 2.463216875], [1.9021552800000001, 2.3957286749999995], [2.1061645700000002, 2.2584815949999997], [2.2577770900000003, 2.064910025], [2.342152, 1.833960625], [2.3510297500000004, 1.5882421449999993], [2.2835420400000004, 1.351806255], [2.14629424, 1.1477971949999994], [1.9527224300000001, 0.9961853949999999], [1.7217735000000003, 0.9118104849999997], [1.535289723501201, 0.9050725061292015], [0.5392798090454987, -0.1656084672373735], [0.5512238700000002, -0.24782934500000042], [0.5232478400000001, -0.42780199500000027], [0.3603469100000001, -0.5908755350000003], [0.20637488000000026, -0.6981128750000005], [0.02472865000000013, -0.7801283850000003], [-1.5505887299999999, -2.455890865], [-1.7533518099999998, -2.4632168750000005]], 'holes': []}], 'simplify_tolerance': 0.0009852867500000002, 'sketch_entity_count': 38}
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
