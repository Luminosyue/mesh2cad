#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0, -0.13199999, 0.41068737499999997], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.05038334499999997, 'zmax': 0.050383345000000024, 'profiles': [{'outer': [[-0.04886619000000002, -0.12608612], [-0.04959380000000001, -0.12517273], [-0.050120150000000016, -0.12337692], [-0.050352380000000016, -0.12006395], [-0.050352380000000016, 0.12006395], [-0.050120150000000016, 0.12337692], [-0.04959380000000001, 0.12517272], [-0.04886619000000002, 0.12608612], [-0.046869120000000014, 0.12679824], [-0.03772137932334694, 0.12681372], [-0.03771443000000001, 0.12847298], [-0.03763317000000001, 0.12889554], [-0.03732440000000001, 0.12904179], [-0.026663700000000012, 0.12922055], [-0.026549930000000013, 0.12938307], [-0.02638742000000001, 0.13276328], [-0.026306170000000018, 0.13292579], [-0.025997400000000018, 0.13307205], [0.026006069999999992, 0.13307205], [0.026298589999999983, 0.13292579], [0.02639611, 0.13276328], [0.026558619999999977, 0.12938307], [0.02667237, 0.12922055], [0.03733307999999999, 0.12904179], [0.03764184999999998, 0.12889554], [0.03772309999999998, 0.12847298], [0.03773004932334691, 0.12681372], [0.046869119999999986, 0.12679824], [0.048866189999999976, 0.12608612], [0.04959379999999999, 0.12517272], [0.050135649999999976, 0.12337692], [0.05035236999999998, 0.12006395], [0.05035236999999998, -0.12006395], [0.050135649999999976, -0.12337692], [0.04959379999999999, -0.12517273], [0.048866189999999976, -0.12608612], [0.046869119999999986, -0.12679824], [0.037729988515067196, -0.12681372], [0.03772309999999998, -0.12845674], [0.03764184999999998, -0.12889554], [0.03733307999999999, -0.12904179], [0.02667237, -0.12922055], [0.026558619999999977, -0.12938306], [0.02639611, -0.13276328], [0.026298589999999983, -0.13292579], [0.026006069999999992, -0.13307205], [-0.025997400000000018, -0.13307205], [-0.026306170000000018, -0.13292579], [-0.02638742000000001, -0.13276328], [-0.026549930000000013, -0.12938306], [-0.026663700000000012, -0.12922055], [-0.03732440000000001, -0.12904179], [-0.03763317000000001, -0.12889554], [-0.03771443000000001, -0.12845674], [-0.03772131851506722, -0.12681372], [-0.046869120000000014, -0.12679824]], 'holes': []}], 'simplify_tolerance': 5.3248324e-05, 'sketch_entity_count': 59}
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
