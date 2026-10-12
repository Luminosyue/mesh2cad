#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.21196647000000002, -0.163685425, 0.08160827999999999], 'basis': [[0.036901198321816105, -0.2137087816713645, 0.9762002141973516], [0.0, 0.9768655389064423, 0.21385443389611078], [-0.9993189188454374, -0.007891484877200096, 0.0360475089849344]], 'axis': [0.9762002141973516, 0.21385443389611078, 0.0360475089849344], 'zmin': -0.05676291899835875, 'zmax': 0.055732937320264714, 'profiles': [{'outer': [[-0.047606820587282335, 0.036750745587477734], [-0.0470561565511333, 0.04826582270607246], [-0.04633550566886689, 0.05204647673550026], [0.04540866651790052, 0.0527709679201759], [0.046187974437983344, 0.04825770131307814], [0.0469074282453762, 0.03613685691849493], [0.0474724582870439, 0.018128674571578216], [0.0469603909302605, 0.010788580357553335], [0.04666673711155769, -0.002624472057636064], [0.04423046902561452, -0.015162488177088257], [0.04161584456262823, -0.020931646022910914], [0.03305219466880775, -0.03607685075106792], [0.021756724864775603, -0.03744952416117556], [0.016879403901099915, -0.04483002357081774], [-0.042857841905732726, -0.045301760433795225], [-0.0445817625651792, -0.045511258585834255], [-0.04458336282553887, -0.0453153866365891], [-0.046790402239083206, -0.04533281532509576], [-0.047606820587282335, -0.02250962032297951], [-0.04790489776597845, -0.0015474829187072134], [-0.04790489776597845, 0.019241163308794627]], 'holes': []}], 'simplify_tolerance': 1.965644530120203e-05, 'sketch_entity_count': 21}
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
