#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.047981325, -0.473509135, 0.051639569999999996], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.035646695, 'zmax': 0.035646695, 'profiles': [{'outer': [[-0.08313495000000001, -0.026490864999999975], [-0.10889335, -0.023255824999999952], [-0.1132271, -0.01348960499999996], [-0.10486477999999999, -0.0008545449999999843], [-0.09253493000000002, 0.010925955000000043], [-0.07837393000000001, 0.02014282500000003], [-0.06305315, 0.025025935], [-0.04687786000000001, 0.02649086500000003], [-0.04590123, 0.02649086500000003], [-0.03100775, 0.02563631500000002], [-0.013001289999999999, 0.02349996500000001], [0.00752418032206903, 0.021550306482310995], [0.013681603053422435, 0.02103576803392203], [0.03308306999999999, 0.019715545], [0.036806439999999996, 0.018616855000000043], [0.04815965999999999, 0.017762305000000034], [0.061649249999999996, 0.017640235000000004], [0.08398948, 0.017640235000000004], [0.08710245999999999, 0.017762305000000034], [0.08972712999999999, 0.01806748500000005], [0.09229076, 0.017457095000000034], [0.09498029382810112, 0.016541515000000007], [0.10492581, 0.016541515000000007], [0.10938165, 0.009216845000000029], [0.1132271, -0.0012818249999999587], [0.11218944, -0.01348960499999996], [0.1055362, -0.023255824999999952], [0.09241284, -0.026490864999999975]], 'holes': []}], 'simplify_tolerance': 4.529084e-05, 'sketch_entity_count': 37}
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
