#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0, -0.132000005, -0.203161795], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.050383335, 'zmax': 0.050383335, 'profiles': [{'outer': [[-0.05035237499999998, -0.12006395], [-0.05035237499999998, 0.12006395], [-0.05012015499999997, 0.12337692], [-0.049593784999999974, 0.12517272], [-0.04886619499999997, 0.12608612], [-0.04686911499999999, 0.12679824], [-0.03774460488971489, 0.1268111445325014], [-0.037658465, 0.13175683], [-0.03751307500000001, 0.13217689], [-0.03702839499999999, 0.13233845], [0.03704491500000001, 0.13233845], [0.03751342500000002, 0.13217689], [0.03765882500000001, 0.13175683], [0.03775574500000001, 0.13012512], [0.03775931899936426, 0.1268111423593003], [0.04686911500000002, 0.12679824], [0.048866185000000006, 0.12608612], [0.049593794999999996, 0.12517272], [0.050135645000000006, 0.12337692], [0.050352385, 0.12006395], [0.050383344999999996, 7.74e-06], [0.050352385, -0.12006395], [0.050135645000000006, -0.12337692], [0.049593794999999996, -0.12517273], [0.048866185000000006, -0.12608612], [0.04686911500000002, -0.12679824], [0.03775931899936426, -0.1268111423593003], [0.03775574500000001, -0.13012512], [0.03765882500000001, -0.13175684], [0.03751342500000002, -0.13217689], [0.03704491500000001, -0.13233845], [-0.03702839499999999, -0.13233845], [-0.03751307500000001, -0.13217689], [-0.037658465, -0.13175684], [-0.03774460488971489, -0.1268111445325014], [-0.04686911499999999, -0.12679824], [-0.04886619499999997, -0.12608612], [-0.049593784999999974, -0.12517273], [-0.05012015499999997, -0.12337692]], 'holes': []}], 'simplify_tolerance': 5.293538e-05, 'sketch_entity_count': 39}
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
