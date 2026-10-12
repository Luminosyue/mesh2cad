#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.0007043950000000104, 0.3715917, -0.03389645000000001], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.14028933, 'zmax': 0.14028933, 'profiles': [{'outer': [[-0.12035660999999998, -0.04490952499999999], [-0.12462673999999996, -0.031014354999999987], [-0.12742604999999996, -0.015870164999999988], [-0.12840657, 7.80500000001046e-06], [-0.12742604999999996, 0.015870165000000012], [-0.12462673999999996, 0.03101434500000001], [-0.12035660999999998, 0.04490952500000001], [-0.11955000999999998, 0.04694503500000001], [-0.11434675999999999, 0.05908176500000001], [-0.10857416999999997, 0.069535335], [-0.10259596999999998, 0.07836269500000001], [-0.09668104999999999, 0.08573805500000001], [-0.09100334999999998, 0.09185387500000002], [-0.08483533999999998, 0.09771289500000001], [-0.07741795999999995, 0.10381114500000001], [-0.06856135999999996, 0.10997186500000002], [-0.05810744999999995, 0.11592710500000002], [-0.04599289999999995, 0.12127642500000001], [-0.03232843999999996, 0.125606345], [-0.017446209999999962, 0.12842531499999998], [-0.001868089999999989, 0.129410965], [0.01371, 0.12842531499999998], [0.028592240000000047, 0.125606345], [0.04225667000000005, 0.12127642500000001], [0.05437122, 0.11592710500000002], [0.06482516000000005, 0.10997186500000002], [0.07368175000000005, 0.10381114500000001], [0.08109914000000001, 0.09771289500000001], [0.08726711000000004, 0.09185387500000002], [0.09294481000000004, 0.08573805500000001], [0.09885977000000001, 0.07836269500000001], [0.10483797, 0.069535335], [0.11061056000000002, 0.05908176500000001], [0.11581380000000002, 0.04694503500000001], [0.11662037000000003, 0.04490952500000001], [0.12089051, 0.03101434500000001], [0.12116795904929815, 0.02951336500000001], [0.12840657000000003, 0.02951336500000001], [0.12840657000000003, -0.03476097499999999], [0.11973913208042077, -0.03476097499999999], [0.11662037000000003, -0.04490952499999999], [0.11581380000000002, -0.04694504499999999], [0.11061056000000002, -0.05908178499999999], [0.10483797, -0.069535355], [0.09885977000000001, -0.07836270499999999], [0.09294481000000004, -0.08573808499999999], [0.08726711000000004, -0.09185641499999998], [0.08109914000000001, -0.09771291499999998], [0.07368175000000005, -0.10381117499999999], [0.06482516000000005, -0.10997188499999999], [0.05437122, -0.11592711499999998], [0.04225667000000005, -0.121276425], [0.028592240000000047, -0.125606355], [0.01371, -0.12842531499999998], [-0.001868089999999989, -0.129410965], [-0.017446209999999962, -0.12842531499999998], [-0.03232843999999996, -0.125606355], [-0.04599289999999995, -0.121276425], [-0.05810744999999995, -0.11592711499999998], [-0.06856135999999996, -0.10997188499999999], [-0.07741795999999995, -0.10381117499999999], [-0.08483533999999998, -0.09771291499999998], [-0.09100334999999998, -0.09185641499999998], [-0.09668104999999999, -0.08573808499999999], [-0.10259596999999998, -0.07836270499999999], [-0.10857416999999997, -0.069535355], [-0.11434675999999999, -0.05908178499999999], [-0.11955000999999998, -0.04694504499999999]], 'holes': []}], 'simplify_tolerance': 5.1764386e-05, 'sketch_entity_count': 71}
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
