#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.295243915, -0.103737505, 0.11132804], 'basis': [[0.0, 0.9977043523935112, 0.06772019798438697], [-0.12698319080155723, -0.06717199411404239, 0.9896278050159052], [0.9919048690544146, -0.008599326821770642, 0.12669168214352933]], 'axis': [0.06772019798438697, 0.9896278050159052, 0.12669168214352933], 'zmin': -0.132683812161936, 'zmax': 0.12850367552118733, 'profiles': [{'outer': [[-0.07799710095337989, 0.127841323373957], [-0.014477533563559618, 0.16351275831723186], [0.07093944000720477, 0.14566035326261936], [0.13096135106163392, 0.09286221552854612], [0.15443608604072537, 0.015285538479235573], [0.13911923800004725, -0.06644398334216449], [0.08802685404683266, -0.12969464460170643], [0.08374908191978998, -0.13182778146340104], [0.07647995006877191, -0.13432042516832812], [0.01607091830901796, -0.15852075849522151], [-0.06138481844758459, -0.14395363966330274], [-0.06535079720422285, -0.143008613129971], [-0.13486254532478778, -0.08701906703115758], [-0.14808881336715227, -0.019578045133266515], [-0.1281928431057472, 0.05539664607503696], [-0.08420055548271921, 0.12017205645729333]], 'holes': []}], 'simplify_tolerance': 6.440670336249068e-05, 'sketch_entity_count': 22}
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
