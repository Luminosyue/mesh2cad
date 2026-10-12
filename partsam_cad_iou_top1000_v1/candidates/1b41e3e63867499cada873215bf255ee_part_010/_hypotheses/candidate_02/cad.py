#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0, -0.132000005, 0.022993185], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.050383335, 'zmax': 0.050383335, 'profiles': [{'outer': [[-0.050120155, -0.12337692], [-0.050352385, -0.12006395], [-0.050352385, 0.12006395], [-0.050120155, 0.12337692], [-0.049593805, 0.12517272], [-0.048866185, 0.12608612], [-0.046869125, 0.12679824], [-0.03774458488980549, 0.1268111444764834], [-0.037658445, 0.13175683], [-0.037513045, 0.13217689], [-0.037028375, 0.13233845], [0.037044935, 0.13233845], [0.037513445, 0.13217689], [0.037658845, 0.13175683], [0.037755775, 0.13012512], [0.03775934789343519, 0.12681114246357547], [0.046869125, 0.12679824], [0.048866185000000006, 0.12608612], [0.049593794999999996, 0.12517272], [0.050135645000000006, 0.12337692], [0.050352375000000005, 0.12006395], [0.050352375000000005, -0.12006395], [0.050135645000000006, -0.12337692], [0.049593794999999996, -0.12517273], [0.048866185000000006, -0.12608612], [0.046869125, -0.12679824], [0.03775934789343519, -0.12681114246357547], [0.037755775, -0.13012512], [0.037658845, -0.13175684], [0.037513445, -0.13217689], [0.037044935, -0.13233845], [-0.037028375, -0.13233845], [-0.037513045, -0.13217689], [-0.037658445, -0.13175684], [-0.03774458488980549, -0.1268111444764834], [-0.046869125, -0.12679824], [-0.048866185, -0.12608612], [-0.049593805, -0.12517273]], 'holes': []}], 'simplify_tolerance': 5.293538e-05, 'sketch_entity_count': 38}
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
