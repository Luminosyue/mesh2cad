#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.10984100000000001, -0.382072685, 0.011379405000000002], 'basis': [[0.2148070672382176, 0.002635361170915534, 0.9766529469243488], [0.0, 0.9999963594467428, -0.0026983500997381144], [-0.9766565024943601, 0.0005796246713066963, 0.2148062852216493]], 'axis': [0.9766529469243488, -0.0026983500997381144, 0.2148062852216493], 'zmin': -0.05447640485407169, 'zmax': 0.05314366052597197, 'profiles': [{'outer': [[-0.029984223738864894, -0.046816507866405586], [-0.00745770674250759, -0.034207577337335815], [-0.02941987954239949, 0.022450794995576083], [-0.05229929300097847, 0.041791770429148015], [-0.06488303852539964, 0.0949417803596227], [-0.03447876835940354, 0.10082881871519425], [0.026155096159953196, 0.11232815028828227], [0.05639931653157985, 0.11792545482484945], [0.06898306205600105, 0.06477547489426552], [0.06657462003074922, 0.040636863743568306], [0.10239065164669965, -0.036037158711367756], [0.10239065164669965, -0.11792852058041818], [0.07833194624548867, -0.1180430686959953], [-0.02417686848558659, -0.11806934509421943], [-0.07866071822149592, -0.11804243654657377], [-0.10259032985219228, -0.11792770053092394], [-0.08553936057077424, -0.07182450188560068]], 'holes': []}], 'simplify_tolerance': 4.719895998381378e-05, 'sketch_entity_count': 23}
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
