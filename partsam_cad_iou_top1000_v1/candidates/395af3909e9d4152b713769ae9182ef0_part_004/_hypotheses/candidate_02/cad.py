#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.18470715, -0.067604345, -0.05565933], 'basis': [[0.0, 0.876373737169615, -0.4816316775289626], [-0.9998116314985147, 0.009347892938039691, 0.01700936265405562], [0.019408800073117204, 0.4815409532915986, 0.8762086559620033]], 'axis': [-0.4816316775289626, 0.01700936265405562, 0.8762086559620033], 'zmin': -0.07169460204485165, 'zmax': 0.06821390926610633, 'profiles': [{'outer': [[-0.1310575873854321, 0.011858316401310782], [-0.13138216461696045, 0.013328672415535711], [-0.13076100841895688, 0.016667128020115298], [-0.13056045792900503, 0.01733558866052056], [-0.12594951318457398, 0.020525289035740066], [-0.11809198477059259, 0.023790958123243736], [-0.06465864024857955, 0.043796748304994214], [-0.02768849943445746, 0.059021069628151804], [0.014960505012529175, 0.06973403746683846], [0.10587781371689266, 0.06835110495556943], [0.11272319546141696, 0.0676048599023662], [0.12236737012857926, 0.06415949497980158], [0.1320173104180972, 0.057922105500076225], [0.13220560877376655, 0.05661392640731108], [0.13248772480496535, 0.04732278087316405], [0.1326102121895228, 0.030430090198329245], [0.13255442993949665, 0.008520207942958035], [0.13232911744938383, -0.015076036359691371], [0.13196818635693613, -0.036763643517713426], [0.13173752899695781, -0.04582003712984883], [0.13123287931410196, -0.05865902960859154], [0.13099243011485848, -0.06195361400086771], [0.13076627792555312, -0.06295223928938187], [0.12061696785821505, -0.06865067897692856], [0.11061016304185345, -0.07119268656664107], [0.10465895865804893, -0.07077637121805719], [0.04628789748234845, -0.03924467071242277], [0.03412355447118443, -0.03216133633697352], [0.008098771070568788, -0.03213138757466745], [-0.07869301398280137, -0.04401895787836136], [-0.08179769381861919, -0.04418566581515043], [-0.0910547984636142, -0.04171978285085399], [-0.09831572216366105, -0.03884657615261464], [-0.1033166646030369, -0.03504951282474693], [-0.10532029107044055, -0.033384556016283456], [-0.10784923354981196, -0.030654359871068182], [-0.11055665587839213, -0.027124901994667223], [-0.11316071148323546, -0.023190459333738825], [-0.11563481869394254, -0.019158279463768087], [-0.11821809705960032, -0.014804175747194788], [-0.12330176763598198, -0.00564326611979453], [-0.1256128514597187, -0.0012004037288643578], [-0.1275735590803182, 0.002918821147131752], [-0.12915138041973584, 0.006556580816988967], [-0.13032914229790893, 0.009580597654213333]], 'holes': []}], 'simplify_tolerance': 5.279847536129665e-05, 'sketch_entity_count': 48}
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
